# LOINC 映射主表

本表是检验结果标准化的**核心权威资产**。阶段 3（LOINC 映射）查本表。

## 使用说明

- 查找键为**标准项目名 `std_name`**（由阶段 2 经 `synonyms.md` 归一后得到）。
- 每行给出该项的 LOINC 编码、LOINC Long Common Name、标准单位（与 `unit_conversion.md` 一致）、默认样本/方法学假设。
- **匹配级别**：
  - `P0`：本表精准命中（标准名 + 默认样本类型成立）。
  - `P1`：命中但依赖样本/方法默认假设（如未注明血清/血浆，按默认假设）。
  - 表外项目 → 阶段 3 标 `P3`，进入 warnings，**不得臆造编码**；如需补充可走通用搜索并标低置信度。

> ⚠️ **码值核验状态**：下表 LOINC 码依据公开常识填写，标注为 `待核验`。上平台前请用 LOINC 官方数据库（loinc.org / RELMA）逐项核对 Code 与 Long Common Name，确认后将"状态"列改为 `已核验`。LOINC 同一分析物常因样本类型（Ser/Plas vs Bld）、计量方式而有多个码，请按检验科常用口径选定。

---

## 1. 血常规 CBC（样本默认：全血 Blood）

| std_name | 中文标准名 | LOINC Code | LOINC Long Common Name | 标准单位 | 级别 | 状态 |
|---|---|---|---|---|---|---|
| WBC | 白细胞计数 | 6690-2 | Leukocytes [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |
| RBC | 红细胞计数 | 789-8 | Erythrocytes [#/volume] in Blood by Automated count | 10^12/L | P0 | 待核验 |
| HGB | 血红蛋白 | 718-7 | Hemoglobin [Mass/volume] in Blood | g/L | P0 | 待核验 |
| HCT | 红细胞压积 | 4544-3 | Hematocrit [Volume Fraction] of Blood by Automated count | % | P0 | 待核验 |
| PLT | 血小板计数 | 777-3 | Platelets [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |
| MCV | 平均红细胞体积 | 787-2 | MCV [Entitic volume] by Automated count | fL | P0 | 待核验 |
| MCH | 平均红细胞血红蛋白量 | 785-6 | MCH [Entitic mass] by Automated count | pg | P0 | 待核验 |
| MCHC | 平均红细胞血红蛋白浓度 | 786-4 | MCHC [Mass/volume] by Automated count | g/L | P0 | 待核验 |
| RDW-CV | 红细胞分布宽度CV | 788-0 | Erythrocyte distribution width [Ratio] by Automated count | % | P0 | 待核验 |
| NEUT% | 中性粒细胞百分比 | 770-8 | Neutrophils/100 leukocytes in Blood by Automated count | % | P0 | 待核验 |
| NEUT# | 中性粒细胞绝对值 | 751-8 | Neutrophils [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |
| LYMPH% | 淋巴细胞百分比 | 736-9 | Lymphocytes/100 leukocytes in Blood by Automated count | % | P0 | 待核验 |
| LYMPH# | 淋巴细胞绝对值 | 731-0 | Lymphocytes [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |
| MONO% | 单核细胞百分比 | 5905-5 | Monocytes/100 leukocytes in Blood by Automated count | % | P0 | 待核验 |
| MONO# | 单核细胞绝对值 | 742-7 | Monocytes [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |
| EO% | 嗜酸性粒细胞百分比 | 713-8 | Eosinophils/100 leukocytes in Blood by Automated count | % | P0 | 待核验 |
| EO# | 嗜酸性粒细胞绝对值 | 711-2 | Eosinophils [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |
| BASO% | 嗜碱性粒细胞百分比 | 706-2 | Basophils/100 leukocytes in Blood by Automated count | % | P0 | 待核验 |
| BASO# | 嗜碱性粒细胞绝对值 | 704-7 | Basophils [#/volume] in Blood by Automated count | 10^9/L | P0 | 待核验 |

## 2. 生化 Chemistry（样本默认：血清 Serum/Plasma）

| std_name | 中文标准名 | LOINC Code | LOINC Long Common Name | 标准单位 | 级别 | 状态 |
|---|---|---|---|---|---|---|
| ALT | 丙氨酸氨基转移酶 | 1742-6 | Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma | U/L | P0 | 待核验 |
| AST | 天门冬氨酸氨基转移酶 | 1920-8 | Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma | U/L | P0 | 待核验 |
| ALP | 碱性磷酸酶 | 6768-6 | Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma | U/L | P0 | 待核验 |
| GGT | γ-谷氨酰转移酶 | 2324-2 | Gamma glutamyl transferase [Enzymatic activity/volume] in Serum or Plasma | U/L | P0 | 待核验 |
| TBIL | 总胆红素 | 1975-2 | Bilirubin.total [Mass/volume] in Serum or Plasma | μmol/L | P0 | 待核验 |
| DBIL | 直接胆红素 | 1968-7 | Bilirubin.direct [Mass/volume] in Serum or Plasma | μmol/L | P0 | 待核验 |
| TP | 总蛋白 | 2885-2 | Protein [Mass/volume] in Serum or Plasma | g/L | P0 | 待核验 |
| ALB | 白蛋白 | 1751-7 | Albumin [Mass/volume] in Serum or Plasma | g/L | P0 | 待核验 |
| GLU | 葡萄糖（血糖） | 2345-7 | Glucose [Mass/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| UREA | 尿素 | 3094-0 | Urea nitrogen [Mass/volume] in Serum or Plasma | mmol/L | P1 | 待核验 |
| CREA | 肌酐 | 2160-0 | Creatinine [Mass/volume] in Serum or Plasma | μmol/L | P0 | 待核验 |
| UA | 尿酸 | 3084-1 | Urate [Mass/volume] in Serum or Plasma | μmol/L | P0 | 待核验 |
| TC | 总胆固醇 | 2093-3 | Cholesterol [Mass/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| TG | 甘油三酯 | 2571-8 | Triglyceride [Mass/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| HDL-C | 高密度脂蛋白胆固醇 | 2085-9 | Cholesterol in HDL [Mass/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| LDL-C | 低密度脂蛋白胆固醇 | 13457-7 | Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation | mmol/L | P1 | 待核验 |
| K | 钾 | 2823-3 | Potassium [Moles/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| Na | 钠 | 2951-2 | Sodium [Moles/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| Cl | 氯 | 2075-0 | Chloride [Moles/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| Ca | 钙 | 17861-6 | Calcium [Mass/volume] in Serum or Plasma | mmol/L | P0 | 待核验 |
| CK | 肌酸激酶 | 2157-6 | Creatine kinase [Enzymatic activity/volume] in Serum or Plasma | U/L | P0 | 待核验 |
| CK-MB | 肌酸激酶同工酶MB | 13969-1 | Creatine kinase.MB [Mass/volume] in Serum or Plasma | μg/L | P1 | 待核验 |
| LDH | 乳酸脱氢酶 | 2532-0 | Lactate dehydrogenase [Enzymatic activity/volume] in Serum or Plasma | U/L | P0 | 待核验 |

> 备注：UREA 在国内常报"尿素"(mmol/L)，LOINC 3094-0 名为 Urea nitrogen(BUN)，两者数值口径不同（尿素 = BUN×2.14 的换算关系按检验科口径，见 `unit_conversion.md` 备注）；列 P1 提示需确认口径。CK-MB 有"质量法 mass"与"活性法 U/L"两种，本表默认质量法，活性法需另选码。

## 3. 凝血 Coagulation（样本默认：血浆 Plasma，PPP）

| std_name | 中文标准名 | LOINC Code | LOINC Long Common Name | 标准单位 | 级别 | 状态 |
|---|---|---|---|---|---|---|
| PT | 凝血酶原时间 | 5902-2 | Prothrombin time (PT) | s | P0 | 待核验 |
| PT-INR | 国际标准化比值 | 6301-6 | INR in Platelet poor plasma by Coagulation assay | （比值，无量纲） | P0 | 待核验 |
| APTT | 活化部分凝血活酶时间 | 14979-9 | aPTT in Platelet poor plasma by Coagulation assay | s | P0 | 待核验 |
| TT | 凝血酶时间 | 3243-3 | Thrombin time | s | P0 | 待核验 |
| FIB | 纤维蛋白原 | 3255-7 | Fibrinogen [Mass/volume] in Platelet poor plasma by Coagulation assay | g/L | P0 | 待核验 |
| D-Dimer | D-二聚体 | 48065-7 | Fibrin D-dimer FEU [Mass/volume] in Platelet poor plasma | mg/L FEU | P1 | 待核验 |

> 备注：D-Dimer 有 FEU（纤维蛋白原当量单位）与 DDU（D-二聚体单位）两种报告体系，单位也分 mg/L、μg/mL、ng/mL，换算与口径见 `unit_conversion.md`；列 P1 提示需确认单位体系。

---

## 维护约定

- 新增项目时：先在 `synonyms.md` 加别名、本表加行、`unit_conversion.md` 加单位、`reference_ranges.md` 加区间，四表保持 `std_name` 一致。
- `std_name` 命名规范：优先用国际通用英文缩写（大写），百分比项加 `%`、绝对值项加 `#`。
