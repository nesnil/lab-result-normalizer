# 同义词 / 别名归一表

阶段 2（项目归一）查本表。目标：把检验报告上五花八门的 `raw_name`（中文全称、英文缩写、别名、大小写/全半角差异、带样本前缀等）归一到统一的标准项目名 `std_name`。

## 归一规则

1. **预处理**（匹配前对 `raw_name` 做规范化）：
   - 去除首尾空格、全角转半角、英文统一大写比对（输出仍用标准 `std_name`）。
   - 去除常见无意义前后缀：样本前缀（血清/血浆/全血/Ser/Plas）、"测定/检测/含量/浓度"等后缀、括号内方法学说明（如"（速率法）"）。
   - 希腊字母与拼写归一：γ/Y/伽马、α/A、β/B。
2. **匹配优先级**：完整别名精准命中 > 去缀后命中 > 关键词包含命中（关键词命中标 `match_type=synonym` 且置信度降一档）。
3. 命中 → 输出对应 `std_name`，`match_type` = `exact`（raw 本身即标准缩写）或 `synonym`（经别名命中）。
4. 未命中 → `std_name=null`，`match_type=unmatched`，加 warnings，后续阶段跳过。

> 下表"别名"列为非穷尽列举，涵盖最常见写法；新写法可继续补充。

---

## 血常规 CBC

| std_name | 别名 / 常见写法 |
|---|---|
| WBC | 白细胞计数、白细胞、白血球、WBC、Leukocyte、白细胞总数 |
| RBC | 红细胞计数、红细胞、RBC、Erythrocyte |
| HGB | 血红蛋白、血色素、Hb、HGB、HB、Hemoglobin |
| HCT | 红细胞压积、红细胞比容、血细胞比容、HCT、Hct、PCV |
| PLT | 血小板计数、血小板、PLT、Plt、Platelet、BPC |
| MCV | 平均红细胞体积、红细胞平均体积、MCV |
| MCH | 平均红细胞血红蛋白量、MCH |
| MCHC | 平均红细胞血红蛋白浓度、MCHC |
| RDW-CV | 红细胞分布宽度、红细胞分布宽度变异系数、RDW、RDW-CV、RDWcv |
| NEUT% | 中性粒细胞百分比、中性粒细胞比率、中性粒细胞%、NEUT%、NE%、Neut% |
| NEUT# | 中性粒细胞绝对值、中性粒细胞计数、中性粒细胞#、NEUT#、NE#、Neut# |
| LYMPH% | 淋巴细胞百分比、淋巴细胞比率、淋巴细胞%、LYMPH%、LY%、LYM% |
| LYMPH# | 淋巴细胞绝对值、淋巴细胞计数、淋巴细胞#、LYMPH#、LY#、LYM# |
| MONO% | 单核细胞百分比、单核细胞%、MONO%、MO% |
| MONO# | 单核细胞绝对值、单核细胞计数、单核细胞#、MONO#、MO# |
| EO% | 嗜酸性粒细胞百分比、嗜酸细胞%、EO%、EOS%、E% |
| EO# | 嗜酸性粒细胞绝对值、嗜酸细胞计数、EO#、EOS#、E# |
| BASO% | 嗜碱性粒细胞百分比、嗜碱细胞%、BASO%、BA%、B% |
| BASO# | 嗜碱性粒细胞绝对值、嗜碱细胞计数、BASO#、BA#、B# |

## 生化 Chemistry

| std_name | 别名 / 常见写法 |
|---|---|
| ALT | 丙氨酸氨基转移酶、谷丙转氨酶、丙氨酸转氨酶、ALT、GPT、SGPT |
| AST | 天门冬氨酸氨基转移酶、谷草转氨酶、门冬氨酸氨基转移酶、AST、GOT、SGOT |
| ALP | 碱性磷酸酶、ALP、AKP、ALKP |
| GGT | γ-谷氨酰转移酶、谷氨酰转肽酶、γ-谷氨酰转肽酶、GGT、γ-GT、r-GT、GGTP |
| TBIL | 总胆红素、TBIL、TBil、T-BIL、STB、总胆 |
| DBIL | 直接胆红素、结合胆红素、DBIL、DBil、D-BIL |
| TP | 总蛋白、血清总蛋白、TP、TProtein |
| ALB | 白蛋白、清蛋白、ALB、Alb |
| GLU | 葡萄糖、血糖、空腹血糖、GLU、Glu、GLUC、FBG、FPG、血浆葡萄糖 |
| UREA | 尿素、尿素氮、血尿素氮、UREA、BUN、Urea |
| CREA | 肌酐、血肌酐、CREA、Cr、Crea、SCr |
| UA | 尿酸、血尿酸、UA、URIC |
| TC | 总胆固醇、胆固醇、CHOL、TC、TCHO、CHO |
| TG | 甘油三酯、三酰甘油、TG、TRIG |
| HDL-C | 高密度脂蛋白胆固醇、高密度脂蛋白、HDL-C、HDLC、HDL |
| LDL-C | 低密度脂蛋白胆固醇、低密度脂蛋白、LDL-C、LDLC、LDL |
| K | 钾、血钾、钾离子、K、K+、Kalium、Potassium |
| Na | 钠、血钠、钠离子、Na、Na+、Sodium |
| Cl | 氯、血氯、氯离子、Cl、Cl-、Chloride |
| Ca | 钙、血钙、总钙、钙离子、Ca、Ca2+、Calcium |
| CK | 肌酸激酶、肌酸磷酸激酶、CK、CPK、CREK |
| CK-MB | 肌酸激酶同工酶、肌酸激酶MB、CK-MB、CKMB、CK-MB质量 |
| LDH | 乳酸脱氢酶、LDH、LD |

## 凝血 Coagulation

| std_name | 别名 / 常见写法 |
|---|---|
| PT | 凝血酶原时间、PT、凝血酶原时间测定、PT-T |
| PT-INR | 国际标准化比值、INR、PT-INR、PTINR |
| APTT | 活化部分凝血活酶时间、部分凝血活酶时间、APTT、aPTT、KPTT |
| TT | 凝血酶时间、TT、凝血酶时间测定 |
| FIB | 纤维蛋白原、FIB、FBG、Fg、Fbg、纤维蛋白原含量 |
| D-Dimer | D-二聚体、D二聚体、DD、D-Dimer、DDimer、D-D |

---

## 易混淆提示（供归一时判别）

- **TC vs TBIL**：都可能简写含糊，"胆固醇"→TC，"胆红素"→TBIL，"总胆"在不同医院可能指总胆红素或总胆固醇，**遇"总胆"且无单位/无上下文时，按单位判别**（mmol/L→TC，μmol/L→TBIL），仍不确定则标 warnings。
- **CK vs CK-MB**：含"MB/同工酶"→CK-MB，否则→CK。
- **UREA / BUN**：国内"尿素"与"尿素氮(BUN)"数值口径不同（见 `unit_conversion.md`），但归一到同一 `std_name=UREA`，由单位换算环节区分口径。
- **GLU 空腹/餐后**：均归一到 GLU，可在 `context`/备注保留"空腹/餐后"信息，不拆分为不同 std_name（v1 范围）。
- **Ca 总钙 vs 离子钙**：本表"钙/总钙"归一到 Ca（总钙）；"离子钙/游离钙"不在 v1 范围 → unmatched + warnings。
