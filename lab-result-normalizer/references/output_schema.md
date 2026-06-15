# 输出格式规范

阶段输出（SKILL.md "输出"节）查本文件。输出**先人读 Markdown 摘要表，后结构化 JSON**。

## 一、人读 Markdown 摘要（先输出）

面向医生/评委快速阅读。要求：
- 一个总览行：来源、报告类型、项目数、异常数、危急值数。
- 一张表：列出每个项目的 `标准名 / 结果(标准单位) / 参考区间 / 标记`。
- **异常用 ↑↓ 标注，危急值用 🔴 前缀加粗**。
- 表下列出质控告警（按 critical → warning → info 排序）。

示例：

> **检验结果标准化摘要**
> 来源：XX医院 · 报告类型：生化 · 共 8 项 · 异常 3 项 · 危急值 1 项
>
> | 项目 | 结果 | 参考区间 | 标记 |
> |---|---|---|---|
> | 钾 (K) | 🔴 **6.7 mmol/L** | 3.5–5.3 | HH ↑ 危急 |
> | 丙氨酸氨基转移酶 (ALT) | 86 U/L | 9–50 | H ↑ |
> | 肌酐 (CREA) | 102 μmol/L | 57–97 | H ↑ |
> | 葡萄糖 (GLU) | 5.4 mmol/L | 3.9–6.1 | N |
>
> **质控告警**
> - 🔴 critical | 钾达危急值（6.7 mmol/L），建议立即复核与临床通报
> - ⚠️ warning | 高钾，提示排查标本溶血（假性高钾）[C9]
> - ℹ️ info | 缺年龄信息，按通用成人区间判定

## 二、结构化 JSON（后输出）

可入库的标准化数据集。顶层结构：

```json
{
  "schema_version": "1.0",
  "source": {
    "facility": "XX医院",
    "department": "检验科",
    "report_type": "chemistry",
    "collected_at": "2026-05-20T08:30:00+08:00",
    "patient": { "sex": "M", "age": 58, "age_unit": "year" },
    "input_type": "text",
    "ocr_source": null
  },
  "items": [
    {
      "raw_name": "谷丙转氨酶",
      "std_name": "ALT",
      "std_name_cn": "丙氨酸氨基转移酶",
      "name_match_type": "synonym",
      "loinc_code": "1742-6",
      "loinc_long_name": "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
      "loinc_match_level": "P0",
      "loinc_confidence": 0.95,
      "raw_value": "86",
      "raw_unit": "U/L",
      "std_value": 86,
      "std_unit": "U/L",
      "conversion_factor": 1,
      "value_type": "quantitative",
      "ref_range": { "low": 9, "high": 50, "source": "standard" },
      "flag": "H",
      "critical": false,
      "context": "肝功能 ALT 86 U/L",
      "warnings": []
    },
    {
      "raw_name": "钾",
      "std_name": "K",
      "std_name_cn": "钾",
      "name_match_type": "exact",
      "loinc_code": "2823-3",
      "loinc_long_name": "Potassium [Moles/volume] in Serum or Plasma",
      "loinc_match_level": "P0",
      "loinc_confidence": 0.95,
      "raw_value": "6.7",
      "raw_unit": "mmol/L",
      "std_value": 6.7,
      "std_unit": "mmol/L",
      "conversion_factor": 1,
      "value_type": "quantitative",
      "ref_range": { "low": 3.5, "high": 5.3, "source": "standard" },
      "flag": "HH",
      "critical": true,
      "context": "电解质 K 6.7",
      "warnings": [
        { "level": "critical", "code": "CRITICAL_VALUE", "message": "钾达危急值（6.7 mmol/L），建议立即复核与临床通报" },
        { "level": "warning", "code": "LOGIC_CONFLICT_C9", "message": "高钾，提示排查标本溶血（假性高钾）" }
      ]
    }
  ],
  "metadata": {
    "total_items": 8,
    "items_by_category": { "chemistry": 8 },
    "abnormal_count": 3,
    "critical_count": 1,
    "unmatched_count": 0,
    "loinc_mapped_count": 8,
    "multi_source": false,
    "warning_count": 3,
    "warnings": [
      { "level": "info", "code": "DEMOGRAPHIC_MISSING", "message": "缺年龄信息，按通用成人区间判定", "related_items": [] }
    ],
    "processed_at": "2026-05-20T10:00:00+08:00",
    "skill_version": "lab-result-normalizer/1.0"
  }
}
```

## 三、字段说明

### source（报告来源）
| 字段 | 说明 |
|---|---|
| facility / department | 医院 / 科室（可识别则填，否则 null） |
| report_type | `cbc` / `chemistry` / `coagulation` / `mixed` |
| collected_at | 采样时间 ISO8601（可识别则填） |
| patient.sex | `M`/`F`/null；patient.age + age_unit |
| input_type | `text` / `image` |
| ocr_source | 图片输入时记 `ocr_mcp` / `model_multimodal`；文本输入为 null |

### items[]（每个检验项）
| 字段 | 说明 |
|---|---|
| raw_name | 报告原始项目名（忠实保留） |
| std_name / std_name_cn | 标准缩写 / 中文标准名 |
| name_match_type | `exact` / `synonym` / `unmatched` |
| loinc_code / loinc_long_name | 来自 loinc_mapping.md；unmatched 或 P3 时为 null |
| loinc_match_level / loinc_confidence | P0/P1/P2/P3 与置信度 |
| raw_value / raw_unit | 原始值 / 原始单位（忠实保留） |
| std_value / std_unit | 换算后值 / 标准单位；无法换算时 std_value=null |
| conversion_factor | 换算系数（=1 表示无需换算） |
| value_type | `quantitative` / `qualitative` |
| ref_range | {low, high, source}；source=`report`/`standard` |
| flag | N/H/L/HH/LL/N/A |
| critical | bool |
| context | 原文上下文片段（供人工复核） |
| warnings[] | 该项相关告警 |

### metadata（报告级）
字段定义见 `abnormal_flag_rules.md` 第五节。`multi_source=true` 表示本次输入含多份不同来源报告。

## 四、多源融合输出

输入多份报告时，输出为**报告数组**：

```json
{
  "schema_version": "1.0",
  "multi_source": true,
  "reports": [ { /* 单份结构同上：source/items/metadata */ }, { /* ... */ } ],
  "fusion_summary": {
    "report_count": 2,
    "unified_std_units": true,
    "comparable": true,
    "note": "已将不同来源、不同单位的同类项目归一到统一 LOINC 编码与标准单位，可直接横向比较"
  }
}
```

人读摘要在多源时应额外给一张**同项跨报告对比表**（同一 std_name 在各报告的 std_value 并列），直观展示"多源异构融合"成效。

## 五、输出约束

- 数值字段输出为 JSON number（非字符串）；无法换算的 std_value 用 null。
- 忠实保留所有 raw_* 原文，便于审计追溯。
- 不臆造任何 loinc_code；P3/unmatched 一律 null + warnings。
- JSON 必须可被机器解析（合法 JSON，无注释、无尾逗号）。
