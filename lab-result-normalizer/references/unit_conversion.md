# 单位换算表

阶段 4（单位与数值标准化）查本表。目标：把 `raw_value`(`raw_unit`) 换算到统一的 `std_unit`，得到 `std_value`。

## 换算规则

1. 查本表对应 `std_name`，取 `std_unit`。
2. 若 `raw_unit` 已等于 `std_unit`（含同义写法，见"单位同义"）→ `std_value = raw_value`，`conversion_factor = 1`。
3. 若 `raw_unit` 在该项"可换算单位"中 → `std_value = raw_value × factor`，记录 `conversion_factor`。
4. 若 `raw_unit` **缺失** → 按"默认单位假设"处理（多数情况下默认单位即标准单位），加 warnings（单位缺失，按默认单位假设）。
5. 若 `raw_unit` **未知/不可换算** → 保留 `raw_value`，`std_value=null`，加 warnings（单位无法识别，未换算）。
6. **质量↔摩尔换算**需分子量，本表对需要换算的项直接给出系数（已含分子量），无需 Skill 自行计算。
7. 数值精度：按 `std_unit` 常规精度保留（见各项"精度"提示，未注明则保留原值有效位数）。

## 单位同义（写法归一，factor=1）

| 标准写法 | 同义写法 |
|---|---|
| 10^9/L | ×10⁹/L、G/L、10e9/L、10*9/L、/nL |
| 10^12/L | ×10¹²/L、T/L、10e12/L、10*12/L |
| g/L | g/l |
| g/dL | g/dl、g% |
| mmol/L | mM、mmol/l |
| μmol/L | umol/L、µmol/L |
| U/L | IU/L、u/L（酶活性，视为等价） |
| % | ％、percent |
| s | sec、秒 |

---

## 1. 血常规 CBC

| std_name | std_unit | 可换算单位 → factor | 默认单位假设 | 精度 |
|---|---|---|---|---|
| WBC | 10^9/L | /μL(=/uL) → 0.001；/mm³ → 0.001；10^3/μL → 1；K/μL → 1 | 10^9/L | 0.01 |
| RBC | 10^12/L | 10^6/μL → 1；/μL → 1e-6；10^4/μL → 0.01 | 10^12/L | 0.01 |
| HGB | g/L | g/dL → 10；mmol/L → 16.114（×分子量，少见）；mg/mL → 1 | g/L | 1 |
| HCT | % | L/L(小数,如0.45) → 100；比例(0–1) → 100 | % | 0.1 |
| PLT | 10^9/L | /μL → 0.001；10^3/μL → 1；K/μL → 1；万/μL → 10 | 10^9/L | 1 |
| MCV | fL | μm³ → 1（等价） | fL | 0.1 |
| MCH | pg | — | pg | 0.1 |
| MCHC | g/L | g/dL → 10 | g/L | 1 |
| RDW-CV | % | 比例(0–1) → 100 | % | 0.1 |
| NEUT% | % | 比例(0–1) → 100 | % | 0.1 |
| NEUT# | 10^9/L | /μL → 0.001；10^3/μL → 1 | 10^9/L | 0.01 |
| LYMPH% | % | 比例 → 100 | % | 0.1 |
| LYMPH# | 10^9/L | /μL → 0.001；10^3/μL → 1 | 10^9/L | 0.01 |
| MONO% | % | 比例 → 100 | % | 0.1 |
| MONO# | 10^9/L | /μL → 0.001；10^3/μL → 1 | 10^9/L | 0.01 |
| EO% | % | 比例 → 100 | % | 0.1 |
| EO# | 10^9/L | /μL → 0.001；10^3/μL → 1 | 10^9/L | 0.01 |
| BASO% | % | 比例 → 100 | % | 0.1 |
| BASO# | 10^9/L | /μL → 0.001；10^3/μL → 1 | 10^9/L | 0.01 |

## 2. 生化 Chemistry

> 凡涉及 mg/dL ↔ mmol/L 的项，factor 已内置分子量。

