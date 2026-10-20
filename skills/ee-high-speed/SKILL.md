---
name: ee-high-speed
description: "Sourced best-practice rules for high-speed digital interfaces: USB, Ethernet (RMII/RGMII), DDR, LVDS, MIPI, PCIe, SPI/I2C on long wires; controlled impedance and stackup, differential-pair coupling and skew, length matching, return paths and via transitions, termination, crosstalk, SI simulation. Use for any interface faster than a few tens of MHz or with sub-ns edges. 高速数字、差分对、阻抗控制、等长、端接、串扰、USB、以太网、DDR。"
---

# 高速数字（High-speed digital）

规则库里本领域共 **52** 条（must 14 · should 35 · consider 3）。每条规则带量化参数、验证方式、来源和可信度；其中 24 条至少有一种验证方式可完全自动化，29 条的来源之间有分歧（已写明）。

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
| 架构与选型（architecture） | 5 | 需求、器件选型、降额、电源预算 |
| 原理图（schematic） | 11 | 原理图设计与绘制 |
| 网表与约束（netlist） | 4 | 网表、网络类、约束、原理图↔PCB 一致性 |
| 叠层与规则（stackup） | 3 | 叠层、阻抗、板级设计规则 |
| 分区规划（floorplan） | 2 | 分区、功能块、接口位置 |
| 器件布局（placement） | 4 | 器件布局 |
| 布线（routing） | 14 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 3 | 平面、铺铜、缝合过孔 |
| 出图与制造（manufacturing） | 1 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 5 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，14 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| HSD-ARC-002 | 架构与选型 | 按接口确定差分/单端目标阻抗与公差 | 每个高速接口在立项时写明目标阻抗和公差并记入设计约束：USB2 90 Ω 差分，USB3 SuperSpeed 90 Ω 差分，PCIe 100 Ω 差分（8/10 层板可取 85 Ω），以太网 MDI 100 Ω 差… |
| HSD-MFG-001 | 出图与制造 | 下单时声明阻抗控制层、目标值、公差和叠层 | 需要阻抗控制的板，下单时在板厂选项中打开阻抗控制，选定板厂叠层（如 JLCPCB 的 JLC7628/JLC3313），在制板说明里写明受控线所在层、目标阻抗（单端/差分）和公差；板厂标准公差 ±10%，±5% 需特殊… |
| HSD-NET-001 | 网表与约束 | 差分对网络按同基名加 P/N 或 +/- 后缀命名 | 每对差分信号的两个网络使用相同的基名加一对成对后缀：_P/_N 或 +/-（如 USB_P/USB_N、USB+/USB-），同一对不得混用两种后缀风格（USB+ 与 USB_N 不构成一对）；在原理图里命名，PCB… |
| HSD-RTE-002 | 布线 | 按接口限定差分对内偏斜 | 差分对 P/N 的长度差不得超过接口限值：USB2 ≤ 50 mil（TI SoC；集线器 TUSB 为 ≤ 150 mil）、USB3/PCIe/SATA/HDMI/SGMII ≤ 5 mil、以太网 MDI 100… |
| HSD-RTE-005 | 布线 | 高速线全程走在连续参考面上，远离参考面边缘和空洞 | 高速线下的 GND 参考面必须连续：不跨分割、不跨空洞（焊盘挖空除外）；线距参考面边缘 ≥ 90 mil，距参考面空洞 ≥ 1.5W；全程参考同一个 GND 平面。确实必须跨分割或换参考面时，在跨越点旁放缝合电容（≤… |
| HSD-RTE-012 | 布线 | DDR3 地址/命令/控制线 fly-by 走线规则 | DDR3 地址/命令/控制按 fly-by：50 Ω（±5%）单端；所有网络沿同一路径依次经过各 SDRAM 再到 VTT 终端；各网络在同一路径上与时钟的长度差 ±20 mil 以内；每个匹配段的过孔数相同；到每个… |
| HSD-RTE-013 | 布线 | DDR3 数据、DQS 与时钟对的匹配和过孔规则 | DDR3 数据线按字节通道布线：单端 50 Ω ±5%，同一通道内所有网络在同一层、过孔数相同（最多 2 个）、长度差 ±10 mil；DQS 差分对 100 Ω ±5%，对间长度差 ±1 mil；时钟 CK 差分对… |
| HSD-SCH-002 | 原理图 | LVDS 接收端用 100 Ω（±2%）差分端接电阻 | 每对 LVDS 在接收端跨接一个与介质差分阻抗一致的端接电阻，典型 100 Ω，精度在标称差分阻抗的 2% 以内；LVDS 接收器无内置端接时该电阻不可省。 |
| HSD-SCH-004 | 原理图 | 按协议决定是否串联隔直电容及其值和封装 | USB2 和 HDMI 数据对不加隔直电容；USB3 SuperSpeed TX 对和 PCIe TX 对必须串联隔直电容，值 0.1 µF（PCIe 允许 75–200 nF），封装 0402 优先、最大 0603，… |
| HSD-SCH-006 | 原理图 | USB-C 受电设备在 CC1、CC2 各接 5.1 kΩ 下拉 | 只做 sink（UFP）的 USB-C 接口在 CC1 和 CC2 两个引脚上各接一个 5.1 kΩ 电阻到 GND（Rd），两个引脚不要合用一个电阻；使用 CC 控制器时用手册给的内置 Rd。Rd 精度取 ±10%… |
| HSD-SCH-009 | 原理图 | DDR3 的 Vref 与 VTT 用 1% 分压并就近去耦 | DDR3 Vref（VrefCA、VrefDQ）由 VDD/2 经 1% 或更好的电阻分压得到，在每个 SDRAM 的 Vref 引脚各放 0.01 µF 与 0.1 µF（0402 或更小）并在源头放 1 个 0.1… |
| HSD-SCH-010 | 原理图 | 按总线电容和模式计算 I2C 上拉电阻窗口 | I2C 上拉电阻必须落在 Rp(min) ≤ Rp ≤ Rp(max) 的窗口内：Rp(min) = (VCC − VOL(max))/IOL，Rp(max) = tr/(0.8473 × Cb)。tr 最大值：标准模… |
| HSD-STK-001 | 叠层与规则 | 高速线紧邻完整 GND 参考面，外层微带优先 | 每个高速信号层的相邻层必须有连续的 GND 参考面（不用电源面作参考，DDR 地址/控制线若参考 VDDQ 面则需沿面分布去耦电容）。TI 推荐高速差分走外层、下方紧邻 GND，不推荐带状线；整条走线始终参考同一个面。 |
| HSD-VER-002 | 签核验证 | 出板前用自定义规则跑 DRC，并核对长度口径 | 出图前用含 HSD-NET-003 全部高速规则的 .kicad_dru 跑 kicad-cli DRC，结果中长度、偏斜、差分间距、未耦合长度、过孔数五类违规都必须为 0；同时核对长度口径：KiCad 长度调谐器（计… |

## 相关 skill

- `ee-rf`
- `ee-emc-esd`
- `ee-general-pcb`
- `ee-pcb-verify`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
