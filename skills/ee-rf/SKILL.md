---
name: ee-rf
description: "Sourced best-practice rules for RF and antenna circuits on PCBs: 2.4 GHz module and chip/PCB antenna keep-outs, pi matching networks, controlled-impedance microstrip/CPWG, via fencing and RF grounding, shielding, TX/RX isolation, tuning and verification with a VNA or S-parameter simulation. Use for Wi-Fi/BLE/LoRa/GNSS boards, antenna clearance, 50-ohm routing. 射频、天线净空、阻抗匹配、50 欧姆走线、过孔屏蔽、VNA 调试。"
---

# 射频与天线（RF and antennas）

规则库里本领域共 **45** 条（must 7 · should 35 · consider 3）。每条规则带量化参数、验证方式、来源和可信度；其中 15 条至少有一种验证方式可完全自动化，6 条的来源之间有分歧（已写明）。

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
| 架构与选型（architecture） | 6 | 需求、器件选型、降额、电源预算 |
| 符号封装库（library） | 1 | 符号 / 封装 / 3D 库质量 |
| 原理图（schematic） | 8 | 原理图设计与绘制 |
| 网表与约束（netlist） | 1 | 网表、网络类、约束、原理图↔PCB 一致性 |
| 叠层与规则（stackup） | 3 | 叠层、阻抗、板级设计规则 |
| 分区规划（floorplan） | 6 | 分区、功能块、接口位置 |
| 器件布局（placement） | 2 | 器件布局 |
| 布线（routing） | 5 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 5 | 平面、铺铜、缝合过孔 |
| 出图与制造（manufacturing） | 1 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 7 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，7 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| RF-ARC-002 | 架构与选型 | 按法规限值选功率、天线增益与杂散抑制 | 把目标市场的法规限值当作设计输入：FCC 15.247 数字调制（2400-2483.5 MHz）传导峰值功率 <= 1 W，天线定向增益 <= 6 dBi （超出要按超出的 dB 降功率），带外任意 100 kHz… |
| RF-ARC-004 | 架构与选型 | 不要改动预认证模组的天线与匹配配置 | 使用预认证模组的主板必须保持认证时的天线配置：板载 PCB 天线按集成指南保留禁布区，不另加匹配或放大器； U.FL 变体只用 50 Ω、增益不高于认证天线的天线；更换天线类型或走线设计需重新认证（FCC 属 C2/C… |
| RF-FLR-001 | 分区规划 | 天线放板边或板角，馈点贴近板边，辐射部分悬出板外 | 带板载 PCB 天线的模组，天线部分放在底板之外（悬出板边），馈点尽量贴近板边；天线无法悬出时馈点仍贴近板边， 并把底板在天线两侧和下方挖空形成净空；不要把模组放在板中央、四周都挖空。分立 PCB 天线放在板角，与其余… |
| RF-FLR-002 | 分区规划 | 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝 | 厂商图纸规定的天线禁布区内，所有铜层都不得有地、电源、走线、过孔、焊盘、元件、安装螺丝或其他导体； 禁布区几何必须与天线数据手册一致，不得缩小。 |
| RF-PLN-001 | 平面与铺铜 | 射频区地平面整块不分割，芯片底焊盘多打过孔 | 射频 IC、匹配网络与射频走线下方的地平面连续整块（尤其第一内层/底层），不分割、不留孤岛； 射频 IC 底部接地焊盘用与参考设计相同数量的接地过孔接到地平面（ESP32-C3 芯片至少 9 个）； 匹配网络地过孔到芯… |
| RF-RTE-001 | 布线 | 射频线按 50 Ω 设计，线宽（及间隙）全程恒定 | 射频走线位于外层，50 Ω 特性阻抗，线宽恒定（CPWG 时间隙也恒定），不分支；仅天线馈点前极短一段（约 3 mm）可放宽线宽， 但线宽须与天线馈点一致；约 1 cm 以上的馈线必须按传输线（宽度 W）设计。 |
| RF-RTE-005 | 布线 | 射频线下方参考地完整，其他走线不穿越、不并行靠近 | 射频线正下方（相邻层）的地平面完整无切割，不允许任何信号线从射频线下方穿过；同层不要有高频或其他信号线紧邻并行； 射频线两侧的返回路径要宽。 |

## 相关 skill

- `ee-high-speed`
- `ee-emc-esd`
- `ee-general-pcb`
- `ee-pcb-verify`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
