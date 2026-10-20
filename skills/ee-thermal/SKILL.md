---
name: ee-thermal
description: "Sourced best-practice rules for PCB thermal design: theta-JA/JC/psi-JT and junction-temperature budgets, copper spreading for SOT-223/DPAK parts, thermal vias and exposed-pad land patterns, hot-part placement, trace temperature rise (IPC-2152), MOSFET and LDO dissipation, thermal verification. Use when a part dissipates more than a few hundred mW or temperature is a risk. 热设计、结温、散热铜皮、热过孔、温升。"
---

# 热设计（Thermal design）

规则库里本领域共 **28** 条（must 6 · should 14 · consider 8）。每条规则带量化参数、验证方式、来源和可信度；其中 10 条至少有一种验证方式可完全自动化，11 条的来源之间有分歧（已写明）。

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
| 架构与选型（architecture） | 8 | 需求、器件选型、降额、电源预算 |
| 符号封装库（library） | 1 | 符号 / 封装 / 3D 库质量 |
| 叠层与规则（stackup） | 3 | 叠层、阻抗、板级设计规则 |
| 器件布局（placement） | 2 | 器件布局 |
| 布线（routing） | 5 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 3 | 平面、铺铜、缝合过孔 |
| 出图与制造（manufacturing） | 1 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 5 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，6 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| THM-ARC-001 | 架构与选型 | 数据手册的 θJA 只对它的测试板成立 | 不要把数据手册的 θJA 直接代入自己的板子算结温；每次引用 θJA 都记下它的测试板条件（JESD51 的 1s / 2s2p、尺寸、铜厚、气流），再用实测或建模得到自己板子的有效 θJA（θJA,effective… |
| THM-ARC-002 | 架构与选型 | 在最高环境温度下算每个发热件的结温 | 对每个功耗显著的器件按 Tj = Ta,max + P × θJA,effective 计算结温，Ta,max 取外壳内最高环境（不是室温），Tj 必须低于数据手册允许的最高结温并留设计余量；数据手册的额定功率 / 电… |
| THM-ARC-003 | 架构与选型 | 线性稳压器的功耗按最坏输入电压和最大电流算 | LDO（含 AMS1117）的功耗 PD = (Vin − Vout) × Iout，取最高输入电压与最大负载电流；由 (Tj,max − Ta,max)/PD 得到允许的 θJA，大于板子能实现的 θJA 时，加铜皮… |
| THM-ARC-006 | 架构与选型 | MOSFET 导通损耗按热态 Rds(on) 算 | MOSFET 导通损耗 P = I² × Rds(on)，Rds(on) 取工作结温下、与实际栅压对应的最大值（不是 25 °C 典型值）；数据手册给出的热阻（以及与之关联的电流、功耗额定值）基于其测试板，换板后重新核… |
| THM-LIB-001 | 符号封装库 | 带裸露焊盘的封装必须有等大的散热焊盘并焊在板上 | 所有带裸露散热焊盘（QFN、SON、PowerPAD、模块底部地焊盘）的封装，PCB 上的散热焊盘做成与封装裸露焊盘等大（TQFP 类按数据手册的最大尺寸）；散热焊盘与引脚焊盘间距 ≥ 0.2 mm；该焊盘必须焊接到板… |
| THM-RTE-005 | 布线 | 散热过孔要实连到尽可能多的层，不用热焊盘 | 散热焊盘下的过孔与内层 / 底层地平面之间做完整环形连接，不使用热焊盘（花焊盘）；把过孔连到尽可能多的铜层，底层地要尽量完整；封装焊盘本身也要连到顶层的大面积地铜。 |

## 相关 skill

- `ee-power`
- `ee-dfm`
- `ee-pcb-verify`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
