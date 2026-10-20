# 可制造 / 可装配 / 可测试（dfm）— 规则全文

横向领域 · 51 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 5，符号封装库 7，原理图 2，网表与约束 2，叠层与规则 4，分区规划 6，器件布局 4，布线 4，平面与铺铜 2，出图与制造 12，签核验证 3

## 架构与选型（architecture）

<a id="DFM-ARC-001"></a>
#### DFM-ARC-001 · 按所选 JLC 贴片档位的能力边界选型
`must` · 可信度 `high` · 适用: jlc-smt, economic-pcba · 标签: cat-feeder

**规则** 确定 Economic 还是 Standard PCBA 后，所有器件封装、引脚间距、板厚、层数、面数都必须落在该档位能力内；超出该档能力表的范围就不能用该档下单（JLC 页面没有写具体的处理方式）。

**依据** Economic 档只做单面、2/4/6 层、0.8–1.6 mm 板厚、最小 0402 / 0.40 mm 引脚间距，且回流温度更高；这些在架构阶段就决定了能否便宜地做出来。

| 参数 | 判据 | 备注 |
|---|---|---|
| `eco_min_ic_lead_pitch` | >= 0.4 mm | Economic PCBA；Standard 为 0.35 mm |
| `eco_min_bga_ball_pitch` | >= 0.5 mm | Economic；Standard 为 0.30 mm |
| `eco_pcb_thickness` | 0.8 … 1.6 mm | Economic PCBA 板厚范围 |
| `eco_order_quantity` | 2 … 50 pcs | Economic PCBA 订单数量 |
| `eco_reflow_peak` | == 255 °C | 能力页「Reflow temperature」一行：Economic 255 ±5 °C 且不可调，Standard 240 ±5 °C；页面没有说这是峰值还是炉温设定 |

**验证**
- `bom_check`（partial）· 自写脚本读 BOM + 板文件 + JLC 能力表 — 逐个器件取封装最小尺寸与引脚间距，对照所选档位的下限；检查板厚、层数、是否单面贴片；任一不满足即失败
- `review`（manual）· JLC 在线 SMT 下单页（上传 BOM/CPL 后的匹配与报价页） — 下单前确认报价页显示的档位与预期一致，没有被自动升级为 Standard

**来源分歧** JLC 自己的页面数字不一致：设计规则博客《Mastering PCB Design Rules》（页面标 2026-10-16 更新）写 Standard PCBA 最小器件 0201、最小 BGA 间距 0.35 mm，能力页与 FAQ 写 01005 和 0.30 mm（能力页）。这里取能力页。能力页的 Reflow temperature 行没有说是峰值，DFM-ARC-004 按 260 °C 保守处理。

**来源**
- [JLCPCB PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) — JLCPCB, vendor_guide, Economic vs Standard PCBA feature table; PCB Specs for Economic PCB Assembly

<a id="DFM-ARC-004"></a>
#### DFM-ARC-004 · 器件必须耐受 JLC 回流峰值并核对 MSL
`must` · 可信度 `medium` · 适用: jlc-smt, reflow · 标签: cat-feeder

**规则** 选型时确认每个器件的数据手册允许的回流峰值不低于所选档位的峰值（Economic 255 ±5 °C，即按 260 °C 考虑），并读出 MSL 等级；MSL 3 及以上的器件（例如 LED；模块以其数据手册的 MSL 为准）要选 JLC 的 Component Baking 服务或在 PCBA 备注里写明烘烤要求。

**依据** 回流峰值过高会损坏电解电容、连接器、塑料件和 LED；吸潮的器件在回流时蒸汽膨胀会开裂（popcorn）。JLC 存储并追踪暴露时间，但需要设计者说明特殊要求。

| 参数 | 判据 | 备注 |
|---|---|---|
| `part_max_reflow_temp` | >= 260 °C | 由能力页 Economic「Reflow temperature 255 ±5 °C」推出的上界（页面没有说它是峰值，这里按峰值保守处理）；以器件数据手册的 J-STD-020 Tp 为准 |
| `msl3_floor_life` | == 168 h | MSL 3 在 30 °C / 60 %RH 下的车间寿命，超过要烘烤 |

**验证**
- `bom_check`（partial）· BOM 脚本 + 数据手册表（人工录入 Tp 与 MSL） — 表中每个器件 Tp ≥ 260 °C（Economic）或 ≥ 245 °C（Standard）；MSL ≥ 3 的器件列入订单备注清单

