# AGENTS.md — acits-xskills

本仓库是"算丰杯"医疗 AI Skill 开发大赛的参赛作品工作区。当前唯一作品为 **`lab-result-normalizer`**（检验结果标准化治理 Skill）。本文件是面向 AI agent 的项目说明，记录已定决策、架构、约定与待办，方便任何新会话冷启动接手。

## 1. 比赛背景与约束

- **赛事**：算丰杯医疗 AI Skill 开发大赛。**提交截止 2026-07-05**。
- **赛道**：AI for Data 数据治理（平台该赛道几乎空白，只有 1 个 ICD 实体映射示例；最契合用户"强技术、无专业医疗背景"）。
- **提交物**：PPT + **≥5 个验证案例**，通过邮件提交。**不直接提交平台文件**——平台只用于把 skill 跑通演示。
- **目标平台**：https://xskills.acits.com.cn/ （账号见本地，未入库）。一个 skill = 一个文件夹，含根 `SKILL.md` + 可选 `references/` 子目录。
- **平台模型**：DeepSeek-V4-Pro（默认）/ minimax / GLM / kimi（**仅 kimi 多模态**）。
- **平台 MCP 现状**：无任何通用 OCR / 文档解析 MCP；无 LOINC 专用查询 MCP。已有 MCP 均为分子/基因组/蛋白/病理图像/文献检索类，与本作品无关。

## 2. 作品定位（差异化话术，PPT 可直接用）

把不同医院、不同格式、不同单位的检验报告（血常规 / 生化 / 凝血），统一治理为**可计算、可比较、可入库**的高质量数据集：项目归一、LOINC 标准化、单位换算、异常/危急值判定、质控告警。

与平台已有 `medical_icd_extractor` **不撞题**：后者是"图片→12 类医学实体→反查 ICD-10/9-CM-3/ICD-O 诊断/手术编码"，**丢失数值/单位/参考区间**等可计算信息；本作品恰好补这块空白，输出 LOINC 编码 + 标准单位 + 归一数值 + 异常分级，使检验数据可跨院比较、可入库分析。

借鉴 `medical_icd_extractor` 的工程化输出范式（结构化 JSON + confidence + match_level + warnings 质控告警），保持"同平台高质量产出"观感，但内容完全不同。

## 3. 目录结构

本项目总目录下含**一个 Skill 目录**（`lab-result-normalizer/`）和**一个自建 MCP 目录**（`lab-ocr-mcp/`）：

```
acits-xskills/                 # 项目总目录
├── AGENTS.md                 # 本文件：项目说明（唯一事实来源）
├── CLAUDE.md                 # 仅 @AGENTS.md，供 Claude Code 读取
├── lab-result-normalizer/    # 参赛 Skill（= 一个文件夹，可整目录打 zip 上传平台）
│   ├── SKILL.md              # 主入口：frontmatter(name+description) + 5 阶段流水线
│   └── references/           # 规则知识库（平台规范用复数 references/）
│       ├── synonyms.md           # 同义名/别名/英文缩写 → 标准项目名
│       ├── loinc_mapping.md      # 标准项目名 → LOINC Code + Long Common Name（⚠ 待核验）
│       ├── unit_conversion.md    # 标准单位、非标单位换算系数、默认单位假设
│       ├── reference_ranges.md   # 参考区间（性别/年龄分层）
│       ├── abnormal_flag_rules.md# 异常标记、危急值阈值、逻辑冲突校验 C1–C10
│       └── output_schema.md      # 输出 JSON Schema + 人读 Markdown 表格规范
└── lab-ocr-mcp/              # 自建 OCR MCP 服务（为 skill 提供"图→文"输入增强）
    ├── README.md             # 部署 + 平台注册（streamableHTTP）说明
    ├── Dockerfile            # python:3.11-slim（锁版本，绕开本地 3.14 onnxruntime 无 wheel）
    ├── docker-compose.yml
    ├── requirements.txt
    ├── src/
    │   ├── core/             # 纯 OCR 逻辑（与传输无关，可单测）
    │   │   ├── loader.py     # image_url / base64 / PDF → PIL 图（只拿像素）
    │   │   └── ocr.py        # RapidOCR 封装 + 表格几何还原 → Markdown
    │   └── server/app.py     # FastMCP streamable-http 壳 + 可选 Bearer 鉴权
    └── tests/test_smoke.py   # 合成化验单图，端到端验证
```

## 4. 架构（已定，不要随意改动）

**5 阶段流水线**（SKILL.md 为权威定义；每阶段产物喂下一阶段，过程对用户可见）：

1. **解析拆分** — 把报告拆成逐条检验项，抽四元组 `raw_name / raw_value / raw_unit / raw_ref_range`，保留来源信息。**本阶段只忠实拆分，不做任何标准化**。
2. **项目归一** — 查 `synonyms.md`，`raw_name → std_name`，记 `match_type`（exact/synonym/unmatched）。unmatched 进 warnings 并跳过后续。
3. **LOINC 映射** — 分层漏斗：①高频精表 `loinc_mapping.md`（P0/P1，覆盖绝大多数，0 成本可审计）→ ②表外走预留接口 `loinc-mcp.loinc_lookup()`（结构化过滤 + BM25/向量混合召回 + rerank + 置信闸门，P1/P2）。**绝不臆造 LOINC 码**：未命中且 MCP 不可用/低于闸门 → P3 + warnings + `loinc_code=null`。
4. **单位与数值标准化** — 查 `unit_conversion.md`，换算到 `std_unit` 得 `std_value`，记 `conversion_factor`；单位缺失/未知按规则进 warnings。定性结果不换算。
5. **异常判定与质控** — 查 `reference_ranges.md` 判 `flag`(N/H/L)、`reference_ranges`+`abnormal_flag_rules.md` 判危急值 `critical`，跑逻辑冲突校验（C1–C10，如 HCT≈HGB×3、白细胞分类%之和≈100、DBIL≤TBIL），全部异常进 warnings。

