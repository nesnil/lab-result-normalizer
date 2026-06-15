# 异常标记、危急值与质控规则

阶段 5 查本表。在普通 H/L 判定（见 `reference_ranges.md`）之上，叠加**危急值识别**与**数据逻辑校验**，输出质控告警 warnings。这是本 skill 从"结构化抽取"升级为"数据治理"的核心。

## 一、flag 体系

| flag | 含义 |
|---|---|
| N | 正常（区间内） |
| H | 偏高 ↑ |
| L | 偏低 ↓ |
| HH | 危急值-高（panic high） |
| LL | 危急值-低（panic low） |
| N/A | 定性项/无区间，不判定 |

`critical = true` 当且仅当 flag ∈ {HH, LL}。危急值优先级高于普通 H/L（达到危急阈值即标 HH/LL，而非 H/L）。

## 二、危急值阈值表（基于标准单位）

> 危急值（panic value）指可能危及生命、需立即通报的结果。以下为**通用参考阈值（待核验）**，各医院危急值清单不同，部署时应替换为目标机构的危急值制度。

| std_name | 单位 | 危急-低 (≤LL) | 危急-高 (≥HH) | 说明 |
|---|---|---|---|---|
| WBC | 10^9/L | 1.5 | 30 | 粒缺/极度增高 |
| HGB | g/L | 50 | 200 | 重度贫血/红细胞增多 |
| PLT | 10^9/L | 30 | 1000 | 出血/血栓风险 |
| GLU | mmol/L | 2.5 | 22.2 | 低血糖/高血糖危象 |
| K | mmol/L | 2.8 | 6.5 | 致心律失常 |
| Na | mmol/L | 120 | 160 | 严重电解质紊乱 |
| Cl | mmol/L | 80 | 120 | — |
| Ca | mmol/L | 1.5 | 3.5 | 总钙 |
| CREA | μmol/L | — | 600 | 急性肾损伤提示 |
| TBIL | μmol/L | — | 307 | 重度黄疸（约18mg/dL） |
| PT-INR | 无量纲 | — | 5.0 | 出血高风险 |
| APTT | s | — | 100 | 出血高风险 |
| FIB | g/L | 1.0 | — | DIC/出血风险 |
| D-Dimer | mg/L FEU | — | （不设危急值，显著升高仅标 H + 提示） | |

- 表中"—"表示该侧不设危急值阈值。
- 命中危急值：flag 设 HH/LL，`critical=true`，并生成**高优先级 warning**（level=critical）："{中文名} 达危急值（{std_value}{unit}），建议立即复核与临床通报"。

## 三、逻辑一致性校验（交叉规则）

对同一份报告内的多个项目做交叉校验，发现矛盾则生成 warnings（level=warning），但**不修改原值**（治理原则：标记而非篡改）。

| 规则ID | 涉及项 | 校验逻辑 | 触发告警 |
|---|---|---|---|
| C1 | HCT, HGB | HCT(%) ≈ HGB(g/L)/10 × 3，允许 ±20% 偏差 | "HCT 与 HGB 不匹配，疑似录入/单位错误" |
| C2 | HCT, RBC, MCV | HCT(%) ≈ RBC(10^12/L) × MCV(fL) / 10，±20% | "HCT/RBC/MCV 三者不自洽" |
| C3 | NEUT%,LYMPH%,MONO%,EO%,BASO% | 五分类百分比之和应 ≈ 100%（95–105%） | "白细胞分类百分比之和偏离 100%（实为 {sum}%）" |
| C4 | NEUT#,LYMPH#,...,WBC | 各分类绝对值之和 ≈ WBC，±15% | "白细胞分类绝对值之和与 WBC 不符" |
| C5 | NEUT%, NEUT#, WBC | NEUT# ≈ WBC × NEUT%/100，±15%（对每个分类同理） | "{分类} 的百分比与绝对值不自洽" |
| C6 | DBIL, TBIL | DBIL ≤ TBIL 必须成立 | "直接胆红素 > 总胆红素，数据矛盾" |
| C7 | HDL-C, LDL-C, TC, TG | TC ≈ HDL-C + LDL-C + TG/2.2（Friedewald，TG<4.5时），±20% | "血脂四项不自洽（Friedewald 校验失败）" |
| C8 | ALB, TP | ALB ≤ TP 必须成立 | "白蛋白 > 总蛋白，数据矛盾" |
| C9 | K | K > 6.0 同时无溶血标记 | "高钾，提示排查标本溶血（假性高钾）" |
| C10 | 任意项 | std_value 为负数或明显超出生理可能范围（如 HGB>250 g/L、WBC>200） | "数值超出生理可能范围，疑似录入错误" |

- C7 仅在四项齐全且 TG < 4.5 mmol/L 时执行；否则跳过（不报错）。
- 校验需用标准单位后的 `std_value`；任一参与项缺失或未换算则跳过该规则。

## 四、数据质量 warnings 汇总（level 分级）

阶段 5 末尾汇总所有 warnings，每条含 `level / code / message / related_items`：

| level | 来源 | 示例 code |
|---|---|---|
| critical | 危急值命中 | CRITICAL_VALUE |
| warning | 逻辑冲突(C1–C10) | LOGIC_CONFLICT_C6 |
| warning | 单位无法识别/未换算 | UNIT_UNRECOGNIZED |
| info | 单位缺失按默认假设 | UNIT_ASSUMED_DEFAULT |
| info | 参考区间缺失/冲突 | REF_RANGE_CONFLICT |
| info | 项目未匹配（表外） | ITEM_UNMATCHED |
| info | LOINC 未映射(P3) | LOINC_UNMAPPED |
| info | 缺性别/年龄分层 | DEMOGRAPHIC_MISSING |

## 五、输出汇总字段（供 output_schema 使用）

报告级 metadata 须含：
- `total_items`：项目总数
- `abnormal_count`：flag ∈ {H,L,HH,LL} 的数量
- `critical_count`：critical=true 的数量
- `unmatched_count`：未匹配项数
- `warning_count` / `warnings[]`：全部告警

---

## 设计说明（PPT 可引用）

本文件体现"数据治理 ≠ 数据抽取"：抽取只回答"报告里写了什么"，治理还要回答"这些数据可信吗、能用吗"。危急值识别保障**临床安全边界**，逻辑校验（C1–C10）保障**数据自洽性**，二者共同把原始报告转为"可入库、可信赖"的高质量数据集——直接对应赛道评分点"对复杂、非规范化医疗文本的鲁棒处理能力"。
