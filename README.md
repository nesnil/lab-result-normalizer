# acits-xskills · 检验结果标准化治理 Skill

> 「算丰杯」医疗 AI Skill 开发大赛参赛作品 · AI for Data 数据治理赛道

把不同医院、不同格式、不同单位的**检验报告（血常规 / 生化 / 凝血）**，统一治理为
**可计算、可比较、可入库**的高质量数据集：项目归一 → LOINC 国际标准编码 → 单位换算 →
异常 / 危急值判定 → 质控告警。

临床检验数据普遍存在"同项异名、同义异单位、参考区间不一、格式各异"的问题，导致跨医院、
跨系统的数据无法直接比较和计算。本作品针对这一痛点，把任意来源的检验报告治理为一份标准化、
可追溯、可入库的数据集。

> ⚠️ 本作品为**研究与数据治理辅助工具**，输出供数据入库与人工复核使用，**不构成诊疗建议**。

---

## 仓库结构

```
acits-xskills/
├── lab-result-normalizer/    # 参赛 Skill（一个文件夹即一个 skill，可整目录上传 xskills 平台）
│   ├── SKILL.md              # 主入口：frontmatter + 5 阶段流水线定义
│   └── references/           # 规则知识库（治理的事实来源，绝不臆造）
│       ├── synonyms.md           # 同义名/别名/英文缩写 → 标准项目名
│       ├── loinc_mapping.md      # 标准项目名 → LOINC Code + Long Common Name
│       ├── unit_conversion.md    # 标准单位、非标单位换算系数
│       ├── reference_ranges.md   # 参考区间（性别/年龄分层）
│       ├── abnormal_flag_rules.md# 异常标记、危急值阈值、逻辑冲突校验 C1–C10
│       └── output_schema.md      # 输出 JSON Schema + 人读 Markdown 表格规范
│
└── lab-ocr-mcp/              # 自建 OCR MCP 服务（为 skill 提供"图 → 文"输入增强）
    ├── README.md             # 部署 + 平台注册（Streamable HTTP）说明
    ├── src/core/             # 纯 OCR 逻辑（RapidOCR 封装 + 表格几何还原）
    ├── src/server/           # FastMCP streamable-http 壳 + 可选 Bearer 鉴权
    └── tests/                # 合成化验单图端到端验证
```

## 核心:5 阶段治理流水线

定义见 [`lab-result-normalizer/SKILL.md`](lab-result-normalizer/SKILL.md)。每阶段产物喂下一阶段，过程对用户可见：

1. **解析拆分** —— 把报告拆成逐条检验项，抽 `raw_name / raw_value / raw_unit / raw_ref_range` 四元组，忠实保留原文。
2. **项目归一** —— 查 `synonyms.md`，`raw_name → std_name`，记 `match_type`。
3. **LOINC 映射** —— 分层漏斗：高频精表优先 → 表外走预留的 `loinc-mcp` 接口。**绝不臆造 LOINC 码**。
4. **单位与数值标准化** —— 查 `unit_conversion.md` 换算到标准单位，记换算系数。
5. **异常判定与质控** —— 判 `flag`(N/H/L) 与危急值，跑逻辑冲突校验（C1–C10），全部异常进 warnings。

**输出**：先人读 Markdown 摘要表（高亮 ↑↓ 与危急值），再完整结构化 JSON（可入库）。

## 设计原则

- **规则表优先，绝不臆造** —— LOINC 码、同义词、换算系数、参考区间、判定阈值一律查 `references/`，不凭模型记忆编造。这是数据治理作品的可信底线。
- **忠实可追溯** —— 始终保留 `raw_*` 原文，便于人工复核。
- **质控可见，不静默丢弃** —— 单位缺失、区间冲突、逻辑冲突、危急值全部进 warnings。
- **非诊断** —— 输出面向数据治理与人工复核，不给诊疗结论。

## 输入端策略

- **文本为主线、模型无关** —— 核心治理链路只依赖文本，用平台默认模型即可稳定跑通。
- **图片为可选增强** —— 优先调自建 OCR MCP（[`lab-ocr-mcp`](lab-ocr-mcp/)）把化验单图片还原成 Markdown 表格；不可用时回退多模态模型读图。**有 OCR 锦上添花，无 OCR 主线照跑**。

## 覆盖范围（v1，约 50–60 项）

| 报告类型 | 覆盖项目 |
|---|---|
| 血常规 CBC | WBC、RBC、HGB、HCT、PLT、MCV、MCH、MCHC、RDW-CV、各类白细胞 %/# |
| 生化 Chemistry | ALT、AST、ALP、GGT、TBIL、DBIL、TP、ALB、GLU、UREA、CREA、UA、TC、TG、HDL-C、LDL-C、K、Na、Cl、Ca、CK、CK-MB、LDH |
| 凝血 Coagulation | PT、PT-INR、APTT、TT、FIB、D-Dimer |

未覆盖项目按"未匹配"处理并记录到 warnings，不臆造编码。

## License

[MIT](LICENSE)。OCR 引擎 [RapidOCR](https://github.com/RapidAI/RapidOCR) 及其依赖遵循各自的开源许可。
