"""Streamable HTTP MCP 服务，暴露 `ocr_extract_text` 工具。

为 xskills 平台而建：平台「新增 MCP 服务器」只接公网 URL + streamableHTTP，
故本服务以 streamable-http 传输公网部署，注册时把 URL 填进「连接地址」，
可选 Bearer Token 填进「请求头」（Authorization=Bearer <token>）。

鉴权用一个轻量 ASGI 中间件实现：仅当环境变量 AUTH_TOKEN 非空时启用；
未设置则开放访问（便于本地冒烟测试）。
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from src.core import ImageLoadError, load_pages, run_ocr

# ---- MCP 实例 -------------------------------------------------------------

mcp = FastMCP(
    name="lab-ocr-mcp",
    instructions=(
        "检验报告 OCR 服务：把化验单图片/PDF 识别为文本，并把表格还原成 "
        "Markdown 表格，供下游 skill 做项目归一/LOINC/单位换算/异常判定。"
        "本服务只负责'图→文'，不做任何标准化。"
    ),
)


@mcp.tool(
    name="ocr_extract_text",
    description=(
        "对检验报告（化验单）图片或 PDF 做 OCR，返回还原后的 Markdown 表格与纯文本。"
        "传入 image_url（公网图片/PDF 链接）或 image_base64（base64 编码的图片/PDF）"
        "之一。仅做图像到文本的转换，不做医学标准化、不给诊疗结论。"
    ),
)
def ocr_extract_text(
    image_url: str | None = Field(
        default=None,
        description="公网可访问的图片或 PDF 的 http(s) 链接。与 image_base64 二选一。",
    ),
    image_base64: str | None = Field(
        default=None,
        description="base64 编码的图片或 PDF（可带 data URI 前缀）。与 image_url 二选一。",
    ),
) -> dict:
    """返回结构：
    {
      "markdown": "...",          # 还原后的 Markdown（表格优先）
      "plain_text": "...",        # 纯文本（保留行结构）
      "engine": "rapidocr-onnxruntime",
      "page_count": 1,
      "mean_confidence": 0.97,
      "warnings": [...],          # 加载/识别过程中的质控提示
      "ocr_source": "lab-ocr-mcp" # 供 skill 写入 metadata.ocr_source
    }
    """
    try:
        pages = load_pages(image_url=image_url, image_base64=image_base64)
    except ImageLoadError as exc:
        return {
            "markdown": "",
            "plain_text": "",
            "engine": "rapidocr-onnxruntime",
            "page_count": 0,
            "mean_confidence": 0.0,
            "warnings": [f"图片加载失败：{exc}"],
            "ocr_source": "lab-ocr-mcp",
        }

    result = run_ocr(pages)
    return {
        "markdown": result.markdown,
        "plain_text": result.plain_text,
        "engine": result.engine,
        "page_count": len(result.pages),
        "mean_confidence": result.mean_confidence,
        "warnings": result.warnings,
        "ocr_source": "lab-ocr-mcp",
    }


# ---- 可选 Bearer 鉴权中间件 ----------------------------------------------


class BearerAuthMiddleware:
    """仅当配置了 AUTH_TOKEN 时校验 `Authorization: Bearer <token>`。"""

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        auth = request.headers.get("authorization", "")
        expected = f"Bearer {self.token}"
        if auth != expected:
            response = JSONResponse({"error": "unauthorized"}, status_code=401)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def build_app():
    """构造可部署的 ASGI 应用（streamable-http），按需套上鉴权中间件。"""
    app = mcp.streamable_http_app()
    token = os.environ.get("AUTH_TOKEN", "").strip()
    if token:
        app.add_middleware(BearerAuthMiddleware, token=token)
    return app


# uvicorn 入口：`uvicorn src.server.app:app --host 0.0.0.0 --port 8000`
app = build_app()


def main() -> None:
    """本地直接运行：python -m src.server.app"""
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
