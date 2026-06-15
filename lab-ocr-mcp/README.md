# lab-ocr-mcp

检验报告（化验单）OCR 的 **Streamable HTTP MCP 服务**，为「算丰杯」医疗 AI Skill 大赛作品、
同目录下的参赛 Skill [`lab-result-normalizer`](../lab-result-normalizer) 提供"图 → 文"输入增强。

- **职责单一**：只把化验单**图片 / PDF** 识别为文本，并把表格**还原成 Markdown 表格**。
  **不做任何医学标准化**（项目归一 / LOINC / 单位换算 / 异常判定全部在 skill 阶段 1–5）。
- **引擎**：[RapidOCR](https://github.com/RapidAI/RapidOCR)（PaddleOCR 模型的 ONNXRuntime 重打包，
  CPU 即可，本地零 API 费用，数据不出本地 —— 契合医疗隐私）。
- **传输**：Streamable HTTP（xskills 平台「新增 MCP 服务器」只接公网 URL + streamableHTTP）。
- **暴露工具**：`ocr_extract_text(image_url | image_base64)`。

> 与 skill 的边界：OCR 只负责"图→文"。有 OCR 锦上添花，无 OCR 时 skill 主线（文本输入）照跑。

---

## 1. 工具契约

`ocr_extract_text` —— 二选一传入：

| 参数 | 说明 |
|------|------|
| `image_url` | 公网可访问的图片或 PDF 的 http(s) 链接 |
| `image_base64` | base64 编码的图片或 PDF（可带 `data:image/png;base64,` 前缀） |

PDF 会逐页栅格化后逐页 OCR（≤20 页）。返回：

```json
{
  "markdown": "| 项目 | 结果 | 单位 | 参考区间 |\n| --- | --- | --- | --- |\n| 谷丙转氨酶 | 58 | U/L | 9-50 |",
  "plain_text": "项目 结果 单位 参考区间\n谷丙转氨酶 58 U/L 9-50",
  "engine": "rapidocr-onnxruntime",
  "page_count": 1,
  "mean_confidence": 0.998,
  "warnings": [],
  "ocr_source": "lab-ocr-mcp"
}
```

`markdown` 即喂给 skill「阶段 1 解析拆分」逐行抽 `raw_name / raw_value / raw_unit / raw_ref_range` 四元组的输入。
质控提示（加载失败、空页等）进 `warnings`，不静默丢弃。

---

## 2. 本地运行（Docker，推荐）

> 本地 Python 3.14 上 `onnxruntime` 无预编译 wheel，故统一用 Docker 锁 Python 3.11。

```bash
# 构建（首次约几分钟，会装依赖并预热 OCR 模型权重）
docker build -t lab-ocr-mcp:latest .

# 启动（不鉴权，仅本地测试）
docker run -d --name lab-ocr-mcp -p 8000:8000 lab-ocr-mcp:latest
# 或： docker compose up -d

# 冒烟测试（合成一张中文化验单表格，验证 loader→ocr 全链路）
docker run --rm -v "$PWD/tests:/app/tests" lab-ocr-mcp:latest python tests/test_smoke.py
```

MCP 端点：`http://localhost:8000/mcp`

---

## 3. 公网部署 + 平台注册

平台是云端 SPA，**必须把服务部署到公网**（云服务器 / 容器平台），拿到一个 https URL。

### 3.1 开启鉴权部署

```bash
export AUTH_TOKEN=$(openssl rand -hex 32)   # 生成强随机 token
AUTH_TOKEN=$AUTH_TOKEN docker compose up -d  # 容器内会校验 Bearer
```

建议在前面再挂一层带 TLS 的反向代理（Nginx / Caddy）把 `https://<你的域名>/mcp` 转发到容器 8000。

### 3.2 在 xskills 平台注册

进入 **MCP 管理 →「新增 MCP 服务器」**，按下表填写：

| 表单字段 | 填写 |
|----------|------|
| 标识名 | `lab-ocr-mcp` |
| 显示名称 | 检验报告 OCR |
| **连接地址** | `https://<你的域名>/mcp` |
| **协议类型** | **streamableHTTP**（默认，保持） |
| 请求头 | `Authorization=Bearer <上面的 AUTH_TOKEN>`（若开了鉴权） |
| 标签 | `OCR,检验,数据治理` |

保存后，在 skill 编辑页右上「MCP 预览」即可看到 `ocr_extract_text` 工具，
`lab-result-normalizer` 的输入增强分支即可调用它。

---

## 4. 代码结构

```
lab-ocr-mcp/
├── src/
│   ├── core/
│   │   ├── loader.py   # 图片加载：image_url / base64 / PDF → PIL 图（只拿像素）
│   │   └── ocr.py      # RapidOCR 封装 + 表格几何还原 → Markdown（纯逻辑，可单测）
│   └── server/
│       └── app.py      # FastMCP streamable-http 壳 + 可选 Bearer 鉴权
├── tests/test_smoke.py # 合成化验单图，端到端验证
├── Dockerfile          # python:3.11-slim，含 opencv 系统库 + 中文字体
├── docker-compose.yml
└── requirements.txt
```

**core / server 分层**：OCR 逻辑与传输无关，今后若平台改用别的 transport，或要做本地 stdio 版，
只换 `server/` 壳，`core/` 不动。

---

## 5. 边界与免责

本服务输出面向**数据治理与人工复核**，不做医学判断、不给诊疗结论。
OCR 存在固有识别误差（如上标符号），原文经 skill 阶段保留 `raw_*` 以便复核。
