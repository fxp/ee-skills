---
name: ee-dfm
description: "Sourced best-practice rules for DFM/DFA/DFT: fab limits (trace/space, drill, annular ring, mask, silkscreen), JLCPCB capabilities and quirks, panelisation, fiducials and tooling holes, pick-and-place spacing, BOM/CPL conventions and rotation offsets, stencil and via-in-pad, test points, Gerber hygiene. Use before ordering PCBs or SMT assembly. 可制造性、嘉立创 JLC、MARK 点、工艺边、贴片、BOM/CPL、测试点、出图检查。"
---

# 可制造 / 可装配 / 可测试（Manufacturability, assembly and test (JLCPCB-oriented)）

规则库里本领域共 **51** 条（must 22 · should 25 · consider 4）。每条规则带量化参数、验证方式、来源和可信度；其中 28 条至少有一种验证方式可完全自动化，20 条的来源之间有分歧（已写明）。

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
| 符号封装库（library） | 7 | 符号 / 封装 / 3D 库质量 |
| 原理图（schematic） | 2 | 原理图设计与绘制 |
| 网表与约束（netlist） | 2 | 网表、网络类、约束、原理图↔PCB 一致性 |
| 叠层与规则（stackup） | 4 | 叠层、阻抗、板级设计规则 |
| 分区规划（floorplan） | 6 | 分区、功能块、接口位置 |
| 器件布局（placement） | 4 | 器件布局 |
| 布线（routing） | 4 | 布线、过孔、回流路径 |
| 平面与铺铜（plane_pour） | 2 | 平面、铺铜、缝合过孔 |
| 出图与制造（manufacturing） | 12 | 出图、板厂 / 贴片工艺、测试点 |
| 签核验证（verification） | 3 | 签核：ERC / DRC / 仿真 / 实测 |

## 必须遵守的规则（must，22 条）

违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。

