---
name: ee-emc-esd
description: "Sourced best-practice rules for EMC/ESD/surge: loop-area and return-path control, edge-rate and clock handling, I/O filtering (ferrites, common-mode chokes), shield and chassis ground, TVS selection and placement, IEC 61000-4-2/-4/-5 immunity, motor/relay noise suppression, pre-compliance checks. Use whenever a board has external connectors, cables, motors or radios. EMC、ESD、浪涌、TVS、滤波、屏蔽、预兼容测试。"
---

# EMC / ESD / 浪涌（EMC, ESD and surge）

规则库里本领域共 **46** 条（must 9 · should 27 · consider 10）。每条规则带量化参数、验证方式、来源和可信度；其中 13 条至少有一种验证方式可完全自动化，9 条的来源之间有分歧（已写明）。

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
| 架构与选型（architecture） | 5 | 需求、器件选型、降额、电源预算 |
| 原理图（schematic） | 14 | 原理图设计与绘制 |
| 叠层与规则（stackup） | 2 | 叠层、阻抗、板级设计规则 |
| 分区规划（floorplan） | 6 | 分区、功能块、接口位置 |
| 器件布局（placement） | 4 | 器件布局 |
| 布线（routing） | 6 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 3 | 平面、铺铜、缝合过孔 |
| 签核验证（verification） | 6 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，9 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| EMC-ARC-002 | 架构与选型 | ESD 目标等级按产品标准定，不靠 IC 的 HBM/CDM | 需求里为每个用户可触及端口写明 IEC 61000-4-2 目标等级（接触/空气放电 kV）。IC 数据手册的 HBM/CDM 额定值只说明产线可制造性，不能当作整机 ESD 保护；用户可触及端口必须有板级保护器件，且… |
| EMC-FLR-003 | 分区规划 | 连接器到 TVS 之间划 ESD 入口禁布区 | 从连接器引脚到 TVS 这段是 ESD 电流和辐射最强的区域，当作禁布区：禁止布入未受保护的走线或器件，已受保护的线也不要与未受保护线并行相邻；过孔穿过的各层同理。 |
| EMC-PLC-001 | 器件布局 | TVS 紧靠连接器引脚，被保护 IC 远离 TVS | TVS 放在设计规则允许的离连接器最近处，被保护 IC 离 TVS 的距离要明显大于 TVS 离连接器的距离，使 L4（TVS 到 IC）远大于 L1（连接器到 TVS），ESD 电流被「导向」TVS。 |
| EMC-RTE-001 | 布线 | 每条快速信号下方保持连续回流路径 | 每条周期性或快边沿信号（时钟、PWM、SPI/UART、开关节点）都必须有紧贴其下方（或紧邻）的连续地回流路径，回路面积最小；两层板上让地铜或地走线紧贴信号走线。 |
| EMC-RTE-003 | 布线 | ESD 入口走线直通 TVS，无 stub、无过孔、拐角 ≤45° | 受保护线从连接器直接走到 TVS 的保护引脚，不要有分叉（stub）；连接器到 TVS 之间不换层；必须换层时先经 TVS 再过孔；拐角用圆弧，做不到则不大于 45°。 |
| EMC-RTE-004 | 布线 | TVS 地脚接同层地铺铜，紧邻过孔缝合到相邻地层 | TVS 的地脚直接接到同层地铺铜，并在紧邻地脚处打过孔与相邻地层缝合（有多个地层时尽量都连）；过孔孔径和焊盘取大；地平面在该过孔附近不得被割断；被保护 IC 的接地不依赖长的地细线。连接到大地的机壳螺丝柱尽量靠近 TV… |
| EMC-SCH-008 | 原理图 | TVS 按 VRWM、VBR、VC、IPP、电容选型 | TVS 的 VRWM 须不低于线路最大工作电压（含容差）；VBR 高于最大电源电压；在设计的 IPP 下 VC 须低于被保护器件的绝对最大值（再叠加布局电感的附加压降）；IPP 与脉冲功率须大于威胁电流；信号线的电容满… |
| EMC-SCH-009 | 原理图 | 所有用户可触及端口和电源入口都要有 ESD 路径 | 每个用户可触及的连接器引脚（USB-C 的 VBUS/CC/D±、电机、传感器口）、按键和外露导体都要有板级 ESD 路径；金属壳连接器的放电打在壳体上，壳体必须有低阻抗路径到地；主电源入口加 ESD 二极管和不小于… |
| EMC-VER-002 | 签核验证 | ESD 测试：金属壳打壳体接触放电，绝缘件打空气放电 | ESD 抗扰测试只打正常使用中人可触及的点和面；带金属壳的连接器接触放电只打壳体（不打引脚），塑料壳连接器的引脚只做空气放电；每个选定点在最敏感极性下至少 10 次单次放电，间隔初值 1 s；空气放电要覆盖到规定等级以… |

## 相关 skill

- `ee-general-pcb`
- `ee-hv-safety`
- `ee-power`
- `ee-high-speed`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
