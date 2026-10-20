---
name: ee-analog
description: "Sourced best-practice rules for precision/low-noise analog: error and noise budgets, op-amp stability, ADC drivers and anti-alias filters, reference routing, bridge/load-cell front-ends (HX711-class), shunt current sensing with Kelvin connections (INA199-class), guard rings and leakage, AGND/DGND. Use for sensor, ADC, current-sense or instrumentation circuits. 精密模拟、传感器前端、ADC、分流检流、开尔文连接、保护环、低噪声。"
---

# 精密模拟 / 传感器前端（Precision analog and sensor front-ends）

规则库里本领域共 **46** 条（must 5 · should 33 · consider 8）。每条规则带量化参数、验证方式、来源和可信度；其中 16 条至少有一种验证方式可完全自动化，9 条的来源之间有分歧（已写明）。

## 怎么用

1. **定位环节**：先看下面「环节分布」，挑你正在做的环节（设计前期看 architecture / schematic，布局看 floorplan / placement，出板前看 manufacturing / verification）。
2. **查索引**：`references/rules-index.md` 一行一条（ID · 标题 · 级别 · 可信度 · 最强验证）。按环节标题或关键词 `grep`，不要整份读。
3. **读详情**：`grep -n "<规则ID>" references/rules.md` 找到位置，只读那一块（规则、依据、参数、验证、来源、来源分歧）。
4. **应用并报告**：结论里写规则 ID、级别、可信度和你看到的证据（器件位号、网络名、实测数值）。有「来源分歧」的规则要把各方观点讲出来，别只报其中一个。
5. **数值要回原文**：规则里的数字来自调研者读到的来源。531 条规则已逐条回原文核对过一遍（约 83% 原样成立，其余已修，详见仓库 `docs/AUDIT.md`），但付费标准和部分站点没能读到原文；`medium` / `low` 的数值只当参考。要把数值写成硬性门禁或 DRC 规则前，打开规则里的来源再核对一次。
6. **能自动验证的交给 `ee-pcb-verify`**：规则 `verify` 里 `automatable: full` 的检查（DRC 自定义规则、pcbnew 几何、网表对比、SPICE）不要靠肉眼估，用它跑；`bench` / `review` 方式的写进待办清单。
7. 不适用就写 N/A 并说明原因，不要为了凑条数硬套规则。

## 环节分布

| 环节 | 条数 | 关注什么 |
|---|---|---|
| 架构与选型（architecture） | 10 | 需求、器件选型、降额、电源预算 |
| 符号封装库（library） | 1 | 符号 / 封装 / 3D 库质量 |
| 原理图（schematic） | 13 | 原理图设计与绘制 |
| 网表与约束（netlist） | 1 | 网表、网络类、约束、原理图↔PCB 一致性 |
| 叠层与规则（stackup） | 1 | 叠层、阻抗、板级设计规则 |
| 分区规划（floorplan） | 2 | 分区、功能块、接口位置 |
| 器件布局（placement） | 4 | 器件布局 |
| 布线（routing） | 5 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 3 | 平面、铺铜、缝合过孔 |
| 出图与制造（manufacturing） | 1 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 5 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，5 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| ANA-ARC-003 | 架构与选型 | 核对电流检测增益档和输出量程 | 用数据手册的型号后缀与增益对照表算满量程输出 Vout_fs = Imax * Rshunt * G，要求 Vout_fs 同时不超过放大器输出上摆幅（V+ 减最大 0.2 V）和 ADC 能保证精度的量程；型号后缀与… |
| ANA-NET-001 | 网表与约束 | 分流电阻的 sense 抽头用独立网络 | 分流电阻到电流检测放大器输入的两条 sense 线必须是独立网络（如 CS_P、CS_N），只连接分流电阻的 sense 焊盘、放大器输入引脚和必要的滤波元件；不得与大电流的源极/地/电机网络在其他位置相连。 |
| ANA-RTE-001 | 布线 | 分流电阻到放大器必须用开尔文（四线）走线 | 放大器输入引脚到分流电阻的两条走线必须直接接在分流电阻的 sense 焊盘上，大电流只经过电阻本体和粗的负载走线；任何一条 sense 线不得借道载流走线，否则两个输入引脚之间会多出一段载流铜阻。 |
| ANA-VER-003 | 签核验证 | 稳定性签核：环路增益 + 阶跃，覆盖角点条件 | 每个驱动电容负载或带反馈的运放/放大器级，在仿真中用环路增益（Aol 与 1/beta 的闭合速率、相位裕度）和小信号阶跃响应两种方式签核：相位裕度 >= 45 deg（目标 60 deg），闭合速率 20 dB/de… |
| ANA-VER-005 | 签核验证 | 实测 HX711 的 PD_SCK 时序，别触发掉电 | 用逻辑分析仪在真实固件运行（含 Wi-Fi/BLE 活动）下抓 PD_SCK：读数期间每个高电平 ≤ 50 us、低电平 ≥ 0.2 us，脉冲数只能是 25、26 或 27，每个转换周期内不得有其他数目；PD_SCK… |

## 相关 skill

- `ee-audio`
- `ee-power`
- `ee-general-pcb`
- `ee-pcb-verify`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
