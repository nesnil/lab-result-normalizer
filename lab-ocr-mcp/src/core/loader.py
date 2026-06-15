"""图片加载层：把三种输入（公网 URL / base64 / PDF）统一成一批 PIL 图像。

只负责"拿到像素"，不做任何 OCR、不做任何标准化。
PDF 会被逐页栅格化成图像（多页化验单逐页 OCR 后由上层合并）。
"""

from __future__ import annotations

import base64
import binascii
import io
from dataclasses import dataclass

import httpx
from PIL import Image

# 下载与解码的安全上限，避免被超大文件拖垮服务
MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_PDF_PAGES = 20  # 单份化验单 PDF 的页数上限
PDF_RENDER_DPI = 200  # PDF 栅格化分辨率，200 DPI 对化验单文字足够清晰


class ImageLoadError(Exception):
    """加载/解码图片失败。携带人类可读原因，供上层写入 warnings。"""


@dataclass
class LoadedPage:
    """一页待 OCR 的图像及其来源信息。"""

    image: Image.Image
    page_index: int  # 0-based；单图恒为 0，PDF 为页码
    source_kind: str  # "image_url" | "base64" | "pdf"


def load_pages(
    *,
    image_url: str | None = None,
    image_base64: str | None = None,
) -> list[LoadedPage]:
    """根据传入的一种输入，返回一批 LoadedPage。

    恰好接受一种输入；URL 或 base64 都可能指向 PDF，会自动识别并分页。
    """
    provided = [v for v in (image_url, image_base64) if v]
    if len(provided) != 1:
        raise ImageLoadError(
            "必须且只能提供一种输入：image_url 或 image_base64。"
        )

    if image_url:
        raw = _fetch_url(image_url)
        kind = "image_url"
    else:
        raw = _decode_base64(image_base64)  # type: ignore[arg-type]
        kind = "base64"

    if _looks_like_pdf(raw):
        return _pdf_to_pages(raw)
    return [LoadedPage(image=_bytes_to_image(raw), page_index=0, source_kind=kind)]


def _fetch_url(url: str) -> bytes:
    if not url.lower().startswith(("http://", "https://")):
        raise ImageLoadError(f"image_url 必须是 http(s) 链接，收到：{url[:80]}")
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                chunks: list[bytes] = []
                total = 0
                for chunk in resp.iter_bytes():
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise ImageLoadError(
                            f"下载内容超过 {MAX_DOWNLOAD_BYTES // (1024 * 1024)} MB 上限。"
                        )
                    chunks.append(chunk)
                return b"".join(chunks)
    except httpx.HTTPError as exc:
        raise ImageLoadError(f"下载 image_url 失败：{exc}") from exc


def _decode_base64(data: str) -> bytes:
    # 容忍 data URI 前缀，例如 "data:image/png;base64,...."
    if data.startswith("data:") and "," in data:
        data = data.split(",", 1)[1]
    try:
        raw = base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageLoadError(f"base64 解码失败：{exc}") from exc
    if len(raw) > MAX_DOWNLOAD_BYTES:
        raise ImageLoadError(
            f"base64 内容超过 {MAX_DOWNLOAD_BYTES // (1024 * 1024)} MB 上限。"
        )
    return raw


def _looks_like_pdf(raw: bytes) -> bool:
    return raw[:5] == b"%PDF-"


def _bytes_to_image(raw: bytes) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception as exc:  # PIL 抛的异常类型很杂，统一兜住
        raise ImageLoadError(f"无法解码为图片：{exc}") from exc
    # 统一成 RGB，规避 RGBA/P/CMYK 等让 OCR 引擎困惑的模式
    return img.convert("RGB")


def _pdf_to_pages(raw: bytes) -> list[LoadedPage]:
    """用 PyMuPDF 把 PDF 逐页栅格化。延迟导入，未装依赖时给出清晰提示。"""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - 取决于部署环境
        raise ImageLoadError(
            "检测到 PDF 输入，但未安装 PyMuPDF（pip install pymupdf）。"
        ) from exc

    pages: list[LoadedPage] = []
    try:
        doc = fitz.open(stream=raw, filetype="pdf")
    except Exception as exc:
        raise ImageLoadError(f"无法打开 PDF：{exc}") from exc

    with doc:
        if doc.page_count > MAX_PDF_PAGES:
            raise ImageLoadError(
                f"PDF 共 {doc.page_count} 页，超过 {MAX_PDF_PAGES} 页上限。"
            )
        zoom = PDF_RENDER_DPI / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            pages.append(LoadedPage(image=img, page_index=i, source_kind="pdf"))
    return pages
