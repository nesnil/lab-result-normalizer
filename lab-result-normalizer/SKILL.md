---
name: lab-result-normalizer
description: 检验结果标准化治理工具。当用户提供一份或多份检验报告（血常规 / 生化 / 凝血），或粘贴检验单文本、上传检验报告图片，并希望对其进行结构化、标准化、多源融合或质控时使用。本 skill 将不同医院、不同格式、不同单位的检验报告，统一治理为可计算、可比较、可入库的高质量数据集：识别检验项目并归一同义名称、映射到国际标准 LOINC 编码、换算到标准单位、判定异常与危急值、生成质控告警。触发关键词：检验报告、化验单、检验结果、血常规、生化、凝血、LOINC、单位标准化、检验数据治理、多源融合、参考区间、危急值、异常值、化验数据结构化。
license: MIT
compatibility: "纯文本主线模型无关（默认 DeepSeek-V4-Pro）；图片输入增强可选调用自建 lab-ocr-mcp（需联网 streamableHTTP），不可用时回退多模态模型读图"
metadata:
  author: "acits-xskills 参赛作品（AI for Data 数据治理赛道主力作品）"
  version: "1.0.0"
  track: "AI for Data 数据治理"
  pipeline: "5 阶段：解析拆分 → 项目归一 → LOINC 映射 → 单位数值标准化 → 异常判定与质控"
  optional_mcp: "自建 lab-ocr-mcp（图→文输入增强）；预留 loinc-mcp 分层检索接口"
---

# Lab Result Normalizer — 检验结果标准化治理

## 概述

本 skill 面向**检验报告（化验单）数据治理**。临床检验数据普遍存在"同项异名、同义异单位、参考区间不一、格式各异"的问题，导致跨医院、跨系统数据无法直接比较和计算。本 skill 把任意来源的检验报告，治理为一份**标准化、可计算、可入库**的数据集。

四件核心工作（也是与平台已有 `medical_icd_extractor` 的本质区别——后者面向图片做"医学实体→ICD 诊断编码"，不处理检验数值、单位、参考区间）：

1. **项目归一** —— 将"谷丙转氨酶 / ALT / GPT"等同义异名统一到标准项目名
2. **LOINC 标准化** —— 为每个检验项映射国际通用的 LOINC 编码，实现跨源可比
3. **单位与数值标准化** —— 将结果换算到统一标准单位
4. **异常判定与质控** —— 标注 ↑/↓/危急值，校验逻辑冲突，生成质控告警

> 本 skill 为**研究与数据治理辅助工具**，输出供数据入库与人工复核使用，不构成诊疗建议。

## 触发条件

当用户做以下任一时触发：
- 提供检验报告文本 / 截图，要求结构化、标准化、编码、入库
- 要求把多份不同来源的检验报告归一为统一格式
- 要求识别检验结果中的异常值、危急值或数据质量问题

关键词：检验报告、化验单、血常规、生化、凝血、LOINC、单位标准化、参考区间、危急值、检验数据治理、多源融合。

## 覆盖范围（v1）

| 报告类型 | 覆盖项目 |
|---|---|
| 血常规 CBC | WBC、RBC、HGB、HCT、PLT、MCV、MCH、MCHC、RDW-CV、NEUT%/#、LYMPH%/#、MONO%/#、EO%/#、BASO%/# |
| 生化 Chemistry | ALT、AST、ALP、GGT、TBIL、DBIL、TP、ALB、GLU、UREA、CREA、UA、TC、TG、HDL-C、LDL-C、K、Na、Cl、Ca、CK、CK-MB、LDH |
| 凝血 Coagulation | PT、PT-INR、APTT、TT、FIB、D-Dimer |

未覆盖的项目按"未匹配"处理并记录到 warnings，不臆造编码。

---

## 工作流程（5 个阶段）

按顺序执行，每阶段产物作为下一阶段输入。整个过程对用户可见：每完成一个阶段，简要展示中间结果，再进入下一阶段。所有标准（LOINC 码、同义词、换算系数、参考区间、判定规则）**一律查 references/ 中的规则表，不得凭记忆臆造**。

