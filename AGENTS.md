# AGENTS.md — acits-xskills

本仓库是"算丰杯"医疗 AI Skill 开发大赛的参赛作品工作区。

> ⚠️ **当前工作重心（2026-07-02 起）**：**唯一在研作品为 `ortho-discharge-summary`（骨科特色出院小结生成 Skill）**。其余作品 `lab-result-normalizer`、`lab-ocr-mcp` **已停止开发**，**文件保留在仓库/ git 历史中不删除**，但**不再投入**——除非用户明确要求，不要去读/改/优化它们。

- **`ortho-discharge-summary`**（骨科特色出院小结生成 Skill）—— 辅助诊疗/文书生成方向，**当前唯一主力作品**。
- ~~`lab-result-normalizer`（检验结果标准化治理 Skill）~~ —— AI for Data 数据治理赛道，**历史作品，已停止开发**（存档）。
- ~~`lab-ocr-mcp`（自建 OCR MCP 服务）~~ —— 为 lab-result-normalizer 提供"图→文"输入增强，**历史作品，已停止开发**（存档）。

本文件是面向 AI agent 的项目说明，记录已定决策、架构、约定与待办，方便任何新会话冷启动接手。

## 1. 比赛背景与约束

- **赛事**：算丰杯医疗 AI Skill 开发大赛。**提交截止 2026-07-05**。
- **赛道**：AI for Data 数据治理（平台该赛道几乎空白，只有 1 个 ICD 实体映射示例；最契合用户"强技术、无专业医疗背景"）。
- **提交物**：PPT + **≥5 个验证案例**，通过邮件提交。**不直接提交平台文件**——平台只用于把 skill 跑通演示。
- **目标平台**：https://xskills.acits.com.cn/ （账号见本地，未入库）。一个 skill = 一个文件夹，含根 `SKILL.md` + 可选 `references/` 子目录。
- **平台模型**：DeepSeek-V4-Pro（默认）/ minimax / GLM / kimi（**仅 kimi 多模态**）。
- **平台 MCP 现状**：无任何通用 OCR / 文档解析 MCP；无 LOINC 专用查询 MCP。已有 MCP 均为分子/基因组/蛋白/病理图像/文献检索类，与本作品无关。

## 2. 作品定位（差异化话术，PPT 可直接用）

### `ortho-discharge-summary`（骨科特色出院小结生成）— 当前唯一主力
把住院期间零散、多来源的诊疗资料，治理为一份**规范、完整、可直接供医生审核签发**的骨科出院小结。区别于通用内科小结：准确表达术式（含入路、内固定物）、骨折/疾病分型、患肢功能与负重康复时序、VTE 预防、内固定随访。

差异化卖点：①**「通用骨架 + 可插拔骨科医生知识库」**——专科深度可由医生增量补充，体现"医生 × 技术"协作；②**强质控、不臆造、需医生签发**，定位为"文书治理辅助"而非"自动写作机"，与平台 MDT/核保类作品错位。

## 3. 目录结构

本项目总目录下含 `ortho-discharge-summary/`（**当前唯一在研**）以及两个**已停止开发、仅存档**的目录（`lab-result-normalizer/`、`lab-ocr-mcp/`，保留不删）。完整目录树如下（存档部分保留供参考）：