**来源**
- [PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) — JLCPCB, vendor_guide, Placement, Reflow, and Inspection
- [Moisture Sensitivity Level (MSL) for Electronic Parts](https://jlcpcb.com/help/article/moisture-sensitivity-level-msl-for-electronic-parts) — JLCPCB, vendor_guide, §2 MSL table (MSL 3 = 168 h at 30 °C/60 %RH)
- [How to Prevent PCBA LED Failure After Soldering](https://jlcpcb.com/help/article/how-to-prevent-pcba-led-failure-after-soldering) — JLCPCB, vendor_guide, §2 Engineering note; §3.2 Component Baking (60 °C, 48 h)
- [Manufacturing Insights: Reflow Soldering Principles and Precautions](https://jlcpcb.com/help/article/reflow-soldering-principles-and-precautions) — JLCPCB, vendor_guide
- J-STD-020 / J-STD-033 (MSL classification and handling)（IPC/JEDEC J-STD-020, J-STD-033） — IPC/JEDEC, standard

<a id="DFM-ARC-002"></a>
#### DFM-ARC-002 · 优先选 JLC 基础库 / Preferred 器件
`should` · 可信度 `medium` · 适用: jlc-smt · 标签: cat-feeder

**规则** Economic 档每用一个 Extended 器件，JLC 加收一次上料费（FAQ 写每个 Extended 器件 3 美元，价格页 Economic 列写 3.07 美元）；Economic 档下 Preferred Extended 免此费。Standard 档价格页改列 Feeder Loading 1.53 美元，写明 Basic 和 Extended 都要收。能用基础库或 Preferred 的位置不要选普通 Extended。

**依据** 基础库器件常驻贴片机料站；Extended 要人工装料，所以收上料费。两个页面都没有明说按料种还是按用量计，这里按每个需要上料的料种理解，小批量时占总价比例很高。

| 参数 | 判据 | 备注 |
|---|---|---|
| `extended_part_loading_fee` | minimize USD | Economic：FAQ 写 3 美元、价格页写 3.07 美元（页面注明会随汇率浮动）；Standard：价格页 1.53 美元 Basic/Extend。计费口径（按种类还是按个数）页面未明写 |

**验证**
- `bom_check`（partial）· 自写脚本：按 LCSC 编号查 JLC 零件库类别（Basic / Preferred / Extended） — 列出所有 Extended 行并统计种类数，乘 3 USD 得上料费；同功能有 Basic / Preferred 替代时标红

**来源分歧** 上面是 jlcpcb.com（美元）的口径。国内嘉立创（jlc.com / jlc-smt.com，人民币）的页面上是「换料费」：作者 2026-10 的一次经济型报价里整盘预订前 ¥340、预订后 ¥85，与美元口径的 3 美元 / 种不是同一套计费，不要直接套用。

**来源**
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide, Basic vs extended parts
- [PCB Assembly Cost: What Does the Price Include?](https://jlcpcb.com/help/article/pcb-assembly-price) — JLCPCB, vendor_guide, Fee table: Feeder Loading; Fee Details and Explanations

<a id="DFM-ARC-003"></a>
#### DFM-ARC-003 · 下单前核对每个料号的库存与封装匹配
`should` · 可信度 `medium` · 适用: jlc-smt · 标签: cat-feeder

**规则** 每个贴片器件都要有 LCSC 编号；下单时核对该料号封装与自己的封装一致，且库存大于「片数 × 每板用量 + 损耗」；库存不足时换料而不是赌补货。

**依据** JLC 只贴 BOM 里匹配到库的零件；缺料会让订单卡在备料，或被迫改成客供料。封装不一致则贴出来对不上焊盘。

**验证**
- `bom_check`（partial）· 自写脚本调用 LCSC/JLC 零件库查询 — 对每个 LCSC 编号取库存、封装名、基础库/扩展库；库存 < 片数×用量×(1+损耗) 或封装名与 BOM Footprint 不符则失败
- `review`（manual）· JLC BOM 匹配选型页（BOM 表 + 右侧 2D/3D 放置预览） — 逐行看「C 编号匹配」、库存、用量是否满足；全部 N/N 核对完才点下一步

**来源**
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide, BOM and CPL requirements / Parts stock
- [How to Prevent PCBA LED Failure After Soldering](https://jlcpcb.com/help/article/how-to-prevent-pcba-led-failure-after-soldering) — JLCPCB, vendor_guide, §2.1 Specify accurate part numbers; §2.2 Use the JLCPCB Parts Library
- 首单 SMT 实测记录（库存与用量核对）（作者首单 JLC SMT 的实测记录（2026-10-19，未公开笔记）） — 作者实测, blog

<a id="DFM-ARC-005"></a>
#### DFM-ARC-005 · 默认按 IPC Class 2 订板，Class 3 另行评估
`consider` · 可信度 `medium` · 适用: fabrication

**规则** 消费 / 工业类产品按 IPC-6012 Class 2 下单；若需要 Class 3（孔铜更厚、环宽无破环），必须与板厂书面确认，JLC 标准产线是商业工艺而不是预认证的 Class 3 线。

**依据** Class 2 孔壁铜平均 20 µm（最薄点 18 µm），Class 3 为 25 µm（最薄 20 µm），外层环宽要求也更严；JLC 公开的平均孔铜是 18 µm，略低于 Class 2 平均值，说明不能默认等同 Class 3。

| 参数 | 判据 | 备注 |
|---|---|---|
| `class2_hole_plating_avg` | >= 20 um | IPC-6012 Class 2 孔壁铜平均 |
| `class3_hole_plating_avg` | >= 25 um | IPC-6012 Class 3 孔壁铜平均 |
| `jlc_avg_hole_plating` | == 18 um | JLC 能力页公布的平均孔铜 |

**验证**
- `review`（manual）· 订单备注 / 与板厂确认记录 — 产品需求文档写明所需 IPC 等级；高可靠项目在下单前取得板厂对 Class 3 的书面答复

**来源分歧** 二手资料对 Class 2 / 3 的外层环宽数字不一致（有写 Class 2 外层 50 µm 最小，也有写 Class 2 允许破环 90°）。这里只收孔壁铜厚度（JLC 文章与多个板厂资料一致）；环宽以 JLC 能力页数值和实际 IPC-6012 版本为准。另外 JLC 自己的口径也不一致：同一篇 IPC-6012 博客（页面标 2026-09-28）写 JLC 的镀铜指南把孔壁铜控制在 20–25 µm，而能力页写平均孔铜 18 µm；这里取能力页的 18 µm（更保守）。

**来源**
- [Understanding IPC-6012 Standards for PCB Quality](https://jlcpcb.com/blog/ipc-6012-standards) — JLCPCB, vendor_guide
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Drilling: Average hole plating
- IPC-6012 Qualification and Performance Specification for Rigid Printed Boards（IPC-6012 (class 1/2/3 definitions)） — IPC, standard

## 符号封装库（library）

<a id="DFM-LIB-002"></a>
#### DFM-LIB-002 · 两端片式元件的两个焊盘必须完全对称
`must` · 可信度 `medium` · 适用: chip-resistor, chip-capacitor, 0402, 0603 · 标签: cat-feeder

**规则** 0201–1206 等两端片式元件的封装，两个焊盘的长、宽、阻焊开口、钢网开口必须一致，且相对本体中心对称。

**依据** 焊盘不对称导致两端锡膏量和润湿面积不同，熔化先后不同，表面张力把轻小元件拉起（立碑）；元件越小越轻越敏感。

**验证**
- `geometry_script`（full）· pcbnew Python 遍历所有 2 焊盘封装 — 比较两焊盘尺寸、形状、阻焊边距、钢网边距，并检查两焊盘中心关于封装原点对称；任何差异（> 0.01 mm）报错

**来源**
- [PCB Tombstoning: Causes, Prevention & Fixes](https://jlcpcb.com/blog/pcb-tombstone) — JLCPCB, vendor_guide, Prevention rules: Pad symmetry
- [PCB Tombstoning and its Impact on PCB Assembly](https://www.sierraassembly.com/blog/tombstoning-in-pcbs-and-impact-on-pcb-assembly/) — Sierra Assembly, blog

<a id="DFM-LIB-006"></a>
#### DFM-LIB-006 · 封装必须与数据手册极性一致并有可见的 1 脚 / 极性标记
`must` · 可信度 `medium` · 适用: led, diode, polarized-capacitor, ic, module · 标签: cat-feeder

**规则** 有极性或方向的器件（LED、二极管、电解电容、IC、模块）的封装焊盘编号必须与数据手册引脚定义一致，丝印或装配层上要有贴装后仍可见的 1 脚 / 阳极 / 负极标记；不要用通用的「LED」封装。

**依据** 极性 / 封装错位是 LED 回流后失效最常见的根因；极性错误无法被 DRC 发现，只能靠库评审和放置预览。

**验证**
- `review`（manual）· 库评审 + 3D 查看器 + JLC BOM 匹配页的 2D/3D 放置预览 — 逐个有极性器件对照数据手册引脚图，确认焊盘号、丝印标记位置、3D 模型 1 脚方向，三者一致
- `geometry_script`（partial）· pcbnew Python — 每个极性封装的 F.Silkscreen / F.Fab 上存在 1 脚标记图形，且不与焊盘重叠（距焊盘 ≥ 0.15 mm）

**来源**
- [PCBA LED Not Working After Soldering: How to Prevent Failure](https://jlcpcb.com/help/article/how-to-prevent-pcba-led-failure-after-soldering) — JLCPCB, vendor_guide, §1.1 Verify Polarity and Footprint Compatibility
- [Mastering PCB Footprints: Design Best Practices](https://jlcpcb.com/blog/pcb-footprint-design-practices) — JLCPCB, vendor_guide

<a id="DFM-LIB-001"></a>
#### DFM-LIB-001 · 封装按 IPC-7351 密度等级选，默认 Nominal
`should` · 可信度 `medium` · 适用: footprint, smd

**规则** 回流量产默认用 IPC-7351 Level B（Nominal，后缀 N）；手工焊接、返修多或高可靠场合用 Level A（Most）；Level C（Least）只在板面极度紧张且有成熟工艺控制时用。courtyard 外扩按所选等级取值。

**依据** 三个等级是三套焊点圆角目标（趾、跟、侧）加三个 courtyard 外扩值，不是质量等级；盲目用 Least 会让焊盘变小、可返修性变差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `courtyard_excess_most` | == 0.5 mm | Level A / M，每边 |
| `courtyard_excess_nominal` | == 0.25 mm | Level B / N，每边；默认 |
| `courtyard_excess_least` | == 0.1 mm | Level C / L，每边 |

**验证**
- `geometry_script`（partial）· pcbnew Python：读取封装库，对每个封装计算 courtyard 到焊盘 / 本体外沿的距离 — courtyard 到最外焊盘边的距离应等于所选等级的外扩值（±0.05 mm）；封装名后缀 M/N/L 与项目约定等级一致
- `review`（manual）· 库评审清单 — 非 Nominal 等级的封装在库里注明理由

**来源**
- [PCB Land Pattern Design: IPC-7351B Footprint Standards](https://www.atlaspcb.com/blog/pcb-land-pattern-design-ipc-7351b-footprint-standards/) — AtlasPCB, vendor_guide
- [Mastering PCB Footprints: Design Best Practices](https://jlcpcb.com/blog/pcb-footprint-design-practices) — JLCPCB, vendor_guide, IPC-7351 density levels
- IPC-7351B Generic Requirements for Surface Mount Design and Land Pattern Standard（IPC-7351B） — IPC, standard

<a id="DFM-LIB-003"></a>
#### DFM-LIB-003 · QFN/SON 焊盘按 TI 的趾跟宽与间隙建立
`should` · 可信度 `high` · 适用: qfn, son, exposed-pad

**规则** QFN/SON 引脚焊盘外伸（趾）至少比封装引脚长 0.1 mm，内伸（跟）0.05 mm，宽度至少比引脚宽 0.05 mm（每边 0.025 mm）；0.5 mm 间距焊盘宽 ≤ 0.28 mm，0.4 mm 间距焊盘宽 0.2 mm；中心散热焊盘做成与封装散热焊盘等大；引脚焊盘与散热焊盘间距 ≥ 0.2 mm。

**依据** 趾端焊点圆角决定可检视性与强度；焊盘过宽或间距过小在引脚间距小时容易桥连；散热焊盘与引脚太近同样桥连。

| 参数 | 判据 | 备注 |
|---|---|---|
| `qfn_pad_toe_extension` | >= 0.1 mm | 焊盘比封装引脚长出的最小量；TI 典型值取封装本体外 0.4 mm 作为起点 |
| `qfn_pad_heel_extension` | >= 0.05 mm |  |
| `qfn_pad_width_extra` | >= 0.05 mm | 总宽度比引脚宽（每边 0.025 mm） |
| `qfn_pad_width_pitch_0p5` | <= 0.28 mm | 0.5 mm 间距；基于引脚最大宽 0.3 mm |
| `qfn_pad_width_pitch_0p4` | == 0.2 mm | 0.4 mm 间距，焊盘间隙 0.2 mm |
| `qfn_lead_to_thermal_pad_gap` | >= 0.2 mm |  |

**验证**
- `geometry_script`（partial）· pcbnew Python 读封装焊盘几何，与数据手册 / TI 推荐尺寸对表 — 对每个 QFN/SON 封装检查引脚焊盘长宽、焊盘到焊盘间隙、引脚焊盘到中心焊盘间隙，不满足上述阈值即失败

**来源**
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.3 lead pads (0.1/0.05/0.025 mm, 0.28 mm); §3.4 exposed pad (0.2 mm gap); §4.3 (0.4 mm pitch, 0.2 mm pad). 该 URL 下的 PDF 页脚标 SLUA271C（2023-12）

<a id="DFM-LIB-004"></a>
#### DFM-LIB-004 · 细间距 QFN 的阻焊开口要成组并圆角
`should` · 可信度 `high` · 适用: qfn, son, fine-pitch

**规则** QFN/SON 引脚间距 ≥ 0.65 mm 时每个焊盘单独开阻焊，开口尺寸比引脚焊盘大 0.1–0.14 mm（NSMD；TI 原文写 larger than the lead finger pad size，没有说是每边还是总量）；0.5 mm 间距时在每一侧把所有焊盘开成一个整窗，窗边到焊盘 ≤ 0.05 mm；窗口内角做圆角。优先 NSMD（铜定义）焊盘。

**依据** 铜腐蚀精度高于阻焊对位精度，NSMD 焊点几何更稳定且焊料被限制在开口内；细间距下焊盘间阻焊桥做不出来时，整窗开口比留残缺的阻焊桥更可靠。

| 参数 | 判据 | 备注 |
|---|---|---|
| `qfn_mask_opening_over_pad` | 0.1 … 0.14 mm | NSMD，引脚间距 ≥ 0.65 mm；TI 写作「比引脚焊盘大 0.1–0.14 mm」 |
| `qfn_mask_gang_clearance_pitch_0p5` | <= 0.05 mm | 0.5 mm 间距，成组开窗 |

**验证**
- `drc`（partial）· KiCad DRC：solder_mask_bridge 违规 + 自定义规则 — 对 QFN 封装启用阻焊桥检查，0.5 mm 间距器件若出现 solder_mask_bridge 违规，应改成成组开窗，而不是接受零碎阻焊桥
- `review`（manual）· 对照 TI SLUA271 Figure 3-5 评审封装 — 内角圆角、整窗开口、无阻焊残渣风险

**来源**
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.1, §3.5

<a id="DFM-LIB-005"></a>
#### DFM-LIB-005 · 通孔封装的孔径按引脚加余量并满足孔环
`should` · 可信度 `medium` · 适用: through-hole, pin-header, connector · 标签: cat-feeder

**规则** 通孔焊盘的成品孔径取引脚对角线（或直径）加 0.1–0.3 mm；金属化孔径尽量 ≥ 0.5 mm；2 层 1 oz 板的孔环建议 ≥ 0.25 mm（绝对下限 0.18 mm）。

**依据** 孔径余量过小插不进，过大焊料填充不足、手焊时也容易虚焊；孔环不足在钻孔偏移后会破环。JLC 建议 ≥ 0.5 mm 以免孔内被阻焊或锡堵。

| 参数 | 判据 | 备注 |
|---|---|---|
| `pth_hole_over_lead` | 0.1 … 0.3 mm | 成品孔径比引脚大的量 |
| `pth_recommended_min_hole` | >= 0.5 mm |  |
| `pth_annular_ring_recommended_2layer_1oz` | >= 0.25 mm |  |
| `pth_annular_ring_absolute_min_2layer_1oz` | >= 0.18 mm |  |

**验证**
- `geometry_script`（partial）· pcbnew Python 读通孔焊盘 — 孔径 ≥ 0.5 mm；(焊盘外径 − 孔径)/2 ≥ 0.25 mm；与数据手册引脚尺寸比对孔径余量在 0.1–0.3 mm
- `drc`（full）· KiCad DRC annular_width — annular_width 约束 min 0.25 mm（硬限 0.18 mm 作 error 下限）

**来源分歧** JLC 的 footprint 文章写通孔孔环建议 0.15–0.3 mm，能力页写 PTH 孔环 ≥ 0.20 mm 且 2 层 1 oz 建议 0.25 mm（下限 0.18 mm）。取能力页数值，因为它是板厂的官方能力表。

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Drilling / Annular Rings
- [Mastering PCB Footprints: Design Best Practices](https://jlcpcb.com/blog/pcb-footprint-design-practices) — JLCPCB, vendor_guide, Pads, holes, and annular rings

<a id="DFM-LIB-007"></a>
#### DFM-LIB-007 · 丝印与焊盘保持间距
`should` · 可信度 `high` · 适用: footprint, silkscreen · 标签: cat-feeder

**规则** 丝印字符 / 线条距任何焊盘边缘 ≥ 0.15 mm（板厂下限），建议 ≥ 0.25 mm；落在裸铜上的丝印会被板厂默认删除，不要依赖它。

**依据** 丝印油墨上焊盘会污染焊接面；板厂 CAM 会自动裁掉焊盘上的丝印，导致极性标记缺失。

| 参数 | 判据 | 备注 |
|---|---|---|
| `silk_to_pad_clearance_min` | >= 0.15 mm |  |
| `silk_to_pad_clearance_recommended` | >= 0.25 mm |  |

**验证**
- `drc`（full）· KiCad DRC：silk_over_copper / silk_overlap / 自定义 silk_clearance 约束 — 设置 silk_clearance min 0.15 mm（建议 0.25 mm），要求 0 个丝印压焊盘违规

**来源**
- [Technical Guidance: Character Design Specifications](https://jlcpcb.com/blog/character-design-specifications) — JLCPCB, vendor_guide
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Silkscreen (Legend)

## 原理图（schematic）

<a id="DFM-SCH-001"></a>
#### DFM-SCH-001 · 原理图符号里带 LCSC 料号字段和 DNP 标记
`should` · 可信度 `medium` · 适用: kicad, jlc-smt · 标签: cat-feeder

**规则** 每个要贴片的符号都带一个 LCSC 料号字段（如「LCSC Part

**依据** JLC BOM 需要 Comment、Designator、Footprint 和 LCSC 料号；导出工具按固定字段名读取，字段缺失会让整行匹配失败，手工改 BOM 又会和原理图漂移。

**验证**
- `bom_check`（full）· kicad-cli sch export bom 或 Python 读 .kicad_sch — 对每个未标 DNP 且封装为 SMD 的符号，LCSC 字段匹配正则 ^C[0-9]+$；DNP 符号的 exclude_from_bom 为真

**来源**
- [How To Export BOM and CPL Files From KiCad](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad) — JLCPCB, vendor_guide
- [Fabrication Toolkit (JLCPCB plugin for KiCad)](https://github.com/bennymeg/Fabrication-Toolkit) — bennymeg (GitHub), tool_doc, LCSC field names; DNP and exclusion attributes

<a id="DFM-SCH-002"></a>
#### DFM-SCH-002 · 在原理图里预留固件下载与调试入口
`should` · 可信度 `medium` · 适用: esp32-c3, programming, dft · 标签: cat-feeder

**规则** 板子上要有不拆件就能烧录和复位的入口：对 ESP32-C3 至少引出 UART0（GPIO20/GPIO21）、CHIP_EN 和下载模式用的 GPIO9，做成排针或测试焊盘；不要把这些脚固定占用或加大电容。

**依据** ESP32-C3 默认用 UART0 下载与打印日志，GPIO9 低电平 + GPIO2/GPIO8 高电平进入下载模式；GPIO9 上加大电容会意外进入下载模式；整板贴片后没有入口就只能靠 USB 或飞线。

| 参数 | 判据 | 备注 |
|---|---|---|
| `gpio9_capacitor` | qualitative | GPIO9 不要加大容量电容，否则芯片可能进入下载模式 |
| `u0txd_series_resistor` | == 499 ohm | Espressif 建议 U0TXD 串 499 Ω 抑制谐波 |

**验证**
- `review`（manual）· 原理图评审清单 — UART0 TX/RX、CHIP_EN、GPIO9、3V3、GND 都有可接触的焊盘或排针，丝印标明名称
- `erc`（partial）· KiCad ERC + 自定义检查脚本 — 检查 GPIO9 / CHIP_EN 网络上没有超过规定值的电容、CHIP_EN 不悬空

**来源分歧** Espressif 该页没有规定测试点 / 排针的物理形式，「预留下载入口」是本库根据下载引脚事实做出的推断，因此 confidence 只给 medium。

**来源**
- [ESP32-C3 Hardware Design Guidelines: Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Strapping pins, UART0, CHIP_EN

## 网表与约束（netlist）

<a id="DFM-NET-001"></a>
#### DFM-NET-001 · BOM、CPL 与 PCB 必须一一对应
`must` · 可信度 `medium` · 适用: jlc-smt · 标签: cat-feeder

**规则** 每个位号在 BOM 里恰好出现一次，且在 CPL 里有坐标；不贴的器件同时从 BOM 和 CPL 中去掉；CPL 里没有 BOM 中不存在的位号。

**依据** JLC 按 BOM 匹配零件、按 CPL 放置；两边不一致会出现缺料、无坐标或多出一行「位号未找到」，且这类错误 DRC 看不到。

**验证**
- `netlist_diff`（full）· 自写脚本：对比 .kicad_pcb 的封装集合、bom.csv、positions.csv — 三个位号集合应相等（扣除标记 DNP / 排除的）；任何一边多或少都失败；位号需大写比较

**来源**
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide, BOM and CPL requirements
- [Fabrication Toolkit (JLCPCB plugin for KiCad)](https://github.com/bennymeg/Fabrication-Toolkit) — bennymeg (GitHub), tool_doc, Exclude from BOM / Exclude from position files

<a id="DFM-NET-002"></a>
#### DFM-NET-002 · 位号不得靠大小写区分
`must` · 可信度 `high` · 适用: jlc-smt

**规则** 同一块板上 R1 与 r1 这类仅大小写不同的位号不允许存在。

**依据** JLC 生产时会把位号字母全部转成大写，大小写不同的两个位号会合并成同一个，造成漏贴或冲突。

**验证**
- `netlist_diff`（full）· Python 读网表 — 把所有位号转大写后检查是否有重复

**来源**
- [Bill of Materials (BOM) File for PCB Assembly](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly) — JLCPCB, vendor_guide

## 叠层与规则（stackup）

<a id="DFM-STK-001"></a>
#### DFM-STK-001 · DRC 的线宽线距不低于板厂能力并留余量
`must` · 可信度 `high` · 适用: 2-layer, jlc-pcb · 标签: cat-feeder

**规则** 2 层板按铜厚设置最小线宽 / 线距：1 oz 0.10 / 0.10 mm，2 oz 0.16 / 0.16 mm，2.5 oz 0.20 / 0.20 mm；4 层以上 1 oz 为 0.09 / 0.09 mm。实际设计取这些下限的 1.5 倍以上，除非必须。

**依据** 这是 JLC 的制造能力下限，不是设计目标；线宽公差 ±20%，铜越厚蚀刻侧蚀越大，下限随铜厚增加。贴着下限做良率低，且小批量板厂可能直接按 DFM 拒单。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_trace_width_2layer_1oz` | >= 0.1 mm | 同时线距 ≥ 0.10 mm |
| `min_trace_width_2layer_2oz` | >= 0.16 mm | 同时线距 ≥ 0.16 mm |
| `min_trace_width_2layer_2p5oz` | >= 0.2 mm |  |
| `min_trace_width_multilayer_1oz` | >= 0.09 mm | 4 层及以上 |
| `trace_width_tolerance` | == 20 % | JLC 公布的线宽公差 ±20% |

**验证**
- `drc`（full）· KiCad DRC，自定义规则 .kicad_dru 的 track_width 与 clearance 约束 — 把 min track width / min clearance 设为上述数值（或 1.5 倍余量），kicad-cli pcb drc 零违规

**来源分歧** JLC 博客《PCB Design Rules and Guidelines》（blog/pcb-design-rules-best-practices，页面标 2026-09-07 更新）的能力表把 1–2 层最小线宽线距写成 5 mil（0.127 mm）；能力页写 4 mil（0.10 mm）。上面第一个 design rules 来源（A Comprehensive Guide，页面标 2026-10-16）现在只写 1 oz 多层 0.09 / 0.09 mm，与能力页一致。取能力页，同时建议按 1.5 倍余量设计，这样两种说法都满足。

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Traces and Spacing
- [A Comprehensive Guide for Optimal Results (JLCPCB PCB design rules)](https://jlcpcb.com/blog/a-comprehensive-guide-for-optimal-results) — JLCPCB, vendor_guide, DFM guidance: set DRC to manufacturer capabilities
- [PCB Design Rules and Guidelines: A Complete Best Practices Guide](https://jlcpcb.com/blog/pcb-design-rules-best-practices) — JLCPCB, vendor_guide, DFM and DFA: capability table (1-2 layer column)

<a id="DFM-STK-002"></a>
#### DFM-STK-002 · 钻孔、过孔与孔环的最小值
`must` · 可信度 `high` · 适用: 2-layer, jlc-pcb, via, pth · 标签: cat-feeder

**规则** 过孔 / 钻孔至少 0.15 mm（推荐过孔钻孔 ≥ 0.2 mm），过孔焊盘直径至少比孔大 0.1 mm（推荐 0.15 mm）；金属化孔环 ≥ 0.20 mm，2 层 1 oz 板推荐 0.25 mm、绝对下限 0.18 mm；孔到孔间距过孔 ≥ 0.2 mm、焊盘孔 ≥ 0.45 mm。

**依据** 钻孔位置公差 ±0.075 mm、孔径公差 +0.13/−0.08 mm，加上对位误差，孔环不足会破环导致开路；孔距过小会钻孔断刀或孔壁崩裂。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_drill` | >= 0.15 mm | 2 层及以上；0.1 mm 需板厚 ≤ 1 mm 且 ENIG/OSP，额外加价 |
| `preferred_via_drill` | >= 0.2 mm |  |
| `via_pad_over_hole` | >= 0.1 mm | 推荐 0.15 mm |
| `pth_annular_ring` | >= 0.2 mm | 2 层 1 oz 推荐 0.25 mm，绝对下限 0.18 mm |
| `via_hole_to_hole` | >= 0.2 mm |  |
| `pad_hole_to_hole` | >= 0.45 mm |  |

**验证**
- `drc`（full）· KiCad DRC 约束 hole_size、via_diameter、annular_width、hole_to_hole — hole_size min 0.2 mm（过孔）、annular_width min 0.20–0.25 mm、hole_to_hole min 0.45 mm（焊盘孔）/ 0.2 mm（过孔），零违规

**来源分歧** JLC 博客《PCB Design Rules and Guidelines》（blog/pcb-design-rules-best-practices，页面标 2026-09-07 更新）的能力表列出 1–2 层最小过孔孔径 0.3 mm、最小孔环 0.13 mm，与能力页（2 层钻孔 0.15 mm、孔环 ≥ 0.20 mm）不同；能力页的 0.3 mm 只对应 1 层板（仅 NPTH），博客把 1 层和 2 层并成一列。取能力页的数值。另外能力页同时写「过孔焊盘比孔大 0.1 mm」（等于孔环 0.05 mm）和「PTH 孔环 ≥ 0.20 mm」，页面没有说过孔适用哪一条；用 KiCad annular_width 约束时过孔可能被误报，需要对过孔单独设规则。

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Drilling / Vias / Annular Rings
- [PCB Design Rules and Guidelines: A Complete Best Practices Guide](https://jlcpcb.com/blog/pcb-design-rules-best-practices) — JLCPCB, vendor_guide, DFM and DFA: capability table (1-2 layer column)

<a id="DFM-STK-003"></a>
#### DFM-STK-003 · 焊盘与走线、孔与走线的间距下限
`must` · 可信度 `high` · 适用: jlc-pcb · 标签: cat-feeder

**规则** SMD 焊盘到焊盘（不同网络）≥ 0.15 mm；焊盘到走线 ≥ 0.10 mm（1 oz）；过孔孔壁到走线 ≥ 0.2 mm；金属化通孔到走线 ≥ 0.28 mm（推荐 0.35 mm）；非金属化孔到走线 ≥ 0.2 mm；最小 SMD 焊盘 0.25 × 0.25 mm。

**依据** 这些是板厂 CAM 的最小蚀刻与钻孔对位余量；低于下限会短路或被工程师改线。

| 参数 | 判据 | 备注 |
|---|---|---|
| `smd_pad_to_pad` | >= 0.15 mm | 不同网络 |
| `pad_to_track_1oz` | >= 0.1 mm |  |
| `via_hole_to_track` | >= 0.2 mm |  |
| `pth_to_track` | >= 0.28 mm | 推荐 0.35 mm |
| `npth_to_track` | >= 0.2 mm |  |
| `min_smd_pad_size` | >= 0.25 mm | 0.25 × 0.25 mm |

**验证**
- `drc`（full）· KiCad DRC 约束 clearance、hole_clearance、physical_hole_clearance — 自定义规则按上述数值设置，零违规；SMD 焊盘尺寸用 pcbnew 脚本扫描最小边 ≥ 0.25 mm

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Traces and Spacing

<a id="DFM-STK-004"></a>
#### DFM-STK-004 · 阻焊桥与阻焊开口的最小值
`must` · 可信度 `high` · 适用: jlc-pcb, fine-pitch · 标签: cat-feeder

**规则** 相邻焊盘间的阻焊桥宽度 1 oz 板绿 / 红 / 黄 / 蓝 / 紫油 ≥ 0.10 mm，黑 / 白油 ≥ 0.13 mm，2 oz 板任何颜色 ≥ 0.20 mm；阻焊开口到相邻走线 ≥ 0.09 mm。桥宽做不出来的细间距焊盘改成整窗开口，不要留残缺阻焊桥。

**依据** 阻焊桥太窄在显影时会脱落，焊接时失去防桥连作用；板厂可能自动把相邻开口合并。

| 参数 | 判据 | 备注 |
|---|---|---|
| `mask_bridge_1oz_color` | >= 0.1 mm | 绿 / 红 / 黄 / 蓝 / 紫 |
| `mask_bridge_1oz_black_white` | >= 0.13 mm |  |
| `mask_bridge_2oz` | >= 0.2 mm |  |
| `mask_opening_to_trace` | >= 0.09 mm |  |

**验证**
- `drc`（full）· KiCad DRC：solder_mask_bridge 违规 + 板级阻焊最小间隙设置 — Board Setup 的 Solder mask minimum web width 设为 0.10 mm（黑白油 0.13 mm），solder_mask_bridge 违规清零，或有意识地改成整窗开口

**来源分歧** 阻焊开口扩张量：JLC 能力页写「Expansion 1:1」，footprint 博客写每边 0.05 mm，TI 对 QFN 写 NSMD 开口比焊盘大 0.1–0.14 mm（总量）。不同封装的量不同，这里只固定「桥宽 ≥ 板厂下限」，扩张量按封装逐个评审。

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Solder Mask
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.5

## 分区规划（floorplan）

<a id="DFM-FLR-002"></a>
#### DFM-FLR-002 · 按元件和板形选 V-cut 还是邮票孔拼板
`must` · 可信度 `high` · 适用: panelization, jlc-smt

**规则** V-cut 只用于直线分板、板厚 ≥ 0.6 mm、整块拼板 70×70 至 475×475 mm 的场合，连接边宽 ≥ 3 mm（板厚 ≤ 0.8 mm 时 ≥ 5 mm）；有异形边或需要空隙的板用邮票孔：板间距 1.6 或 2 mm、连接桥宽 ≥ 4 mm（带邮票孔 5 mm）、孔径 0.5–0.8 mm、孔间距 0.2–0.3 mm。Economic 贴片要求邮票孔拼板，Standard 才支持 V-cut。

**依据** V-cut 靠 25° 双面刀槽留约 1/3 板厚的残余，太薄的板无法承受；邮票孔桥宽不足分板时撕裂铜箔和阻焊。

| 参数 | 判据 | 备注 |
|---|---|---|
| `vcut_min_board_thickness` | >= 0.6 mm |  |
| `vcut_panel_min_size` | >= 70 mm | 两个方向 |
| `vcut_panel_max_size` | <= 475 mm | 横向和纵向都有 V-cut 时 |
| `vcut_connecting_edge_width` | >= 3 mm | 板厚 ≤ 0.8 mm 时 5 mm |
| `vcut_spacing_min` | >= 2 mm | 两条 V-cut 线之间，推荐 3 mm |
| `mousebite_panel_spacing` | 1.6 … 2 mm |  |
| `mousebite_tab_width` | >= 4 mm | 带邮票孔时 5 mm |
| `mousebite_hole_diameter` | 0.5 … 0.8 mm |  |
| `mousebite_hole_spacing` | 0.2 … 0.3 mm |  |

**验证**
- `review`（partial）· JLC 下单页拼板预览 + 自写检查脚本 — 按所选分板方式检查尺寸、板厚、连接边宽、孔参数是否落在上述范围；V-cut 线是否全部为直线并贯穿整块拼板

**来源**
- [Technical Guidance: V-Cut Panelization Standards](https://jlcpcb.com/blog/v-cut-panelization-standards) — JLCPCB, vendor_guide
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, V-Cut / Mouse Bite Panelization
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide, Economic vs. standard assembly

<a id="DFM-FLR-004"></a>
#### DFM-FLR-004 · 孔、槽与异形开口的制造下限
`must` · 可信度 `high` · 适用: jlc-pcb, mounting-hole, slot, cutout

**规则** 非金属化孔 ≥ 0.50 mm；金属化槽宽 2 层板 ≥ 0.5 mm、长度 ≥ 2 倍宽度；非金属化槽宽 ≥ 1.0 mm；铜到铣边 / 铣槽 ≥ 0.2 mm；非金属化槽公差 ±0.2 mm。

**依据** 低于下限的孔槽钻头 / 铣刀做不出；槽边铜靠得太近会在铣削时露铜或起翘。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_npth_diameter` | >= 0.5 mm |  |
| `min_plated_slot_width_2layer` | >= 0.5 mm |  |
| `plated_slot_length_over_width` | >= 2 x |  |
| `min_nonplated_slot_width` | >= 1.0 mm |  |
| `copper_to_routed_slot` | >= 0.2 mm |  |
| `max_drill_diameter` | <= 6.3 mm | 能力页列出的 2 层钻孔范围上限 0.15–6.3 mm |

**验证**
- `drc`（full）· KiCad DRC：hole_size、edge_clearance、copper_edge_clearance — NPTH hole_size min 0.5 mm，槽用 Edge.Cuts 或 NPTH 长圆孔绘制，槽边铜距离 ≥ 0.2 mm

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Slots and Holes / Drilling / Board Outline and Routing

<a id="DFM-FLR-001"></a>
#### DFM-FLR-001 · 为贴片预留工艺边、工装孔与 MARK 点
`should` · 可信度 `medium` · 适用: jlc-smt · 标签: cat-feeder

**规则** 需要贴片的板（尤其 Standard 档）预留 ≥ 5 mm 工艺边（可随成品交付，也可事后去掉）；工艺边上放 2–3 个不金属化的工装孔（对角、尽量远）和 1 mm 直径的 MARK 点，MARK 点圆心距板边 3.85 mm。设计里不满足时 JLC 会自行加，但最好自己放好。

**依据** 贴片线的导轨夹住板边，靠近边缘的元件会被导轨碰到而偏位或漏贴；工装孔和 MARK 点让贴片机定位。Economic 档文档写不必须，Standard 档必须。

| 参数 | 判据 | 备注 |
|---|---|---|
| `process_edge_width` | >= 5 mm |  |
| `fiducial_diameter` | == 1.0 mm | 铜点 |
| `fiducial_center_to_panel_edge` | >= 3.85 mm |  |
| `tooling_hole_diameter_capability_page` | == 2 mm | 能力页 / 工艺边页写 2 mm |
| `tooling_hole_diameter_help_article` | == 1.152 mm | 「如何添加工装孔」帮助页写 1.152 mm、不金属化、2–3 个、对角 |

**验证**
- `geometry_script`（partial）· pcbnew Python（Edge.Cuts + 封装位置） — 有工艺边时：边宽 ≥ 5 mm；2–3 个 NPTH 工装孔，位置对角；MARK 点圆心到工艺边外沿 ≥ 3.85 mm
- `review`（manual）· JLC 下单页的拼板预览 — 预览里工艺边与 MARK 点符合上述数值，没有被系统自动重加

**来源分歧** JLC 自己的文档互相矛盾（各帮助页标 2026-09-09 更新）：能力页说 Economic 档不需要边框和 MARK 点；帮助页说标准贴片必须；FAQ 又说不用自己加、JLC 会加；而 V-Cut 博客（页面标 2026-09-08）说客户自己提供 Gerber 拼板时，工装孔和 MARK 点要自己加，JLC 不会补图上没有的数据。工装孔页还写 Economic 档工装孔「是必须的」，不满足时 JLC 默认补加，与能力页对边框 / MARK 点的「不必须」口径不同。工装孔直径一处写 2 mm（能力页、工艺边页）、一处写 1.152 mm（工装孔页）。MARK 点距板边也有 3.85 mm（圆心，工艺边页 / V-Cut 博客）和 3.35 mm（含净空，边框页）两种口径。作者首单实测里，没有 MARK 点的订单无法转为 SMT。取舍：自己放 MARK 点和工艺边（不依赖系统补加），工装孔直径以最新下单页预览为准。

**来源**
- [How to Add Edge Rails and Fiducials for PCB Assembly Orders](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order) — JLCPCB, vendor_guide
- [Design Optimization: Specifications for Adding Process Edges and Positioning Holes](https://jlcpcb.com/help/article/specifications-for-adding-process-edges-and-positioning-holes) — JLCPCB, vendor_guide
- [How to add tooling holes for PCB assembly order](https://jlcpcb.com/help/article/How-to-add-tooling-holes-for-PCB-assembly-order) — JLCPCB, vendor_guide
- [PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) — JLCPCB, vendor_guide, Panelization and Delivery

<a id="DFM-FLR-003"></a>
#### DFM-FLR-003 · 高大件和应力敏感件远离分板线
`should` · 可信度 `medium` · 适用: panelization, ceramic-capacitor, v-cut

**规则** 高大元件和对应力敏感的元件（陶瓷电容、晶振、大体积 QFN）距 V-cut 线至少 2.0 mm（JLC 博客只给了 V-cut 的数值；邮票孔桥处来源没有给数，可参照执行）；铜箔距 V-cut 中心线 ≥ 0.4 mm（推荐 1.0 mm）。

**依据** 分板和夹持时板材弯曲，应力集中在分板线附近，陶瓷件会裂、焊点会拉伤。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tall_or_stress_part_to_vcut` | >= 2.0 mm |  |
| `copper_to_vcut_centerline_min` | >= 0.4 mm |  |
| `copper_to_vcut_centerline_recommended` | >= 1.0 mm |  |

**验证**
- `geometry_script`（full）· pcbnew Python — 给定 V-cut 线坐标，对所有高度 > 阈值或标记为应力敏感的封装计算本体到线的最小距离 ≥ 2.0 mm；对所有铜对象计算到线的距离 ≥ 0.4 mm

**来源**
- [Technical Guidance: V-Cut Panelization Standards](https://jlcpcb.com/blog/v-cut-panelization-standards) — JLCPCB, vendor_guide, FAQ: component keepout
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.7 Board layout considerations

<a id="DFM-FLR-005"></a>
#### DFM-FLR-005 · 外壳与安装孔的配合要吃下制造公差
`should` · 可信度 `medium` · 适用: enclosure, mounting-hole, connector · 标签: cat-feeder

**规则** 板与外壳 / 螺柱 / 连接器的配合尺寸要留出 JLC 的公差总和：外形铣边 ±0.2 mm（精密 ±0.1 mm）、V-cut ±0.4 mm、板厚 ±10%（≥ 1.0 mm）、金属化孔径 +0.13 / −0.08 mm、孔位 ±0.075 mm、非金属化槽 ±0.2 mm。

**依据** 外壳卡位、螺柱孔和连接器开口的间隙小于公差时会装不进或受力；这类问题 DRC 发现不了，只有 3D 配合检查和公差叠加能发现。

| 参数 | 判据 | 备注 |
|---|---|---|
| `outline_tolerance_routed` | == 0.2 mm | 常规铣边；精密 ±0.1 mm |
| `outline_tolerance_vcut` | == 0.4 mm |  |
| `board_thickness_tolerance` | == 10 % | 板厚 ≥ 1.0 mm；< 1.0 mm 为 ±0.1 mm |
| `pth_diameter_tolerance_plus` | == 0.13 mm |  |
| `pth_diameter_tolerance_minus` | == 0.08 mm |  |
| `hole_position_tolerance` | == 0.075 mm |  |

**验证**
- `review`（manual）· KiCad 导出 STEP + 外壳 CAD 装配检查 — 把外壳与 PCB 的配合间隙逐项和公差总和比较，最小间隙 ≥ 公差叠加（最坏情况）；带天线的模块还要满足 RF 净空要求
- `geometry_script`（partial）· pcbnew Python — 读取安装孔、边缘连接器位置，按公差上下限生成极限位置，检查与外壳模型（简化为矩形开口）的干涉

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Dimension Tolerance / Drilling / Board Thickness

<a id="DFM-FLR-006"></a>
#### DFM-FLR-006 · 元件离板边与工艺边保持足够距离
`should` · 可信度 `low` · 适用: jlc-smt · 标签: cat-feeder

**规则** 元件和 SMD 焊盘不要放进贴片线导轨会碰到的边缘带内；没有工艺边的单板，经验上按元件焊盘距板边 ≥ 3 mm 处理，MARK 点区域距板边 ≥ 3.35 mm（含其净空）。

**依据** 导轨宽度会遮挡或碰到靠边元件，造成偏位、漏贴或返工；JLC 没有公布元件到板边的数值，只给出 5 mm 工艺边和 MARK 点的距离，3 mm 是经验值。

| 参数 | 判据 | 备注 |
|---|---|---|
| `component_pad_to_board_edge` | >= 3 mm | 经验值，JLC 无公开数字；有 5 mm 工艺边时不受此限 |
| `fiducial_clearance_to_board_edge` | >= 3.35 mm | 含 MARK 点净空区，JLC 官方 |

**验证**
- `geometry_script`（full）· pcbnew Python — 对所有 SMD 焊盘计算到 Edge.Cuts 的最小距离，小于 3 mm 的列出；MARK 点净空区边到板边 ≥ 3.35 mm

**来源分歧** JLC 的能力页（未标日期）和工艺边帮助页（标 2026-09-09）都没有给出元件 / 焊盘到板边的数值；工艺边页只说工艺边不够宽时靠边元件可能撞到导轨。3 mm 不是板厂的规则，而是经验值（有 5 mm 工艺边时可放宽）。

**来源**
- [Design Optimization: Specifications for Adding Process Edges and Positioning Holes](https://jlcpcb.com/help/article/specifications-for-adding-process-edges-and-positioning-holes) — JLCPCB, vendor_guide
- [Fiducial Marks in PCB and SMT Assembly](https://jlcpcb.com/blog/fiducial-marks) — JLCPCB, vendor_guide, Edge distance
- 作者 SMT 经验：焊盘离板边 ≥ 3 mm（作者首单 JLC SMT 的实测记录（2026-10-19，未公开笔记）） — 作者实测, blog

## 器件布局（placement）

<a id="DFM-PLC-002"></a>
#### DFM-PLC-002 · 封装 courtyard 不得重叠
`must` · 可信度 `low` · 适用: kicad, smd · 标签: cat-feeder

**规则** 同一面上任意两个封装的 courtyard 不重叠；courtyard 用 IPC-7351 Nominal 的 0.25 mm 外扩（回流量产默认）。

**依据** courtyard 是装配与返修的最小净空，重叠意味着贴片机吸嘴、AOI 视角或烙铁头无法进入。

| 参数 | 判据 | 备注 |
|---|---|---|
| `courtyard_to_courtyard_gap_same_side` | qualitative | 本库取「不重叠」；Atlas 页写同面 courtyard 之间 ≥ 0.25 mm（Level N），见 conflicts，所以不把 0 当作出处数值 |

**验证**
- `drc`（full）· KiCad DRC：courtyards_overlap，kicad-cli pcb drc — courtyards_overlap 与 missing_courtyard 两类违规均为 0

**来源分歧** Atlas 页在「Courtyard Overlap Rules」里写同一面元件 courtyard 之间最小间隙 0.25 mm（Level N），而本规则取「不重叠即可，0.25 mm 外扩已含在 courtyard 内」；该页同一页还把 0.25 mm 写成每边外扩量，两处口径可能混用。没有读到 IPC-7351 原文，所以两种取法都不能算有出处的数值。元件之间的实际间距以 DFM-PLC-001 的 JLC 表为准。

**来源**
- [PCB Land Pattern Design: IPC-7351B Footprint Standards](https://www.atlaspcb.com/blog/pcb-land-pattern-design-ipc-7351b-footprint-standards/) — AtlasPCB, vendor_guide, Courtyard excess; Courtyard Overlap Rules
- [Minimum Spacing Requirements for SMD Components](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components) — JLCPCB, vendor_guide

<a id="DFM-PLC-001"></a>
#### DFM-PLC-001 · 元件间距满足 JLC 最小间距表
`should` · 可信度 `medium` · 适用: jlc-smt · 标签: cat-feeder

**规则** 相邻元件本体 / 焊盘外沿间距不小于 JLC 表：片式件之间 0.15–0.35 mm（0201–0402 之间 0.15，0603–0805 之间 0.18，到 1206 为 0.25，1206–1206 为 0.35）；片式件到 QFN 1.0 mm、到 QFP 0.5 mm、到 SOP 0.4 mm、到 SOT 0.2 mm、到 BGA 1.0 mm；IC 之间 SOP–SOP 0.5、SOT–SOT 0.4、QFN–QFN 1.0、QFP–QFP 1.25、BGA–BGA 2.0 mm。

**依据** 间距要容纳锡膏印刷与钢网开口分隔、贴片机精度、AOI 检视和手工返修的操作空间。

| 参数 | 判据 | 备注 |
|---|---|---|
| `chip_0201_0402_gap` | >= 0.15 mm |  |
| `chip_0603_0805_gap` | >= 0.18 mm |  |
| `chip_to_1206_gap` | >= 0.25 mm |  |
| `chip_1206_to_1206_gap` | >= 0.35 mm |  |
| `chip_to_sot_gap` | >= 0.2 mm |  |
| `chip_to_sop_gap` | >= 0.4 mm |  |
| `chip_to_qfp_gap` | >= 0.5 mm |  |
| `chip_to_qfn_gap` | >= 1.0 mm |  |
| `sot_to_sot_gap` | >= 0.4 mm |  |
| `sop_to_sop_gap` | >= 0.5 mm |  |
| `qfn_to_qfn_gap` | >= 1.0 mm |  |

**验证**
- `geometry_script`（partial）· pcbnew Python：按封装名分类，计算相邻封装本体矩形间的最小距离 — 对所有相邻封装对查上表，实际间距 < 表值则失败；封装分类靠封装名 / 焊盘数 / 本体尺寸判定
- `review`（manual）· JLC DFM / 下单预览 — 对 JLC 页面最新版表格核对数值（页面表格排版易错位）

**来源分歧** 该 JLC 页面的表格在抓取后被展平，行列对应关系是推断出来的；JLC 回流原理页另写「焊盘间距至少 0.3 mm 防桥连」，与片式件间 0.15 mm 的数值口径不同（前者是元件间距，后者是焊盘间距建议）。下单前以 JLC 页面实时数值和 DFM 为准。

**来源**
- [Minimum Spacing Requirements for SMD Components](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components) — JLCPCB, vendor_guide
- [Manufacturing Insights: Reflow Soldering Principles and Precautions](https://jlcpcb.com/help/article/reflow-soldering-principles-and-precautions) — JLCPCB, vendor_guide, Designer precautions: pad spacing

<a id="DFM-PLC-003"></a>
#### DFM-PLC-003 · 放置 3 个不对称的全局 MARK 点
`should` · 可信度 `high` · 适用: jlc-smt, fiducial · 标签: cat-feeder

**规则** 贴片面放至少 2 个、推荐 3 个全局 MARK 点，按 L 形不对称分布、彼此尽量远；铜点直径约 1.0 mm，阻焊开口 ≥ 2 倍铜点（约 2.0 mm），开口范围内无其它铜、走线、过孔、丝印；MARK 点到板边（含净空）≥ 3.35 mm；双面贴片时两面都要放。

**依据** 3 点不对称可以让贴片机无歧义地解出位置、旋转和板材涨缩；对称或共线则 180° 反装时无法区分；周围有铜或丝印会因反光混淆视觉相机。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fiducial_count_min` | >= 2 pcs | 强烈推荐 3 个 |
| `fiducial_copper_diameter` | == 1.0 mm |  |
| `fiducial_mask_opening_diameter` | >= 2.0 mm | 至少 2 倍铜点直径 |
| `fiducial_copper_free_diameter` | >= 2.0 mm | 与阻焊开口同大，内无其它铜 / 走线 / 过孔 / 文字 |
| `fiducial_edge_clearance` | >= 3.35 mm | 板边到 MARK 点及其净空 |

**验证**
- `geometry_script`（full）· pcbnew Python 读 MARK 点封装 — 数量 ≥ 2（推荐 3）；三点两两距离互不相同（不对称）；每个点的铜径 1.0 mm、阻焊开口 ≥ 2.0 mm；2.0 mm 圆内无其它铜 / 孔 / 丝印；到 Edge.Cuts 距离 ≥ 3.35 mm

**来源分歧** JLC 帮助页称 MARK 点「圆心距板边 ≥ 3.85 mm」（面向工艺边 / 拼板），MARK 点博客称「板边到 MARK 点含净空 ≥ 3.35 mm」。两者口径不同，一个量圆心，一个量净空边；对 1.0 mm 铜点 + 2.0 mm 净空，3.35 mm 边距对应圆心约 4.35 mm，比 3.85 mm 严。单板取更严者。

**来源**
- [Fiducial Marks in PCB and SMT Assembly](https://jlcpcb.com/blog/fiducial-marks) — JLCPCB, vendor_guide
- [How to Add Edge Rails and Fiducials for PCB Assembly Orders](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order) — JLCPCB, vendor_guide

<a id="DFM-PLC-004"></a>
#### DFM-PLC-004 · 细间距器件旁加局部 MARK 点
`consider` · 可信度 `medium` · 适用: qfp, qfn, bga, fine-pitch

**规则** 引脚间距 ≤ 0.5 mm 的 QFP / QFN / BGA，在器件焊盘区对角各放 1 个局部 MARK 点（共 2 个），尺寸可沿用全局 MARK 点。

**依据** 板材翘曲约 100 ppm 就可使远离全局 MARK 点的位置产生约 0.01 mm 量级误差，对细间距足以短路；局部 MARK 点补偿局部偏差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `local_fiducial_pitch_threshold` | <= 0.5 mm | 引脚 / 球间距小于等于此值时建议放 |
| `local_fiducial_count` | == 2 pcs | 每个器件，对角 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 对间距 ≤ 0.5 mm 的封装，检查其对角存在 2 个 MARK 点封装且距封装边 ≤ 约 10 mm

**来源**
- [Fiducial Marks in PCB and SMT Assembly](https://jlcpcb.com/blog/fiducial-marks) — JLCPCB, vendor_guide, Local fiducials

## 布线（routing）

<a id="DFM-RTE-002"></a>
#### DFM-RTE-002 · 2 层板不要在 SMD 焊盘里放开口过孔
`must` · 可信度 `medium` · 适用: 2-layer, jlc-pcb, via-in-pad · 标签: cat-feeder

**规则** 焊盘内（除 QFN 等散热焊盘内按设计放置的小孔外）不放开口过孔；确需过焊盘孔时，用环氧或铜浆填平并电镀盖帽（IPC-4761 Type VII）；JLC 能力页只写 6 层及以上默认提供，设计规则博客把 1–2 层标为不支持，所以 2 层板按不可用处理，改为从焊盘引出过孔。

**依据** 开口过孔会把焊料吸走，造成虚焊或焊点空洞；油墨塞孔对焊盘内的孔做不了，盖油过孔又不适合焊盘上的有源过孔。

**验证**
- `geometry_script`（full）· pcbnew Python — 遍历所有过孔，检查中心是否落在任一 SMD 焊盘轮廓内（除白名单：QFN 等散热焊盘）；命中则失败
- `drc`（partial）· KiCad 自定义规则：对 via 与 SMD pad 的 physical_clearance / 条件表达式 — 用条件表达式使焊盘内的过孔报错

**来源分歧** JLC 能力页写 via-in-pad（环氧 / 铜浆填充并盖帽）6 层及以上默认提供；博客《PCB Design Rules and Guidelines》（页面标 2026-09-07）的能力表把 1–2 层标为不支持。via covering 帮助页没有按层数区分，只说焊盘内的孔不能用油墨塞，可用环氧或铜浆。2 层板是否可选填平盖帽要在下单页确认，本规则保守按不可用处理。

**来源**
- [Via Covering: Tented, Untented, Plugged, Epoxy-Filled and Copper-epoxy-filled](https://jlcpcb.com/help/article/pcb-via-covering) — JLCPCB, vendor_guide, Notes: holes in pad / vias < 0.35 mm from a pad cannot be ink-plugged, use epoxy or copper
- [PCB Design Rules and Guidelines: A Complete Best Practices Guide](https://jlcpcb.com/blog/pcb-design-rules-best-practices) — JLCPCB, vendor_guide, DFM and DFA: capability table (Via-in-Pad row: 1-2 layer Not Supported)
- [Via hole protection](https://www.ncabgroup.com/blog/via-hole-protection/) — NCAB, blog
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.4.1 Thermal Pad Via Design
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Vias: via-in-pad

<a id="DFM-RTE-001"></a>
#### DFM-RTE-001 · 片式元件两端的铜连接要热平衡
`should` · 可信度 `medium` · 适用: chip-resistor, chip-capacitor, 0402, 0603 · 标签: cat-feeder

**规则** 0402/0603 等小片式元件，两个焊盘的引出走线宽度一致；不要把一个焊盘直接并入大面积铜皮（必须并入时用热焊盘 / 花焊盘），也不要只在一个焊盘上放过孔。

**依据** 一端接大铜皮而另一端接细线时，细线端先到熔点，表面张力把元件拉起（立碑）；元件越小越轻，越容易发生。

**验证**
- `geometry_script`（partial）· pcbnew Python — 对每个 2 焊盘片式封装，比较两焊盘各自连接的铜面积（走线宽度 + 直接相连的铜皮）；一端为铜皮而另一端不是且没有热焊盘的，报警；一个焊盘内有过孔而另一个没有的，报警
- `drc`（partial）· KiCad 自定义规则 zone_connection / min_resolved_spokes — 对小封装焊盘的 zone_connection 设为 thermal relief，且 min_resolved_spokes ≥ 2

**来源分歧** 与热设计冲突：大功率路径需要焊盘与铜皮实连以散热（见 thermal 库）。取舍：信号 / 小电流的片式元件用热焊盘，功率散热焊盘实连并评估立碑风险。

**来源**
- [PCB Tombstoning: Causes, Prevention & Fixes](https://jlcpcb.com/blog/pcb-tombstone) — JLCPCB, vendor_guide, Causes: thermal imbalance; Prevention: thermal relief, trace width
- [PCB Tombstoning and its Impact on PCB Assembly](https://www.sierraassembly.com/blog/tombstoning-in-pcbs-and-impact-on-pcb-assembly/) — Sierra Assembly, blog

<a id="DFM-RTE-003"></a>
#### DFM-RTE-003 · QFN 1 脚旁保留走线与过孔禁区
`should` · 可信度 `medium` · 适用: qfn

**规则** 所有 QFN 封装的 1 脚附近保留走线与过孔禁区，不要在封装下方 1 脚区域放过孔。

**依据** 部分 QFN 的 1 脚在封装底部有外露金属特征，若下方有过孔会短路；保留禁区也让更换供应商时封装更宽容。

**验证**
- `review`（manual）· 布局评审，对照 TI SLUA271 Figure 3-5 — 每个 QFN 的 1 脚区域内没有过孔与非本脚走线

**来源**
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.5 Solder Mask

<a id="DFM-RTE-004"></a>
#### DFM-RTE-004 · 过孔覆盖方式与孔径、间距要匹配
`should` · 可信度 `high` · 适用: jlc-pcb, via · 标签: cat-feeder

**规则** 盖油（tented）过孔孔径理想 ≤ 0.4 mm、最大 0.5 mm；塞孔 / 填孔过孔孔径 ≤ 0.5 mm；喷锡面的开窗（untented）过孔与其它裸铜至少 0.2 mm（更小用沉金）；离通孔焊盘不足 0.35 mm 的过孔无法油墨塞孔。

**依据** 孔太大盖不住或填不满，且板厂对此类投诉不予受理；开窗过孔离裸铜太近喷锡后会桥连。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tented_via_drill_ideal` | <= 0.4 mm |  |
| `tented_via_drill_max` | <= 0.5 mm |  |
| `plugged_or_filled_via_drill_max` | <= 0.5 mm |  |
| `untented_via_to_exposed_copper_hasl` | >= 0.2 mm |  |
| `ink_plug_via_to_th_pad_min` | >= 0.35 mm |  |

**验证**
- `drc`（full）· KiCad DRC hole_size / 自定义规则 via_diameter — 所有过孔钻孔 ≤ 0.4 mm（盖油），超过 0.5 mm 的过孔列表为零；untented 过孔到其它裸铜的距离 ≥ 0.2 mm

**来源**
- [Via Covering: Tented, Untented, Plugged, Epoxy-Filled and Copper-epoxy-filled](https://jlcpcb.com/help/article/pcb-via-covering) — JLCPCB, vendor_guide, Hole size limits; Clearances and spacing
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Vias: plugged vias

## 平面与铺铜（plane_pour）

<a id="DFM-PLN-001"></a>
#### DFM-PLN-001 · 铜皮与走线到板边、V-cut 线的距离
`must` · 可信度 `high` · 适用: jlc-pcb, zone · 标签: cat-feeder

**规则** 铜（含铺铜）距铣边 / 铣槽 ≥ 0.2 mm；距 V-cut 中心线 ≥ 0.4 mm（推荐 1.0 mm）；邮票孔拼板中非邮票孔的边同为 ≥ 0.2 mm。

**依据** 铣刀和 V-cut 刀有位置公差，铜太近会被切到露铜、翘边或短路。

| 参数 | 判据 | 备注 |
|---|---|---|
| `copper_to_routed_edge` | >= 0.2 mm |  |
| `copper_to_vcut_centerline` | >= 0.4 mm | 推荐 1.0 mm |

**验证**
- `drc`（full）· KiCad DRC：copper_edge_clearance，自定义约束 edge_clearance — 全局 Board Setup 的 Copper to edge clearance ≥ 0.2 mm（V-cut 板 ≥ 0.4 mm）；零违规

**来源**
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Board Outline and Routing; V-Cut; Mouse Bite Panelization
- [Technical Guidance: V-Cut Panelization Standards](https://jlcpcb.com/blog/v-cut-panelization-standards) — JLCPCB, vendor_guide

<a id="DFM-PLN-002"></a>
#### DFM-PLN-002 · 铺铜上的焊盘用热焊盘，散热焊盘除外
`should` · 可信度 `medium` · 适用: zone, thermal-relief, through-hole

**规则** 通孔焊盘和需要手工焊接 / 易立碑的焊盘连接铜皮时使用热焊盘（花焊盘）；承担散热的焊盘（如散热焊盘上的过孔）则实连，不用热焊盘。

**依据** 铜皮会把焊盘热量带走，造成冷焊或两端受热不均；而散热路径上用热焊盘会显著增加热阻。

**验证**
- `drc`（partial）· KiCad 自定义规则 zone_connection、thermal_spoke_width、min_resolved_spokes — 通孔焊盘、片式焊盘 zone_connection = thermal relief，至少 2 根有效辐条；散热焊盘上过孔 zone_connection = solid

**来源分歧** 焊接性（热焊盘）与散热（实连）互相冲突：JLC 建议散热焊盘用铜皮 + 过孔阵列并考虑热焊盘改善可焊性；TI 明确说散热过孔不要用热焊盘。取舍：散热过孔 / 散热焊盘实连，其余焊盘用热焊盘。

**来源**
- [A Comprehensive Guide for Optimal Results (JLCPCB PCB design rules)](https://jlcpcb.com/blog/a-comprehensive-guide-for-optimal-results) — JLCPCB, vendor_guide, Non-numeric DFM guidance: thermal pads
- [PowerPAD Thermally Enhanced Package](https://www.ti.com/lit/an/slma002h/slma002h.pdf) — Texas Instruments, app_note, §2.4 Thermal Vias

## 出图与制造（manufacturing）

<a id="DFM-MFG-001"></a>
#### DFM-MFG-001 · Gerber 输出集合完整、带 X2 属性、单位为 mm
`must` · 可信度 `high` · 适用: gerber, kicad · 标签: cat-feeder

**规则** 出图含铜层、阻焊、丝印、Edge.Cuts（板框，单独文件、闭合轮廓），贴片订单加焊膏层；开启 X2 扩展格式与网络属性，坐标用 mm 且小数位 ≥ 5（KiCad 默认 4.6）；全部文件同一原点、1:1、不镜像；用单个 zip 打包（JLCPCB 的 KiCad 9 出图指南写上传只接受 .zip 或 .rar，不接受 7z 等其他格式）；出图前重新填充所有铺铜。

**依据** Gerber 规范要求制造数据集必须有 FileFunction 与 FilePolarity 属性和独立的板框文件；层数错位、缺层、旧铺铜会直接导致板厂做错板或拒单。

| 参数 | 判据 | 备注 |
|---|---|---|
| `gerber_mm_decimals` | >= 5 digits | Ucamco 规定 mm 单位至少 5 位小数，推荐 6 位；KiCad 默认 4.6 |

**验证**
- `geometry_script`（full）· Python 解析 Gerber 文件头（或 gerbonara / pygerber） — 每个文件有 %TF.FileFunction 与 %TF.FilePolarity；存在 FileFunction=Profile 的文件且为闭合轮廓；MO 为 MM，FS 小数位 ≥ 5；所有文件原点一致；层数与板子叠层一致；zip 内无嵌套目录
- `review`（manual）· KiCad 绘图对话框设置 — 「Check zone fills before plotting」勾选；不画钻孔标记；缩放 1:1；使用 X2 格式并包含网络属性

**来源**
- [The Gerber File Format Specification, Revision 2020.09](https://www.ucamco.com/files/downloads/file_en/399/the-gerber-file-format-specification-revision-2020-09_en.pdf) — Ucamco, standard, §4.1 FS/MO; §5 attributes; §6 PCB Fabrication Data
- [How to Generate Gerber and Drill Files From KiCad 9](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9) — JLCPCB, vendor_guide

<a id="DFM-MFG-002"></a>
#### DFM-MFG-002 · 钻孔文件按 PTH / NPTH 分开并用成品孔径
`must` · 可信度 `high` · 适用: drill, kicad · 标签: cat-feeder

**规则** 钻孔文件用 Excellon，mm 单位、十进制零，原点为绝对坐标；金属化（PTH）和非金属化（NPTH）分两个文件；孔径是电镀后的成品孔径；长圆孔使用「alternate drill mode」。

**依据** Gerber 规范要求 PTH 与 NPTH 分开，钻孔图像表示成品孔径；混在一起或孔径当作钻头径，会让孔径偏小或把安装孔金属化。

**验证**
- `geometry_script`（full）· Python 解析 Excellon / 读文件名 — 存在 *-PTH.drl 与 *-NPTH.drl 两个文件；单位 METRIC；孔径集合与 .kicad_pcb 里焊盘 / 过孔的成品孔径一致

**来源**
- [How to Generate Gerber and Drill Files From KiCad 9](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9) — JLCPCB, vendor_guide, Excellon drill options
- [The Gerber File Format Specification, Revision 2020.09](https://www.ucamco.com/files/downloads/file_en/399/the-gerber-file-format-specification-revision-2020-09_en.pdf) — Ucamco, standard, §6.1.6 Drill/rout files

<a id="DFM-MFG-003"></a>
#### DFM-MFG-003 · BOM 文件格式与内容
`must` · 可信度 `medium` · 适用: jlc-smt · 标签: cat-feeder

**规则** BOM 至少含 Comment、Designator、Footprint 三列并加 LCSC Part

**依据** JLC 按这些列做零件匹配，只有匹配到的才会被贴；多余或缺失的行会让订单卡在人工确认。

**验证**
- `bom_check`（full）· 自写脚本读 bom.csv — 表头恰好含 Comment、Designator、Footprint、LCSC Part #；每行 LCSC 料号匹配 ^C[0-9]+$；位号无重复、全大写；不含 DNP 零件

**来源**
- [Bill of Materials (BOM) File for PCB Assembly](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly) — JLCPCB, vendor_guide
- [How To Export BOM and CPL Files From KiCad](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad) — JLCPCB, vendor_guide
- 作者 SMT 实测：Excel 表头行被当作一个器件（作者首单 JLC SMT 的实测记录（2026-10-19，未公开笔记）） — 作者实测, blog

<a id="DFM-MFG-004"></a>
#### DFM-MFG-004 · CPL 坐标文件的列、单位与方向
`must` · 可信度 `medium` · 适用: jlc-smt, cpl · 标签: cat-feeder

**规则** CPL 列为 Designator、Mid X、Mid Y、Layer（Top / Bottom）、Rotation；坐标单位为 mm，旋转角为度、逆时针为正；坐标原点和 Y 方向要与 JLC 一致（作者实测过：原点在板左下角、+Y 向上，KiCad 的 Y 向下需翻转）。

**依据** JLC 只规定列、单位和旋转方向，原点未明文规定；原点或 Y 方向错误会让所有元件整体偏移或镜像，而 DRC 看不出来。

**验证**
- `geometry_script`（full）· 自写脚本：由 .kicad_pcb 重新生成期望 CPL 并与 positions.csv 逐行对比 — 同一位号的 X、Y 差 ≤ 0.01 mm，旋转差 0（mod 360），层一致

**来源分歧** JLC 的 CPL 页面未规定原点与 Y 方向；这里的原点约定来自作者第一次真实 SMT 下单的实测，不是 JLC 的公开规则。

**来源**
- [Pick & Place File for PCB Assembly](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly) — JLCPCB, vendor_guide
- 作者 SMT 实测：CPL 原点与 Y 方向（作者首单 JLC SMT 的实测记录（2026-10-19，未公开笔记）） — 作者实测, blog

<a id="DFM-MFG-005"></a>
#### DFM-MFG-005 · 逐个核对 JLC 库与 KiCad 封装的旋转差
`must` · 可信度 `medium` · 适用: jlc-smt, cpl, polarized · 标签: cat-feeder

**规则** JLC 库里部分封装的零度方向与 KiCad 不同，CPL 要加按封装的旋转偏移；用 Fabrication Toolkit 的旋转表或自己的偏移表，并在 JLC BOM 匹配页的放置预览里逐一核对所有有极性 / 方向的器件（1 脚、阴极、天线端）。

**依据** 旋转错误对 DRC 不可见，贴出来的整批板都是反的；JLC 提供的预览是下单前唯一的拦截点。

| 参数 | 判据 | 备注 |
|---|---|---|
| `sot23_sot223_rotation_offset` | == 180 deg | 作者实测：JLC 库的 SOT-23（3 脚）与 SOT-223 与 KiCad 差 180°；其它封装未验证 |

**验证**
- `review`（manual）· JLC BOM 匹配页的 2D / 3D 放置预览 — 点开每个有方向的位号，对照 1 脚圆点、+/− 标记、模块天线方向，与 KiCad 3D 视图一致；发现反的就调整偏移并重新生成 CPL
- `bom_check`（partial）· 自写脚本读 CPL 与偏移表 — 每个封装类别在偏移表中有明确条目（0 也要显式写出）；没有条目的封装类别被列出供人工核对

**来源**
- [Fabrication Toolkit (JLCPCB plugin for KiCad)](https://github.com/bennymeg/Fabrication-Toolkit) — bennymeg (GitHub), tool_doc, Rotation and position corrections
- [How To Export BOM and CPL Files From KiCad](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad) — JLCPCB, vendor_guide, Apply automatic component translations
- 作者 SMT 实测：SOT-23 / SOT-223 需 +180°（作者首单 JLC SMT 的实测记录（2026-10-19，未公开笔记）） — 作者实测, blog

<a id="DFM-MFG-006"></a>
#### DFM-MFG-006 · 不贴的零件和通孔件同时移出 BOM 与 CPL
`should` · 可信度 `medium` · 适用: jlc-smt, through-hole, dnp · 标签: cat-feeder

**规则** 不让 JLC 贴的零件（DNP、排针、需要自己焊的通孔件）不放进 BOM 和 CPL；要 JLC 手工焊的通孔件在零件库里选「波峰焊 / 手工」类并接受额外费用与工期；未选用的通孔焊盘会被保护，保持开孔供后焊。

**依据** JLC 只贴匹配到的 BOM 行；通孔件手工焊要加人工费和工期，且被误当 SMD 贴会报「不可贴」异常。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hand_solder_fee_per_order` | == 3.5 USD | 手工焊人工费（FAQ），另按焊点收费约 0.0173 USD / 点，工期 +1 天 |

**验证**
- `bom_check`（full）· 自写脚本 — 原理图中 DNP / 通孔手焊标记的位号既不在 BOM 也不在 CPL 中；订单备注里列出这些位号及后续处理

**来源**
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide, Through-hole components; BOM and CPL requirements
- [PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) — JLCPCB, vendor_guide, Through-Hole and Manual Work
- [Fabrication Toolkit (JLCPCB plugin for KiCad)](https://github.com/bennymeg/Fabrication-Toolkit) — bennymeg (GitHub), tool_doc, DNP and exclusion attributes

<a id="DFM-MFG-007"></a>
#### DFM-MFG-007 · 丝印文字与线宽达到可制造下限
`should` · 可信度 `high` · 适用: silkscreen, jlc-pcb · 标签: cat-feeder

**规则** 丝印字高 ≥ 1.0 mm（高精度字体下限 0.8 mm）、线宽 ≥ 0.15 mm（推荐 ≥ 0.2 mm）、宽高比约 1:6；镂空字体笔画 ≥ 0.2 mm、字高 ≥ 1.5 mm；字符间距 ≥ 0.15 mm（推荐 ≥ 0.2 mm）。需要的位号、极性标记、板名与版本号都用这个尺寸以上。

**依据** 低于下限的笔画会模糊、断笔或丢失；极性标记一旦丢失，人工返修和目检都会出错。

| 参数 | 判据 | 备注 |
|---|---|---|
| `silk_text_height_min` | >= 1.0 mm | 高精度字体可到 0.8 mm |
| `silk_line_width_min` | >= 0.15 mm | 推荐 ≥ 0.2 mm |
| `silk_char_gap_min` | >= 0.15 mm |  |
| `silk_hollow_font_stroke_min` | >= 0.2 mm |  |

**验证**
- `drc`（full）· KiCad DRC 约束 text_height、text_thickness — text_height min 1.0 mm、text_thickness min 0.15 mm，针对 F.Silkscreen / B.Silkscreen，零违规

**来源**
- [Technical Guidance: Character Design Specifications](https://jlcpcb.com/blog/character-design-specifications) — JLCPCB, vendor_guide
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Silkscreen (Legend)

<a id="DFM-MFG-010"></a>
#### DFM-MFG-010 · 每个电源轨与关键信号至少有一个探测点
`should` · 可信度 `medium` · 适用: dft, bring-up · 标签: cat-feeder

**规则** 每个独立的电源轨和地都要有可达的测试点（理想 ≥ 2 个）；固件下载与复位涉及的 UART TX/RX、CHIP_EN、下载脚也引出到测试焊盘；关键模拟节点（例如电流检测输出）留一个探测焊盘。

**依据** 没有探测点，整板贴片后无法在不拆件的前提下定位电源、复位和烧录问题；多点电源 / 地用于检测接触与压降。

**验证**
- `netlist_diff`（full）· 自写脚本读网表 — 每个电源 / 地网络至少有 1 个（推荐 2 个）TestPoint 封装；列出没有测试点的网络
- `review`（manual）· 原理图评审 — CHIP_EN、UART0 TX/RX、GPIO9、3V3、5V、GND、电流检测输出各有测试焊盘或排针

**来源**
- [Maximizing PCB Reliability with Test Points & DFT Guide](https://jlcpcb.com/blog/pcb-test-points-and-smart-dft) — JLCPCB, vendor_guide, Coverage
- [ESP32-C3 Hardware Design Guidelines: Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, UART0; CHIP_EN

<a id="DFM-MFG-011"></a>
#### DFM-MFG-011 · 细间距或需平整焊盘的器件选 ENIG / OSP
`should` · 可信度 `low` · 适用: fine-pitch, bga, qfn · 标签: cat-feeder

**规则** 超细间距器件（JLC 博客以 0.4 mm 间距 BGA 为例）、BGA 焊盘 0.2–0.25 mm（JLC 能力页要求 ENIG），或对 MARK 点识别要求高时，表面处理选 ENIG（或 OSP）而不是喷锡；一般标准 SMT 设计用喷锡即可（JLC 博客）。本库暂以「引脚间距 ≤ 0.5 mm」作触发线，这个阈值是经验取值，JLC 和 TI 都没有给出具体的间距数字。

**依据** 喷锡表面呈球冠形、反光，锡膏印刷不均、相机识别也更难；ENIG / OSP 平整、低反光。

| 参数 | 判据 | 备注 |
|---|---|---|
| `finish_flat_pitch_threshold` | qualitative mm | 出处没有给间距阈值：JLC 博客只举 0.4 mm 间距 BGA 为例，TI §3.6 只说 OSP / ENIG 可接受、要求焊盘平整；本库经验触发线为 ≤ 0.5 mm |
| `bga_pad_requires_enig_min` | 0.2 … 0.25 mm | JLC 能力页：BGA 焊盘直径 0.2–0.25 mm 需要 ENIG |

**验证**
- `bom_check`（partial）· 自写脚本读 BOM 封装库 — 取全板最小引脚间距；≤ 0.5 mm（本库经验阈值）时核对订单表面处理为 ENIG 或 OSP；BGA 焊盘 0.2–0.25 mm 时必须是 ENIG

**来源分歧** JLC 的 Fiducial 博客（页面标 2026-09-09 更新）只说 ENIG / OSP 适合超细间距，喷锡「对大多数标准 SMT 设计可接受」，没有给间距阈值；JLC 能力页只对 BGA 焊盘 0.2–0.25 mm 给出 ENIG 要求。≤ 0.5 mm 是本库的经验线，不是出处数值。

**来源**
- [Fiducial Marks in PCB and SMT Assembly](https://jlcpcb.com/blog/fiducial-marks) — JLCPCB, vendor_guide, Surface finish
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.6 Surface Finishes
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, BGA

<a id="DFM-MFG-012"></a>
#### DFM-MFG-012 · 钢网开孔：QFN 散热焊盘开窗，细间距缩小
`should` · 可信度 `high` · 适用: qfn, son, fine-pitch, stencil

**规则** 钢网（0.100–0.150 mm，QFN 典型 0.125 mm）上，散热焊盘的锡膏覆盖约 50–70% 并开成窗格；引脚间距 ≤ 0.5 mm 的 QFN/SON 引脚开孔可缩小约 20%；开孔面积比 ≥ 0.66、宽厚比 > 1.5。JLC 不直接用客户 Gerber 出钢网，钢网由其工程师按封装库优化，有特殊锡膏量要求要写在订单备注里。

**依据** 1:1 的大散热焊盘锡量过多会使器件浮起、产生开路和大空洞；细间距开孔过大则桥连；面积比低于 0.66 的开孔脱模差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ep_paste_coverage` | 50 … 70 % | TI 推荐；JLC footprint 博客写 60–70% 缩减 |
| `stencil_thickness` | 0.1 … 0.15 mm | 0.5 mm 间距 QFN 典型 0.125 mm |
| `fine_pitch_aperture_reduction` | == 20 % | 间距 ≤ 0.5 mm 的 QFN/SON 引脚，需关注面积比 |
| `stencil_area_ratio_min` | >= 0.66 ratio | 更低需电铸（nickel formed）钢网，TI 称实验到 0.57 |
| `stencil_aspect_ratio_min` | > 1.5 ratio | 孔宽 / 钢网厚度，IPC-7525 |

**验证**
- `geometry_script`（partial）· pcbnew Python 读 F.Paste 开孔 — 对每个带散热焊盘的封装，计算 F.Paste 开孔总面积 / 散热焊盘面积，落在 50–70%；对间距 ≤ 0.5 mm 的引脚开孔，按钢网厚度算面积比 ≥ 0.66
- `review`（manual）· JLC 订单备注与 SMT 工程确认 — 特殊锡膏量或阶梯钢网需求已在订单备注写明

**来源**
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §4.2–4.4
- [How Is SMT Stencil Data Prepared for JLCPCB SMT Orders?](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders) — JLCPCB, vendor_guide
- [Mastering PCB Footprints: Design Best Practices](https://jlcpcb.com/blog/pcb-footprint-design-practices) — JLCPCB, vendor_guide, Paste and stencil

<a id="DFM-MFG-008"></a>
#### DFM-MFG-008 · 为序列号 / 二维码预留位置，不再用 JLCJLCJLCJLC
`consider` · 可信度 `medium` · 适用: jlc-pcb, silkscreen, labelling · 标签: cat-feeder

**规则** 不要在丝印层加「JLCJLCJLCJLC」来指定订单号位置；需要序列号或二维码时，选「指定位置」并在丝印层放一个等大的实心方块（二维码 5×5 / 8×8 / 10×10 mm，仅编号 2×10 mm），远离走线、孔和其它丝印；不指定则放在空白处，空间不够可能打不上。板名、版本号、日期码自己放在丝印里。

**依据** JLC 帮助页明确说订单号标记方式已变，旧的文字占位法不再适用；没有对应实心方块时，二维码 / 序列号不会出现在指定位置。

| 参数 | 判据 | 备注 |
|---|---|---|
| `qr_square_sizes` | qualitative | 5×5、8×8 或 10×10 mm，方块要与所选二维码大小一致 |
| `serial_number_square` | qualitative | 仅编号：2×10 mm 实心方块 |

**验证**
- `review`（manual）· 板文件丝印层 + JLC 下单页「指定位置」选项 — 丝印层存在尺寸匹配的实心方块；周围无走线 / 孔；丝印里有板名 + 版本号 + 日期

**来源分歧** 网上论坛和旧文章仍写用「JLCJLCJLCJLC」占位；JLC 当前帮助页明确要求不要添加。取官方帮助页。

**来源**
- [How to remove order number from your PCB?](https://jlcpcb.com/help/article/how-to-mark-on-pcb) — JLCPCB, vendor_guide

<a id="DFM-MFG-009"></a>
#### DFM-MFG-009 · 测试点的尺寸、间距与可达性
`consider` · 可信度 `medium` · 适用: test-point, ict, flying-probe · 标签: cat-feeder

**规则** 要做探针测试（飞针 / 针床）的板，信号测试点焊盘直径 ≥ 0.8 mm（推荐 1.0–1.27 mm）、电源 / 地 ≥ 1.0 mm（推荐 1.5–2.0 mm），中心距 ≥ 1.27 mm（推荐 2.54 mm），到元件本体 ≥ 0.5 mm（推荐 1.0 mm）、到高于 6.4 mm 的元件 ≥ 2.0 mm、到板边 ≥ 3.2 mm，全部放在同一面，焊盘开阻焊窗，丝印不压焊盘。

**依据** 探针需要足够的接触面积与机械余量；双面针床夹具昂贵，低于 100 mil 间距要用导向板；测试点被阻焊盖住或丝印覆盖则无法探到。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tp_pad_diameter_signal_min` | >= 0.8 mm | 推荐 1.0–1.27 mm |
| `tp_pad_diameter_power_min` | >= 1.0 mm | 推荐 1.5–2.0 mm |
| `tp_center_pitch_min` | >= 1.27 mm | 推荐 2.54 mm |
| `tp_to_component_body` | >= 0.5 mm | 推荐 1.0 mm |
| `tp_to_tall_component` | >= 2.0 mm | 元件高度 > 6.4 mm；推荐 5.0 mm |
| `tp_to_board_edge` | >= 3.2 mm | 推荐 3.8 mm |

**验证**
- `geometry_script`（full）· pcbnew Python 读测试点封装（名称含 TP） — 焊盘直径、两两中心距、到最近元件本体 / 板边距离满足上述阈值；所有测试点在同一铜层；焊盘存在阻焊开口（无阻焊覆盖）

**来源分歧** 不同来源的探针净空数字差异很大（例如到元件 0.5–1.27 mm、到板边 3.0–3.8 mm）。这里取 JLC 博客的数字，该博客的数据比较系统但是营销性质的文章；量产前以夹具厂的规格为准。

**来源**
- [Maximizing PCB Reliability with Test Points & DFT Guide](https://jlcpcb.com/blog/pcb-test-points-and-smart-dft) — JLCPCB, vendor_guide

## 签核验证（verification）

<a id="DFM-VER-001"></a>
#### DFM-VER-001 · 用板厂能力而不是 EDA 默认值跑 DRC
`must` · 可信度 `high` · 适用: kicad, jlc-pcb · 标签: cat-feeder

**规则** 把板厂能力表（线宽线距、孔径、孔环、阻焊桥、铜到边、丝印字高）写进板级设计规则 / .kicad_dru，出图前 kicad-cli pcb drc 的错误数为 0，并且「未连接」与「封装与原理图不一致」也为 0。

**依据** EDA 默认规则与板厂能力无关；通过默认 DRC 并不代表能被板厂制造。

**验证**
- `drc`（full）· kicad-cli pcb drc --format json --output drc.json board.kicad_pcb — JSON 中 violations 与 unconnected_items 均为空；加载的 .kicad_dru 含 DFM-STK-001..004 的数值

**来源**
- [A Comprehensive Guide for Optimal Results (JLCPCB PCB design rules)](https://jlcpcb.com/blog/a-comprehensive-guide-for-optimal-results) — JLCPCB, vendor_guide, Non-numeric DFM guidance
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide

<a id="DFM-VER-003"></a>
#### DFM-VER-003 · 下单前核对 CPL 与板文件的几何一致
`must` · 可信度 `medium` · 适用: jlc-smt, cpl · 标签: cat-feeder

**规则** 用脚本由板文件重算每个位号的中心坐标与旋转，对比 positions.csv；所有位号落在板框内；Top / Bottom 与封装实际所在层一致。

**依据** 坐标 / 旋转 / 层错误在 JLC 预览里只能逐个肉眼发现，脚本可全量检查；这是 CPL 生成链路上的最后一道自动防线。

**验证**
- `geometry_script`（full）· pcbnew Python + csv — 对每个位号：|X−X'| ≤ 0.01 mm、|Y−Y'| ≤ 0.01 mm、旋转一致（含偏移表）；点在 Edge.Cuts 多边形内；Layer 与封装层一致

**来源**
- [Pick & Place File for PCB Assembly](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly) — JLCPCB, vendor_guide
- [Fabrication Toolkit (JLCPCB plugin for KiCad)](https://github.com/bennymeg/Fabrication-Toolkit) — bennymeg (GitHub), tool_doc

<a id="DFM-VER-002"></a>
#### DFM-VER-002 · 用独立查看器重新读一遍出图结果
`should` · 可信度 `medium` · 适用: gerber

**规则** 在上传前用与 KiCad 无关的 Gerber 查看器（如 Ucamco 的 Reference Gerber Viewer 或 JLC 在线查看）打开最终 zip，核对层数、板框、钻孔、阻焊 / 丝印极性、各层对齐。

**依据** 生成器和 CAM 对属性、极性、单位的理解可能不同；只有独立读回才能发现层缺失、镜像或原点漂移。

**验证**
- `review`（manual）· Reference Gerber Viewer / JLC 在线 Gerber 查看 — 层数与叠层一致；板框闭合且尺寸正确；钻孔位置与焊盘重合；各层在同一坐标下叠合；丝印未压焊盘
- `geometry_script`（partial）· gerbonara / pygerber 读回并与 .kicad_pcb 比较 — 板框外接矩形与 .kicad_pcb 的 Edge.Cuts 一致（±0.01 mm）；钻孔数量与板文件一致

**来源**
- [The Gerber File Format Specification, Revision 2020.09](https://www.ucamco.com/files/downloads/file_en/399/the-gerber-file-format-specification-revision-2020-09_en.pdf) — Ucamco, standard, Introduction: Reference Gerber Viewer; §6 PCB Fabrication Data