### 阶段 1：输入处理、解析与拆分

**目标**：把报告（可能含表头、患者信息、多项目）拆成一条条"检验项记录"，每条抽取四元组。

输入分两种来源，**文本为主线，图片为可选入口**：

- **文本输入（主线）**：用户直接粘贴检验单文本 / 上传文本文件。直接进入解析。本主线模型无关，使用平台默认模型（DeepSeek-V4-Pro）即可稳定运行。
- **图片输入（可选）**：用户上传检验单图片。优先调用自建 OCR MCP 工具 `ocr_extract_text(image_url)` 将图片转为纯文本后再解析；该 MCP 不可用时，回退到具备多模态能力的模型（如 Kimi）读图取文，并在 metadata 标注 `ocr_source`。OCR 仅负责"图→文"，不做任何标准化。

> 设计原则：图片/OCR 是可选增强，**核心治理链路只依赖文本**——有 OCR 锦上添花，无 OCR 主线照跑。

解析步骤（两种来源得到文本后一致）：
- 对每个检验项，抽取四元组：
  - `raw_name`：报告上的原始项目名（保留原文）
  - `raw_value`：原始结果值（数值或定性，如"阳性"）
  - `raw_unit`：原始单位（可能缺失）
  - `raw_ref_range`：报告上印的参考区间（可能缺失）
- 保留来源信息：医院/科室名、报告类型、采样时间（如可识别）。
- **不要在本阶段做任何标准化或判断**，只做忠实拆分。

展示：解析出的原始四元组列表，并报告"共识别 N 项"。

### 阶段 2：项目归一

**目标**：把 `raw_name` 归一到标准项目名 `std_name`。

- 查 `references/synonyms.md`，将中文全称、英文缩写、别名、大小写/全半角差异统一到标准项目名。
- 归一时记录 `match_type`：`exact`（直接命中标准名）/ `synonym`（经别名表命中）/ `unmatched`（表中无）。
- `unmatched` 的项目保留 `raw_name`，标记 `std_name=null`，并加入 warnings，**后续阶段对其跳过 LOINC/单位/参考区间处理**。

### 阶段 3：LOINC 映射

**目标**：为每个 `std_name` 配 LOINC 编码。

LOINC 全量约 9.8 万个 concept 且每半年更新，无法全部内置。本 skill 采用**分层映射**策略（漏斗式，越靠前越快越准）：

1. **第一层 · 高频精表命中（默认）**：查 `references/loinc_mapping.md`，取该标准项的 `loinc_code` 与 `loinc_long_name`。本表覆盖血常规/生化/凝血高频项，命中即标 P0/P1，覆盖绝大多数临床请求，零成本、可审计。
2. **第二层 · 全量检索兜底（可选增强，预留接口）**：表外项目调用 `loinc-mcp` 的 `loinc_lookup(name, sample_type?, top_k)`——其内部为"结构化过滤（按样本类型/属性硬过滤）+ BM25 关键词与向量语义混合召回 + 重排序 + 置信闸门"。返回结果按置信度标 P1/P2，并标注 `source=loinc-mcp`。

- 标注匹配级别与置信度：
  | 级别 | 条件 | 置信度 |
  |---|---|---|
  | P0 | 高频精表精准命中 | 0.95+ |
  | P1 | 精表命中但依赖样本/方法默认假设，或 loinc-mcp 高置信返回 | 0.85–0.94 |
  | P2 | loinc-mcp 中置信返回 / 仅关键词部分命中 | 0.70–0.84 |
  | P3 | 无法映射或低于置信闸门 | <0.50，记 warnings |
- **绝不臆造 LOINC 码**：精表未命中且 `loinc-mcp` 不可用或返回低于置信闸门时，一律标 P3 + warnings（LOINC 未映射，建议人工核验），`loinc_code=null`。
- `loinc-mcp` 为可选服务：不可用时第一层照常工作，核心链路不受影响（高频项不依赖外部）。

