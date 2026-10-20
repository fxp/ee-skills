---
name: ee-low-power
description: "Sourced best-practice rules for low-power and battery/IoT designs: sleep-current budgets, leakage paths (pull-ups, dividers, ESD diodes, level shifters), load switches and power gating, quiescent-current regulator choice, Wi-Fi/BLE burst loads vs battery resistance, nA-level measurement. Use for battery-life, deep-sleep, leakage or brown-out questions. 低功耗、电池供电、睡眠电流预算、漏电、负载开关、掉电。"
---

# 低功耗 / 电池（Low power and battery-powered design）

规则库里本领域共 **40** 条（must 6 · should 28 · consider 6）。每条规则带量化参数、验证方式、来源和可信度；其中 10 条至少有一种验证方式可完全自动化，4 条的来源之间有分歧（已写明）。

## 怎么用

1. **定位环节**：先看下面「环节分布」，挑你正在做的环节（设计前期看 architecture / schematic，布局看 floorplan / placement，出板前看 manufacturing / verification）。
2. **查索引**：`references/rules-index.md` 一行一条（ID · 标题 · 级别 · 可信度 · 最强验证）。按环节标题或关键词 `grep`，不要整份读。
3. **读详情**：`grep -n "<规则ID>" references/rules.md` 找到位置，只读那一块（规则、依据、参数、验证、来源、来源分歧）。
4. **应用并报告**：结论里写规则 ID、级别、可信度和你看到的证据（器件位号、网络名、实测数值）。有「来源分歧」的规则要把各方观点讲出来，别只报其中一个。
5. **数值要回原文**：规则里的数字来自调研者读到的来源，审计里带数值的高可信度规则仍有约 5–10% 有瑕疵；`medium` / `low` 的数值只当参考。要把数值写成硬性门禁或 DRC 规则前，打开规则里的来源核对一次。
6. **能自动验证的交给 `ee-pcb-verify`**：规则 `verify` 里 `automatable: full` 的检查（DRC 自定义规则、pcbnew 几何、网表对比、SPICE）不要靠肉眼估，用它跑；`bench` / `review` 方式的写进待办清单。
7. 不适用就写 N/A 并说明原因，不要为了凑条数硬套规则。

## 环节分布

| 环节 | 条数 | 关注什么 |
|---|---|---|
| 架构与选型（architecture） | 13 | 需求、器件选型、降额、电源预算 |
| 符号封装库（library） | 1 | 符号 / 封装 / 3D 库质量 |
| 原理图（schematic） | 14 | 原理图设计与绘制 |
| 网表与约束（netlist） | 1 | 网表、网络类、约束、原理图↔PCB 一致性 |
| 器件布局（placement） | 1 | 器件布局 |
| 布线（routing） | 2 | 布线、过孔、回流路径 |
| 出图与制造（manufacturing） | 2 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 6 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，6 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| LPW-ARC-012 | 架构与选型 | 无线突发电流下电源内阻不能把电压拉到下限以下 | 对每个电源（电池、LDO、5 V 输入）校核 V_open − I_peak × (R_int + R_path) − ΔV_ripple ≥ V_min。ESP32-C3 要求外部电源在 3.0–3.6 V 下至少能… |
| LPW-SCH-005 | 原理图 | 掉电域的信号要隔离，防止经 I/O 二极管反向供电 | 任何会被关断或可能先于其他域掉电的器件（负载开关后的模块、外部电压域的传感器、电平转换器）不得有来自常开域的信号去驱动它的 I/O：在断电前把信号驱动到低或高阻，用串联电阻限流，或选用带 Ioff/部分掉电保护的器件。 |
| LPW-SCH-006 | 原理图 | 使能与栅极控制线在复位和深睡期间要有确定电平 | MCU GPIO 控制的负载开关 EN、LDO EN、MOSFET 栅极（包括电机驱动管）、外设供电开关，都要有外部上拉/下拉到关断电平。ESP32-C3 复位和 Deep-sleep 期间数字 GPIO（6–21）为… |
| LPW-SCH-012 | 原理图 | 一次性锂电池的反向充电电流不得超过 1 µA | 不要给一次性锂电池（Li/MnO2 纽扣电池）反向充电：Energizer CR2032 规定最大反向充电电流为 1 µA。与电池并联的任何电源路径（备份电容或超级电容、外部电源 OR-ing、经 ESD 二极管灌入的… |
| LPW-VER-003 | 签核验证 | 在真实板、真实固件、真实电压下验收睡眠电流 | 芯片数据手册的 Deep-sleep 值只适用于芯片本身（3.3 V、25 °C、RTC 定时器加 RTC 内存）。验收值必须在目标板、目标固件、目标供电电压（使板载稳压器有足够裕量）下测量，并断开调试器和串口桥后重新… |
| LPW-VER-005 | 签核验证 | 无线突发时在负载端实测电压跌落与纹波 | 在最差电池状态（低温、老化高内阻、低电量）下，用示波器在模块供电脚测 TX 突发期间的最低电压和纹波：最低电压不低于 3.0 V（ESP32-C3 下限），TX 时纹波峰值低于 80 mV（MCS7）或 120 mV（… |

## 相关 skill

- `ee-power`
- `ee-rf`
- `ee-general-pcb`
- `ee-pcb-verify`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