| ID | 环节 | 标题 | 规则 |
|---|---|---|---|
| DFM-ARC-001 | 架构与选型 | 按所选 JLC 贴片档位的能力边界选型 | 确定 Economic 还是 Standard PCBA 后，所有器件封装、引脚间距、板厚、层数、面数都必须落在该档位能力内；超出该档能力表的范围就不能用该档下单（JLC 页面没有写具体的处理方式）。 |
| DFM-ARC-004 | 架构与选型 | 器件必须耐受 JLC 回流峰值并核对 MSL | 选型时确认每个器件的数据手册允许的回流峰值不低于所选档位的峰值（Economic 255 ±5 °C，即按 260 °C 考虑），并读出 MSL 等级；MSL 3 及以上的器件（例如 LED；模块以其数据手册的 MSL… |
| DFM-FLR-002 | 分区规划 | 按元件和板形选 V-cut 还是邮票孔拼板 | V-cut 只用于直线分板、板厚 ≥ 0.6 mm、整块拼板 70×70 至 475×475 mm 的场合，连接边宽 ≥ 3 mm（板厚 ≤ 0.8 mm 时 ≥ 5 mm）；有异形边或需要空隙的板用邮票孔：板间距 1… |
| DFM-FLR-004 | 分区规划 | 孔、槽与异形开口的制造下限 | 非金属化孔 ≥ 0.50 mm；金属化槽宽 2 层板 ≥ 0.5 mm、长度 ≥ 2 倍宽度；非金属化槽宽 ≥ 1.0 mm；铜到铣边 / 铣槽 ≥ 0.2 mm；非金属化槽公差 ±0.2 mm。 |
| DFM-LIB-002 | 符号封装库 | 两端片式元件的两个焊盘必须完全对称 | 0201–1206 等两端片式元件的封装，两个焊盘的长、宽、阻焊开口、钢网开口必须一致，且相对本体中心对称。 |
| DFM-LIB-006 | 符号封装库 | 封装必须与数据手册极性一致并有可见的 1 脚 / 极性标记 | 有极性或方向的器件（LED、二极管、电解电容、IC、模块）的封装焊盘编号必须与数据手册引脚定义一致，丝印或装配层上要有贴装后仍可见的 1 脚 / 阳极 / 负极标记；不要用通用的「LED」封装。 |
| DFM-MFG-001 | 出图与制造 | Gerber 输出集合完整、带 X2 属性、单位为 mm | 出图含铜层、阻焊、丝印、Edge.Cuts（板框，单独文件、闭合轮廓），贴片订单加焊膏层；开启 X2 扩展格式与网络属性，坐标用 mm 且小数位 ≥ 5（KiCad 默认 4.6）；全部文件同一原点、1:1、不镜像；用… |
| DFM-MFG-002 | 出图与制造 | 钻孔文件按 PTH / NPTH 分开并用成品孔径 | 钻孔文件用 Excellon，mm 单位、十进制零，原点为绝对坐标；金属化（PTH）和非金属化（NPTH）分两个文件；孔径是电镀后的成品孔径；长圆孔使用「alternate drill mode」。 |
| DFM-MFG-003 | 出图与制造 | BOM 文件格式与内容 | BOM 至少含 Comment、Designator、Footprint 三列并加 LCSC Part |
| DFM-MFG-004 | 出图与制造 | CPL 坐标文件的列、单位与方向 | CPL 列为 Designator、Mid X、Mid Y、Layer（Top / Bottom）、Rotation；坐标单位为 mm，旋转角为度、逆时针为正；坐标原点和 Y 方向要与 JLC 一致（作者实测过：原点在… |
| DFM-MFG-005 | 出图与制造 | 逐个核对 JLC 库与 KiCad 封装的旋转差 | JLC 库里部分封装的零度方向与 KiCad 不同，CPL 要加按封装的旋转偏移；用 Fabrication Toolkit 的旋转表或自己的偏移表，并在 JLC BOM 匹配页的放置预览里逐一核对所有有极性 / 方向… |
| DFM-NET-001 | 网表与约束 | BOM、CPL 与 PCB 必须一一对应 | 每个位号在 BOM 里恰好出现一次，且在 CPL 里有坐标；不贴的器件同时从 BOM 和 CPL 中去掉；CPL 里没有 BOM 中不存在的位号。 |
| DFM-NET-002 | 网表与约束 | 位号不得靠大小写区分 | 同一块板上 R1 与 r1 这类仅大小写不同的位号不允许存在。 |
| DFM-PLC-002 | 器件布局 | 封装 courtyard 不得重叠 | 同一面上任意两个封装的 courtyard 不重叠；courtyard 用 IPC-7351 Nominal 的 0.25 mm 外扩（回流量产默认）。 |
| DFM-PLN-001 | 平面与铺铜 | 铜皮与走线到板边、V-cut 线的距离 | 铜（含铺铜）距铣边 / 铣槽 ≥ 0.2 mm；距 V-cut 中心线 ≥ 0.4 mm（推荐 1.0 mm）；邮票孔拼板中非邮票孔的边同为 ≥ 0.2 mm。 |
| DFM-RTE-002 | 布线 | 2 层板不要在 SMD 焊盘里放开口过孔 | 焊盘内（除 QFN 等散热焊盘内按设计放置的小孔外）不放开口过孔；确需过焊盘孔时，用环氧或铜浆填平并电镀盖帽（IPC-4761 Type VII）；JLC 能力页只写 6 层及以上默认提供，设计规则博客把 1–2 层标… |
| DFM-STK-001 | 叠层与规则 | DRC 的线宽线距不低于板厂能力并留余量 | 2 层板按铜厚设置最小线宽 / 线距：1 oz 0.10 / 0.10 mm，2 oz 0.16 / 0.16 mm，2.5 oz 0.20 / 0.20 mm；4 层以上 1 oz 为 0.09 / 0.09 mm。… |
| DFM-STK-002 | 叠层与规则 | 钻孔、过孔与孔环的最小值 | 过孔 / 钻孔至少 0.15 mm（推荐过孔钻孔 ≥ 0.2 mm），过孔焊盘直径至少比孔大 0.1 mm（推荐 0.15 mm）；金属化孔环 ≥ 0.20 mm，2 层 1 oz 板推荐 0.25 mm、绝对下限 0… |
| DFM-STK-003 | 叠层与规则 | 焊盘与走线、孔与走线的间距下限 | SMD 焊盘到焊盘（不同网络）≥ 0.15 mm；焊盘到走线 ≥ 0.10 mm（1 oz）；过孔孔壁到走线 ≥ 0.2 mm；金属化通孔到走线 ≥ 0.28 mm（推荐 0.35 mm）；非金属化孔到走线 ≥ 0.2… |
| DFM-STK-004 | 叠层与规则 | 阻焊桥与阻焊开口的最小值 | 相邻焊盘间的阻焊桥宽度 1 oz 板绿 / 红 / 黄 / 蓝 / 紫油 ≥ 0.10 mm，黑 / 白油 ≥ 0.13 mm，2 oz 板任何颜色 ≥ 0.20 mm；阻焊开口到相邻走线 ≥ 0.09 mm。桥宽做不… |
| DFM-VER-001 | 签核验证 | 用板厂能力而不是 EDA 默认值跑 DRC | 把板厂能力表（线宽线距、孔径、孔环、阻焊桥、铜到边、丝印字高）写进板级设计规则 / .kicad_dru，出图前 kicad-cli pcb drc 的错误数为 0，并且「未连接」与「封装与原理图不一致」也为 0。 |
| DFM-VER-003 | 签核验证 | 下单前核对 CPL 与板文件的几何一致 | 用脚本由板文件重算每个位号的中心坐标与旋转，对比 positions.csv；所有位号落在板框内；Top / Bottom 与封装实际所在层一致。 |

## 相关 skill

- `ee-general-pcb`
- `ee-thermal`
- `ee-design-review`
- `ee-pcb-verify`

## 局限

* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。
* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。
* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。