### 阶段 4：单位与数值标准化

**目标**：把结果换算到统一标准单位 `std_unit`，得到 `std_value`。

- 查 `references/unit_conversion.md`，取该标准项的 `std_unit` 及从 `raw_unit` 到 `std_unit` 的换算系数。
- 换算规则：
  - `raw_unit` 已是标准单位 → `std_value = raw_value`，`conversion_factor=1`
  - `raw_unit` 是已知非标单位 → 按系数换算，记录 `conversion_factor`
  - `raw_unit` 缺失 → 按该项在换算表中标注的"默认单位假设"处理，并加 warnings（单位缺失，按默认单位假设）
  - `raw_unit` 未知/无法换算 → 保留原值，标 warnings（单位无法识别，未换算）
- 定性结果（阳性/阴性、+/-）不做数值换算，保留原文，`std_value` 记为定性值。
- 数值保留合理有效位数（与该项标准单位的常规精度一致）。

### 阶段 5：异常判定与质控

**目标**：基于标准单位判定异常，并做数据质控。

- **异常判定**：查 `references/reference_ranges.md`，按性别/年龄选对应参考区间（信息缺失时用通用成人区间并加 warnings）。判定 `flag`：
  - `N` 正常 / `H` 偏高(↑) / `L` 偏低(↓)
  - 优先使用报告自带的 `raw_ref_range`（如存在且与标准单位一致）；否则用标准区间。两者冲突时以标准区间为准并记 warnings。
- **危急值判定**：查 `references/abnormal_flag_rules.md` 的危急值阈值，命中则 `critical=true`，加高优先级 warning。
- **逻辑冲突校验**：执行 `abnormal_flag_rules.md` 中的交叉校验规则（如 HCT ≈ HGB×3 不成立、白细胞分类百分比之和明显偏离 100%、DBIL>TBIL 等），冲突写入 warnings。
- 汇总所有 warnings。

---

## 输出

按 `references/output_schema.md` 定义输出。**先输出一段人读 Markdown 摘要表**（高亮异常↑↓与危急值、列出质控告警），**再输出完整结构化 JSON**（可入库的标准化数据集）。

JSON 必须包含：每个项目的 `raw_name / std_name / loinc_code / loinc_long_name / raw_value / raw_unit / std_value / std_unit / conversion_factor / ref_range / flag / critical / match_level / confidence`，以及报告级 `metadata`（来源、项目数、按类型计数、检出异常数、危急值数、warnings、是否多源融合）。

多份报告输入时，按报告分组输出，并在 metadata 标注 `multi_source=true`，体现"多源异构融合治理"。

## 质量约束

- **规则表优先**：所有编码、换算、区间、判定都来自 references/，不臆造。
- **忠实可追溯**：始终保留 `raw_*` 原文，便于人工复核。
- **不臆造编码**：无法映射的项目标 P3 + warnings，绝不编造 LOINC 码。
- **质控可见**：所有数据质量问题（单位缺失/无法识别、区间冲突、逻辑冲突、危急值）必须进入 warnings，不静默丢弃。
- **置信度标注**：对不确定的映射/换算标注较低置信度。
- **非诊断**：输出面向数据治理与人工复核，不给诊疗结论。

## 参考文件索引

| 文件 | 内容 |
|---|---|
| references/synonyms.md | 检验项同义词 / 别名 / 英文缩写 → 标准项目名归一表 |
| references/loinc_mapping.md | 标准项目名 → LOINC 编码主表（Code + Long Common Name + 标准单位） |
| references/unit_conversion.md | 各标准项的标准单位、常见非标单位与换算系数、默认单位假设 |
| references/reference_ranges.md | 标准参考区间表（性别 / 年龄分层） |
| references/abnormal_flag_rules.md | 异常标记、危急值阈值、逻辑冲突校验规则 |
| references/output_schema.md | 输出 JSON Schema 定义、字段说明与人读表格格式规范 |