| std_name | std_unit | 可换算单位 → factor | 默认单位假设 | 精度 |
|---|---|---|---|---|
| ALT | U/L | μkat/L → 60 | U/L | 0.1 |
| AST | U/L | μkat/L → 60 | U/L | 0.1 |
| ALP | U/L | μkat/L → 60 | U/L | 1 |
| GGT | U/L | μkat/L → 60 | U/L | 1 |
| TBIL | μmol/L | mg/dL → 17.1 | μmol/L | 0.1 |
| DBIL | μmol/L | mg/dL → 17.1 | μmol/L | 0.1 |
| TP | g/L | g/dL → 10 | g/L | 1 |
| ALB | g/L | g/dL → 10 | g/L | 1 |
| GLU | mmol/L | mg/dL → 0.0555 | mmol/L | 0.01 |
| UREA | mmol/L | mg/dL(尿素) → 0.1665；**BUN mg/dL → 0.357**；BUN mmol/L(尿素氮口径) → 1 注意口径 | mmol/L（尿素口径） | 0.01 |
| CREA | μmol/L | mg/dL → 88.4 | μmol/L | 1 |
| UA | μmol/L | mg/dL → 59.48 | μmol/L | 1 |
| TC | mmol/L | mg/dL → 0.0259 | mmol/L | 0.01 |
| TG | mmol/L | mg/dL → 0.0113 | mmol/L | 0.01 |
| HDL-C | mmol/L | mg/dL → 0.0259 | mmol/L | 0.01 |
| LDL-C | mmol/L | mg/dL → 0.0259 | mmol/L | 0.01 |
| K | mmol/L | mEq/L → 1；mg/dL → 0.2558 | mmol/L | 0.01 |
| Na | mmol/L | mEq/L → 1；mg/dL → 0.435 | mmol/L | 0.1 |
| Cl | mmol/L | mEq/L → 1 | mmol/L | 0.1 |
| Ca | mmol/L | mg/dL → 0.2495；mEq/L → 0.5 | mmol/L | 0.01 |
| CK | U/L | μkat/L → 60 | U/L | 1 |
| CK-MB | μg/L | ng/mL → 1（等价）；U/L(活性法) → **不可直接换算**，标 warnings | μg/L（质量法） | 0.1 |
| LDH | U/L | μkat/L → 60 | U/L | 1 |

### 生化换算备注

- **UREA / BUN 口径**：国内"尿素"单位 mmol/L；美制常报"BUN"(尿素氮) mg/dL。尿素(mmol/L) = BUN(mg/dL) × 0.357。若 `raw_name` 经 synonyms 归一为 UREA 但来源标 BUN/mg/dL，按 0.357 换算并在 warnings 注明"按 BUN→尿素口径换算"。
- **CK-MB**：质量法(μg/L 或 ng/mL，等价)与活性法(U/L)不可互换，遇活性法保留原值+warnings。

## 3. 凝血 Coagulation

| std_name | std_unit | 可换算单位 → factor | 默认单位假设 | 精度 |
|---|---|---|---|---|
| PT | s | — | s | 0.1 |
| PT-INR | （无量纲） | — | 无量纲 | 0.01 |
| APTT | s | — | s | 0.1 |
| TT | s | — | s | 0.1 |
| FIB | g/L | mg/dL → 0.01；mg/L → 0.001 | g/L | 0.01 |
| D-Dimer | mg/L FEU | μg/mL FEU → 1；ng/mL FEU → 0.001；**DDU 体系** → 不直接换算，标 warnings(单位体系不同) | mg/L FEU | 0.01 |

### 凝血换算备注

- **D-Dimer 单位体系**：FEU(纤维蛋白原当量) 与 DDU(D-二聚体单位) 是不同报告体系，约 FEU ≈ 2×DDU 但因厂商而异，**不做自动换算**，仅在同为 FEU 体系内做 mg/L ↔ μg/mL ↔ ng/mL 换算；跨体系标 warnings。
- **PT-INR** 无量纲，任何"单位"都忽略。

---

## 维护约定

- factor 定义：`std_value = raw_value × factor`。
- 新增项目须同时在 `loinc_mapping.md` 的 std_unit 与本表保持一致。
- 所有需分子量的换算系数已预先算好内置，Skill 不自行推导分子量。