```
acits-xskills/                 # 项目总目录
├── AGENTS.md                 # 本文件：项目说明（唯一事实来源）
├── CLAUDE.md                 # 仅 @AGENTS.md，供 Claude Code 读取
├── README.md                 # 面向人/GitHub 的仓库说明
├── LICENSE                   # MIT
├── lab-result-normalizer/    # 参赛 Skill ①（= 一个文件夹，可整目录打 zip 上传平台）
│   ├── SKILL.md              # 主入口：frontmatter(name+description) + 5 阶段流水线
│   └── references/           # 规则知识库（平台规范用复数 references/）
│       ├── synonyms.md           # 同义名/别名/英文缩写 → 标准项目名
│       ├── loinc_mapping.md      # 标准项目名 → LOINC Code + Long Common Name（⚠ 待核验）
│       ├── unit_conversion.md    # 标准单位、非标单位换算系数、默认单位假设
│       ├── reference_ranges.md   # 参考区间（性别/年龄分层）
│       ├── abnormal_flag_rules.md# 异常标记、危急值阈值、逻辑冲突校验 C1–C10
│       └── output_schema.md      # 输出 JSON Schema + 人读 Markdown 表格规范
├── ortho-discharge-summary/  # 参赛 Skill ②（骨科特色出院小结生成）
│   ├── SKILL.md              # 主入口：frontmatter + 5 阶段生成流水线
│   └── references/           # 「通用骨架 + 可插拔骨科医生知识库」
│       ├── extraction_rules.md     # 从住院资料抽取出院小结要素的规则 + 逻辑校验
│       ├── ortho_knowledge.md      # 骨科专科知识：术式规范名/分型/内固定物/入路（医生为主）
│       ├── discharge_template.md   # 骨科出院小结标准章节模板与必填项
│       ├── rehab_vte_protocols.md  # 负重/康复计划、VTE 预防、内固定随访（医生为主）
│       └── output_schema.md        # 输出格式：人读小结 + 质控清单 + 结构化 JSON
└── lab-ocr-mcp/              # 自建 OCR MCP 服务（为 skill ① 提供"图→文"输入增强）
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

### 4A. `lab-result-normalizer` —— 5 阶段流水线

（SKILL.md 为权威定义；每阶段产物喂下一阶段，过程对用户可见）：

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

### 4B. `ortho-discharge-summary` —— 5 阶段生成流水线

把住院期间零散的诊疗资料（入院记录/术前诊断与影像/手术记录/病程/医嘱/检验检查）治理为一份**规范、完整、可直接供医生审核签发**的骨科出院小结草稿。SKILL.md 为权威定义；每阶段产物喂下一阶段，过程对用户可见：

1. **资料解析与要素归集** — 查 `extraction_rules.md`，从各类输入抽出院小结要素（基本信息/入出院诊断/手术信息/治疗经过/出院情况），每要素记 `source`，缺失记 `null`。**只忠实归集，不规范化、不补全**。
2. **骨科要素规范化** — 查 `ortho_knowledge.md`，规范手术名称（部位+术式+入路+内固定）、分型（AO/OTA、Gustilo-Anderson、Garden、Schatzker、Frankel 等以知识库收录为准）、内固定物/假体、手术入路；保留 `raw_*`，结果记 `std_*`，未收录的留原文 + 质控提示。
3. **出院小结章节组装** — 查 `discharge_template.md`，按标准章节（入院/出院诊断、入院情况、诊疗经过、手术情况、出院情况、出院医嘱）填充；缺失字段填【待补充：xxx】，不编造。
4. **骨科专项内容生成** — 查 `rehab_vte_protocols.md`，按术式/诊断生成患肢功能、分阶段负重与康复计划、VTE 预防、内固定/假体随访、专科出院注意事项；无依据不臆造，标"建议由经治医生补充"。
5. **质控校验与输出** — 对照模板必填项列缺失项；跑逻辑一致性校验（出院早于入院、手术日期不在住院期间、诊断与术式部位不匹配、患肢侧别矛盾、住院天数与起止不符等）。

**输出**：先人读出院小结草稿（核心产物），后质控清单（缺失/冲突/术语未规范/需医生补充，分级列出），可选结构化要素 JSON。文末固定附**免责声明：AI 辅助生成草稿，须经经治医生审核、修改、签字后方可正式使用**。

**设计要点（PPT 亮点）**：「**通用骨科骨架 + 可插拔专科知识库**」——主流程通用，骨科深度由 `ortho_knowledge.md` 与 `rehab_vte_protocols.md` 承载，**医生补充知识即可加深特色，无需改主流程**。references 索引里标注了主要贡献者（技术 / 骨科医生），体现"医生 × 技术"协作的产品化思路。

## 5. 核心原则（改任何内容都必须守住）

> 两个 skill 共享同一套治理底线；`ortho-discharge-summary` 额外强调"输出为草稿、需医生签发"。

- **规则表优先，绝不臆造**：所有 LOINC 码、同义词、换算系数、参考区间、判定阈值一律查 `references/`，不得凭模型记忆编造。这是"数据治理"作品的可信底线，也是评分点。
- **忠实可追溯**：始终保留 `raw_*` 原文，便于人工复核。
- **质控可见，不静默丢弃**：单位缺失/无法识别、区间冲突、逻辑冲突、危急值，全部进 warnings。
- **置信度与匹配级别**：不确定的映射/换算标低置信度 + P0/P1/P2/P3 级别。
- **非诊断**：输出面向数据治理与人工复核，不给诊疗结论。SKILL.md 必须保留免责声明。

## 6. 待办（当前唯一在研 = ortho-discharge-summary）

### `ortho-discharge-summary`（当前唯一主力）
1. **✅ 知识库已用公开权威文献/指南充实**：`references/ortho_knowledge.md`（AO/OTA、Gustilo-Anderson、Garden、Pauwels、Schatzker、Danis-Weber、Lauge-Hansen、Denis/AO Spine/TLICS、Letournel、Tile/Young-Burgess、Salter-Harris、Neer、Sanders、Frykman、Gartland、Mason、Rüedi-Allgöwer 等 20+ 分型已按原始文献填充并标注来源+临床意义）与 `rehab_vte_protocols.md`（10 类术式分阶段康复方案、VTE 三级预防、随访要点、功能评分量表已填充）。**具体用药剂量、精确疗程天数、本院随访排期、内固定取出具体时间**仍标"【需医生确认】"，未臆造。
2. **✅ frontmatter 已符合官方 Agent Skills 规范**：`name`+`description`（含触发关键词）+`license`+`metadata`（version/author/track/pipeline 均字符串）；已按 agentskills.io 规范核验（详见 [[xskills-platform-structure]] 相关约束）。
3. **准备 ≥5 个验证案例**（进行中，`cases/` 目录）：覆盖创伤骨折内固定、关节置换、脊柱、运动医学等典型场景，含一例资料缺失触发"待补充"、一例逻辑冲突（如侧别矛盾/日期不符）触发质控。**真实脱敏 + 仿真混合，仿真须标注**。提交要求 ≥5 个真实案例的输入输出比对报告。
4. **平台落地演示**：整 `ortho-discharge-summary/` 目录打 zip（`.zip` 推荐）上传平台「Skill 管理→上传技能」跑通，截图入 PPT。
5. **PPT**：突出"通用骨架 + 可插拔骨科医生知识库""输出为草稿需医生签发"两大产品化卖点。

### 已停止开发（存档，不再投入）
- `lab-result-normalizer`、`lab-ocr-mcp`：文件保留在仓库/git 历史，但**不再开发**。相关历史待办（LOINC 核验、OCR 公网部署等）已冻结，除非用户明确重启，不要在其上投入 token。

## 7. 编辑约定

- 改任何 `SKILL.md` 或 `references/*.md` 时，保持现有中文风格、表格格式与字段命名一致；两个 skill 各自独立，不要把检验治理逻辑混进出院小结 skill（反之亦然）。
- **`lab-result-normalizer`**：`loinc_mapping.md` 改码值后务必同步更新"状态"列；新增项目须同时在 `synonyms.md`/`unit_conversion.md`/`reference_ranges.md` 配齐，避免阶段间断链；新增逻辑冲突校验沿用 `abnormal_flag_rules.md` 的 C1–C10 编号体例。
- **`ortho-discharge-summary`**：专科深度全部沉淀进 `ortho_knowledge.md` / `rehab_vte_protocols.md`，**主流程（SKILL.md）保持通用、不写死具体术式**，守住"通用骨架 + 可插拔知识库"边界；新增分型/术式术语在 `ortho_knowledge.md` 收录，并保持 `raw_*`/`std_*` 双轨；任何无依据内容标"待补充/建议医生补充"，文末免责声明不可删。
- 改 `lab-ocr-mcp/` 时守住其单一职责：**只做"图→文"，绝不在 MCP 内做任何医学标准化**（标准化全在 skill 阶段 1–5）。OCR 逻辑写在 `src/core/`（与传输无关、可单测），传输/鉴权写在 `src/server/`，分层不要混。验证用 `docker build` 跑 `tests/test_smoke.py`（本地 Python 3.14 装不上 onnxruntime，统一走 Docker）。
- **版本管理**：本仓库已是 git 仓库，远端 `origin` = https://github.com/nesnil/lab-result-normalizer.git （PUBLIC，MIT）。用 `gh` 操作。提交/推送仅在用户明确要求时进行。