**输出**：先人读 Markdown 摘要表（高亮 ↑↓ 与危急值、列 warnings），再完整结构化 JSON（可入库）。多份报告 → 分组输出 + `metadata.multi_source=true`。

### 输入端策略（重要）
- **文本为主线，模型无关**：用平台默认 DeepSeek-V4-Pro 即可稳定跑通。核心治理链路**只依赖文本**。
- **图片为可选增强**：优先调自建 OCR MCP `ocr_extract_text(image_url | image_base64)`（见 `lab-ocr-mcp/`）；不可用时回退多模态模型（Kimi）读图，metadata 标 `ocr_source`。OCR 只负责"图→文"（化验单表格还原成 Markdown 表格喂阶段 1），不做标准化。**有 OCR 锦上添花，无 OCR 主线照跑**。
- 自建 OCR MCP 作为"自行扩展 MCP 能力"的加分亮点，**已实现并验证**（代码在本仓库 `lab-ocr-mcp/`）。引擎 RapidOCR（本地零费用、数据不出本地），Streamable HTTP 传输，Docker 部署。**⚠ 平台「新增 MCP 服务器」只接公网 streamableHTTP 端点（无 stdio）**，故须公网部署后把 `https://<域名>/mcp` + 可选 Bearer 填进平台 MCP 管理页。详见 `lab-ocr-mcp/README.md`。

### 覆盖范围（v1，约 50–60 项，刻意收窄以便准备验证案例）
- **血常规 CBC**：WBC/RBC/HGB/HCT/PLT/MCV/MCH/MCHC/RDW-CV/各类白细胞 %/#
- **生化**：ALT/AST/ALP/GGT/TBIL/DBIL/TP/ALB/GLU/UREA/CREA/UA/TC/TG/HDL-C/LDL-C/K/Na/Cl/Ca/CK/CK-MB/LDH
- **凝血**：PT/PT-INR/APTT/TT/FIB/D-Dimer

## 5. 核心原则（改任何内容都必须守住）

- **规则表优先，绝不臆造**：所有 LOINC 码、同义词、换算系数、参考区间、判定阈值一律查 `references/`，不得凭模型记忆编造。这是"数据治理"作品的可信底线，也是评分点。
- **忠实可追溯**：始终保留 `raw_*` 原文，便于人工复核。
- **质控可见，不静默丢弃**：单位缺失/无法识别、区间冲突、逻辑冲突、危急值，全部进 warnings。
- **置信度与匹配级别**：不确定的映射/换算标低置信度 + P0/P1/P2/P3 级别。
- **非诊断**：输出面向数据治理与人工复核，不给诊疗结论。SKILL.md 必须保留免责声明。

## 6. 待办（接手优先级从高到低）

1. **⚠ 核验 LOINC 码（阻塞项，必须用户做）**：`references/loinc_mapping.md` 的 ~48 个 LOINC 码当前全标"待核验"，依据是公开知识。**需用户用 loinc.org / RELMA 官方库逐项核验**后，把"状态"列改为"已核验"。我（agent）无法登录 loinc.org 核验，只能提供候选值 + 公开依据供用户比对。
2. **准备 ≥5 个验证案例**：混合策略——少量真实脱敏样例打底，其余 AI 生成仿真检验报告补足。**仿真样例必须标注"仿真"**。覆盖：单源单类型、多源融合、含异常/危急值、含单位非标需换算、含表外未匹配项各至少一例。
3. **画 PPT 架构图**：重点画 LOINC 分层检索漏斗（精表 → 结构化过滤 → BM25+向量混合 → rerank → 置信闸门 → loinc-mcp），作为"可扩展性/产品化"亮点——**本期不实现 loinc-mcp，只在架构上体现并预留接口**。比赛主体用高频精表保质量保可信。
4. **平台落地演示**：整 `lab-result-normalizer/` 目录打 zip 上传平台跑通，截图入 PPT。
5. **自建 OCR MCP** —— 代码已完成并端到端验证（`lab-ocr-mcp/`，RapidOCR + streamableHTTP + Docker）。**剩余工作：公网部署**（云服务器/容器 + TLS），拿到 `https://<域名>/mcp` 后在平台 MCP 管理页注册（协议选 streamableHTTP，可选 Bearer）。部署步骤见 `lab-ocr-mcp/README.md` 第 3 节。

## 7. 编辑约定

- 改 `SKILL.md` 或任何 `references/*.md` 时，保持现有中文风格、表格格式与字段命名一致。
- `loinc_mapping.md` 改码值后务必同步更新"状态"列；新增项目须同时在 `synonyms.md`/`unit_conversion.md`/`reference_ranges.md` 配齐，避免阶段间断链。
- 新增逻辑冲突校验沿用 `abnormal_flag_rules.md` 的 C1–C10 编号体例。
- 改 `lab-ocr-mcp/` 时守住其单一职责：**只做"图→文"，绝不在 MCP 内做任何医学标准化**（标准化全在 skill 阶段 1–5）。OCR 逻辑写在 `src/core/`（与传输无关、可单测），传输/鉴权写在 `src/server/`，分层不要混。验证用 `docker build` 跑 `tests/test_smoke.py`（本地 Python 3.14 装不上 onnxruntime，统一走 Docker）。
- 本仓库**当前不是 git 仓库**；如需版本管理先 `git init`。
