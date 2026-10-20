---
name: ee-audio
description: "Sourced best-practice rules for audio circuits: codec/ADC/DAC signal chains, AC-coupling capacitor dielectric and distortion, op-amp stability with capacitive loads, ground partitioning and return currents, Class-D output filters and layout, I2S clocking, THD+N/SNR verification. Use for microphone, line-in, headphone and speaker-amplifier designs. 音频、编解码器、D 类功放、耦合电容、接地、THD+N。"
---

# 音频（Audio circuits）

规则库里本领域共 **43** 条（must 4 · should 37 · consider 2）。每条规则带量化参数、验证方式、来源和可信度；其中 8 条至少有一种验证方式可完全自动化，3 条的来源之间有分歧（已写明）。

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
| 架构与选型（architecture） | 4 | 需求、器件选型、降额、电源预算 |
| 符号封装库（library） | 1 | 符号 / 封装 / 3D 库质量 |
| 原理图（schematic） | 16 | 原理图设计与绘制 |
| 网表与约束（netlist） | 1 | 网表、网络类、约束、原理图↔PCB 一致性 |
| 叠层与规则（stackup） | 1 | 叠层、阻抗、板级设计规则 |
| 分区规划（floorplan） | 3 | 分区、功能块、接口位置 |
| 器件布局（placement） | 3 | 器件布局 |
| 布线（routing） | 5 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 2 | 平面、铺铜、缝合过孔 |
| 出图与制造（manufacturing） | 1 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 6 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，4 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| AUD-PLC-001 | 器件布局 | Class-D 去耦与自举电容紧贴引脚并控制回路电感 | 最小的去耦电容放在引脚 1 mm 以内、顶层同层，较大者紧随其后；去耦电容地端用多个过孔就近接地层；自举电容以星形接到 OUT 引脚而不是挂在粗的输出走线上，并按数据手册给的回路电感预算复核。 |
| AUD-RTE-002 | 布线 | 开关网络与其他信号在相邻层不平行重叠 | Class-D 输出、自举、Vsense（及升压 SW）这类持续开关的网络，在相邻层不得与其他信号线平行重叠，除非中间隔有完整地层；同层也要和其他信号保持距离。 |
| AUD-SCH-014 | 原理图 | 自举电容按数据手册的容量、介质和耐压选 | 每个高边自举引脚（BSxx）跨接到对应输出（OUTxx）的陶瓷电容按数据手册选值：TPA3116D2 为 220 nF、X5R 或更好、额定 ≥16 V；该电容只连这两个节点。 |
| AUD-VER-002 | 签核验证 | Class-D 扬声器输出必须差分测量，输出端不接地 | BTL Class-D 的两个输出端对地都有以 PVCC/2 为中心的共模电压，测量用差分探头或平衡输入，且测量设备的共模抑制能力要高于输出级供电的一半；负端（黑端）绝不能接地或机壳；负载使用 4-8 Ω 假负载。 |

## 相关 skill

- `ee-analog`
- `ee-power`
- `ee-emc-esd`
- `ee-general-pcb`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
