# 验证待办 — 规则按验证方式分组

由 `build_docs.py` 生成。每个方法列出：本机可用的工具（来自 `verifiers.yaml`）、可完全自动化的规则（带检查说明）、可部分自动化的规则（只列 ID，检查说明在规则详情里）。下一步按方法建立检查器，每个检查器输出 `rule id → pass/fail/evidence`。

## `erc` — 原理图 ERC

full 22 · partial 21 · manual 0

可用工具：KiCad ERC (kicad-cli sch erc)（bundled）

### 可完全自动化（22）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [AUD-SCH-014](../skills/ee-audio/references/rules.md#AUD-SCH-014) | 自举电容按数据手册的容量、介质和耐压选 | must | 对每个 BSPx/BSNx 引脚，检查网络上仅有一个电容，另一端接到同通道的 OUTxx；容量/介质/额定电压与手册一致 |
| [GEN-LIB-001](../skills/ee-general-pcb/references/rules.md#GEN-LIB-001) | 符号的引脚号、名称和电气类型逐脚对照数据手册 | must | 符号检查器对该符号无错误；原理图 ERC 在 pin_to_pin、pin_not_driven 类别上无异常。 |
| [GEN-LIB-005](../skills/ee-general-pcb/references/rules.md#GEN-LIB-005) | 自动核对符号引脚与封装焊盘一致 | must | 遍历网表中每个 (位号, 引脚号)，在对应封装文件里查同号焊盘；再反向查封装里未被引用的焊盘号。 两个方向的差集都必须为空，或在白名单（NC、散热焊盘）内。 |
| [GEN-NET-003](../skills/ee-general-pcb/references/rules.md#GEN-NET-003) | 差分对的两个网络同名并用一致的 _P/_N 后缀 | must | 每个以 _P 或 + 结尾的网络都存在同基础名、同风格的 _N 或 - 网络，反之亦然；同一设计里不出现两种后缀风格混用的配对。 |
| [GEN-SCH-005](../skills/ee-general-pcb/references/rules.md#GEN-SCH-005) | 执行器驱动脚在上电和复位期间必须保持关断 | must | 对每个 MOSFET 栅极（或驱动器使能）网络：必须存在一个电阻接到源极 / 地，阻值 <= 项目设定上限（示例板取 100 kOhm）；栅极网络不得直接连到 GPIO18。 |
| [GEN-VER-001](../skills/ee-general-pcb/references/rules.md#GEN-VER-001) | ERC 零违规，例外逐条带理由，禁止整类静音 | must | 在干净检出、固定 KiCad 主版本下运行，退出码为 0；JSON 报告解析而不是正则匹配文本。 |
| [GEN-VER-008](../skills/ee-general-pcb/references/rules.md#GEN-VER-008) | 下单前按固定门禁逐项签核 | must | 门禁 1：退出码 0。 |
| [HSD-SCH-006](../skills/ee-high-speed/references/rules.md#HSD-SCH-006) | USB-C 受电设备在 CC1、CC2 各接 5.1 kΩ 下拉 | must | USB-C 连接器 A5（CC1）和 B5（CC2）各自经一个 5.1 kΩ 电阻（容差 ≤ 10%）连接到 GND 网络，两个电阻是不同的器件位号 |
| [HSD-SCH-009](../skills/ee-high-speed/references/rules.md#HSD-SCH-009) | DDR3 的 Vref 与 VTT 用 1% 分压并就近去耦 | must | 每个 Vref 引脚网络上有 0.01 µF 与 0.1 µF 电容各一，分压电阻容差 ≤ 1%；每个 VTT 引脚有 ≥ 0.1 µF；VTT 网络总电容 ≥ 10 µF |
| [GEN-LIB-007](../skills/ee-general-pcb/references/rules.md#GEN-LIB-007) | 库只有一个来源：项目内库表且纳入版本控制 | should | 解析项目 sym-lib-table 与 fp-lib-table：每个条目的 URI 必须在项目目录内（${KIPRJMOD} 展开后）且文件已被 git 跟踪； ERC 中 lib_symbol_mismatch、lib_symbol_issues、footprint_link_issues 必须为 0。 |
| [GEN-NET-001](../skills/ee-general-pcb/references/rules.md#GEN-NET-001) | 信号网络显式命名并统一命名风格 | should | 正则检查所有网络名 ^[A-Za-z0-9_+\-/]+$；属于以下集合的网络名不得以 Net-( 开头：网络类模式匹配到的网络、含测试点的网络、 固件引脚映射中的网络。ERC 的 multiple_net_names 为 0。 |
| [GEN-NET-002](../skills/ee-general-pcb/references/rules.md#GEN-NET-002) | 网络类承载约束并保证每个网络都有归属 | should | undefined_netclass（默认 Error）为 0。 |
| [GEN-NET-007](../skills/ee-general-pcb/references/rules.md#GEN-NET-007) | 排查孤立标签、单引脚网络和意外短接 | should | 引脚数为 1 的网络必须在白名单（测试点、预留）中；ERC 中 label_dangling（Error）、isolated_pin_label（KiCad 10 Warning）、global_label_dangling（KiCad 9 Warning）为 0，并启用 single_global_label。 |
| [GEN-SCH-001](../skills/ee-general-pcb/references/rules.md#GEN-SCH-001) | 按功能块组织原理图，页间只用层次标签连接 | should | hier_label_mismatch、duplicate_sheet_names（均为默认 Error）和 label_dangling 必须为 0。 |
| [GEN-SCH-002](../skills/ee-general-pcb/references/rules.md#GEN-SCH-002) | 电源轨用统一的电源符号并规范命名 | should | similar_power、similar_labels、similar_label_and_power、multiple_net_names、same_local_global_label 全部为 0（默认 Warning）。 |
| [GEN-SCH-002](../skills/ee-general-pcb/references/rules.md#GEN-SCH-002) | 电源轨用统一的电源符号并规范命名 | should | 电源轨网络名匹配 ^[+]?[0-9]+V[0-9]*$/^(VIN/VBUS/VBAT/GND)$ 等项目白名单，含小数点或非白名单的电源轨名失败。 |
| [GEN-SCH-008](../skills/ee-general-pcb/references/rules.md#GEN-SCH-008) | 未用引脚按手册处理并显式标注 | should | pin_not_connected（默认 Error）、no_connect_connected、no_connect_dangling 均为 0；每个 NC 标记都在引脚上。 |
| [GEN-SCH-011](../skills/ee-general-pcb/references/rules.md#GEN-SCH-011) | 在原理图中为电源轨和关键信号预留测试点 | should | 网表中每条电源轨网络至少有一个 TP 类元件；GND 网络至少有两个；复位 / 使能 / 烧录信号网络各至少一个。 |
| [GEN-SCH-012](../skills/ee-general-pcb/references/rules.md#GEN-SCH-012) | 全部元件完成标注，位号唯一且稳定 | should | unannotated、duplicate_reference 为 0（两者均默认 Error）。 |
| [GEN-VER-003](../skills/ee-general-pcb/references/rules.md#GEN-VER-003) | 打开默认被忽略的 ERC 检查 | should | single_global_label、footprint_filter 的严重级别不是 ignore；kicad-cli sch erc 在启用后无违规。 |
| [LPW-SCH-004](../skills/ee-low-power/references/rules.md#LPW-SCH-004) | 外部逻辑 IC 的输入不得悬空或长期处于半电平 | should | 所有逻辑 IC 的输入引脚类型必须有驱动源或显式的拉电阻；ERC 零警告 |
| [PWR-SCH-011](../skills/ee-power/references/rules.md#PWR-SCH-011) | 电机 MOSFET 栅极加下拉电阻和串联电阻 | should | 每个功率 MOSFET 的栅极网络都必须有到源极的下拉电阻，阻值在 4.7~100 kohm（来源只给 10 kohm 典型，范围为工程判断）。 |

### 可部分自动化（21）

[GEN-SCH-004](../skills/ee-general-pcb/references/rules.md#GEN-SCH-004)、[GEN-SCH-006](../skills/ee-general-pcb/references/rules.md#GEN-SCH-006)、[GEN-SCH-007](../skills/ee-general-pcb/references/rules.md#GEN-SCH-007)、[GEN-VER-001](../skills/ee-general-pcb/references/rules.md#GEN-VER-001)、[PWR-LIB-001](../skills/ee-power/references/rules.md#PWR-LIB-001)、[ANA-SCH-011](../skills/ee-analog/references/rules.md#ANA-SCH-011)、[AUD-SCH-010](../skills/ee-audio/references/rules.md#AUD-SCH-010)、[DFM-SCH-002](../skills/ee-dfm/references/rules.md#DFM-SCH-002)、[EMC-SCH-002](../skills/ee-emc-esd/references/rules.md#EMC-SCH-002)、[EMC-SCH-013](../skills/ee-emc-esd/references/rules.md#EMC-SCH-013)、[GEN-PLN-003](../skills/ee-general-pcb/references/rules.md#GEN-PLN-003)、[GEN-SCH-003](../skills/ee-general-pcb/references/rules.md#GEN-SCH-003)、[GEN-SCH-010](../skills/ee-general-pcb/references/rules.md#GEN-SCH-010)、[GEN-SCH-014](../skills/ee-general-pcb/references/rules.md#GEN-SCH-014)、[GEN-VER-002](../skills/ee-general-pcb/references/rules.md#GEN-VER-002)、[HSD-SCH-001](../skills/ee-high-speed/references/rules.md#HSD-SCH-001)、[HSD-SCH-003](../skills/ee-high-speed/references/rules.md#HSD-SCH-003)、[HSD-SCH-011](../skills/ee-high-speed/references/rules.md#HSD-SCH-011)、[LPW-SCH-003](../skills/ee-low-power/references/rules.md#LPW-SCH-003)、[RF-SCH-001](../skills/ee-rf/references/rules.md#RF-SCH-001)、[RF-SCH-003](../skills/ee-rf/references/rules.md#RF-SCH-003)

## `drc` — PCB DRC / 自定义规则

full 62 · partial 22 · manual 1

可用工具：KiCad DRC built-in checks (kicad-cli pcb drc)（bundled）；KiCad custom DRC rules (.kicad_dru, rule language v1)（bundled）；DRC fromTo() path rules (routed length between two named pads)（bundled）；DRC proximity via helper rule areas + assertion (placement 'within N mm of pin')（bundled）

### 可完全自动化（62）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [DFM-FLR-004](../skills/ee-dfm/references/rules.md#DFM-FLR-004) | 孔、槽与异形开口的制造下限 | must | NPTH hole_size min 0.5 mm，槽用 Edge.Cuts 或 NPTH 长圆孔绘制，槽边铜距离 ≥ 0.2 mm |
| [DFM-PLC-002](../skills/ee-dfm/references/rules.md#DFM-PLC-002) | 封装 courtyard 不得重叠 | must | courtyards_overlap 与 missing_courtyard 两类违规均为 0 |
| [DFM-PLN-001](../skills/ee-dfm/references/rules.md#DFM-PLN-001) | 铜皮与走线到板边、V-cut 线的距离 | must | 全局 Board Setup 的 Copper to edge clearance ≥ 0.2 mm（V-cut 板 ≥ 0.4 mm）；零违规 |
| [DFM-STK-001](../skills/ee-dfm/references/rules.md#DFM-STK-001) | DRC 的线宽线距不低于板厂能力并留余量 | must | 把 min track width / min clearance 设为上述数值（或 1.5 倍余量），kicad-cli pcb drc 零违规 |
| [DFM-STK-002](../skills/ee-dfm/references/rules.md#DFM-STK-002) | 钻孔、过孔与孔环的最小值 | must | hole_size min 0.2 mm（过孔）、annular_width min 0.20–0.25 mm、hole_to_hole min 0.45 mm（焊盘孔）/ 0.2 mm（过孔），零违规 |
| [DFM-STK-003](../skills/ee-dfm/references/rules.md#DFM-STK-003) | 焊盘与走线、孔与走线的间距下限 | must | 自定义规则按上述数值设置，零违规；SMD 焊盘尺寸用 pcbnew 脚本扫描最小边 ≥ 0.25 mm |
| [DFM-STK-004](../skills/ee-dfm/references/rules.md#DFM-STK-004) | 阻焊桥与阻焊开口的最小值 | must | Board Setup 的 Solder mask minimum web width 设为 0.10 mm（黑白油 0.13 mm），solder_mask_bridge 违规清零，或有意识地改成整窗开口 |
| [DFM-VER-001](../skills/ee-dfm/references/rules.md#DFM-VER-001) | 用板厂能力而不是 EDA 默认值跑 DRC | must | JSON 中 violations 与 unconnected_items 均为空；加载的 .kicad_dru 含 DFM-STK-001..004 的数值 |
| [GEN-FLR-007](../skills/ee-general-pcb/references/rules.md#GEN-FLR-007) | 板框闭合，铜到板边满足板厂最小间距 | must | 项目设 min_copper_edge_clearance=0.2 mm（V-cut 板 0.4 mm）；DRC 里“Board has malformed outline”和“Board edge clearance violation”必须为 0；自定义规则 (rule edge_all (constraint edge_clearance (min 0.3mm))) 可给余量 |
| [GEN-PLN-009](../skills/ee-general-pcb/references/rules.md#GEN-PLN-009) | 天线下方和周围所有铜层禁布，铺铜前先画禁布区 | must | 天线区建规则区域，勾选禁止 tracks / vias / copper fill；DRC 的“Items not allowed”数 = 0 |
| [GEN-STK-005](../skills/ee-general-pcb/references/rules.md#GEN-STK-005) | 按板厂能力设板级约束，不贴着极限设计 | must | 确认 .kicad_pro 中 min_track_width ≥ 0.10 mm、min_clearance ≥ 0.10 mm（2 层 1 oz）、min_via_diameter ≥ 0.25 mm、min_through_hole_diameter ≥ 0.15 mm、min_copper_edge_clearance ≥ 0.2 mm；DRC 0 error |
| [GEN-VER-008](../skills/ee-general-pcb/references/rules.md#GEN-VER-008) | 下单前按固定门禁逐项签核 | must | 门禁 2：退出码 0。 |
| [HSD-RTE-002](../skills/ee-high-speed/references/rules.md#HSD-RTE-002) | 按接口限定差分对内偏斜 | must | 为各接口网络类写 (constraint skew (max <limit>) (within_diff_pairs))，limit 取下列 parameters（1 mil = 0.0254 mm）；DRC 无 'Skew between tracks out of range' |
| [HSD-RTE-013](../skills/ee-high-speed/references/rules.md#HSD-RTE-013) | DDR3 数据、DQS 与时钟对的匹配和过孔规则 | must | 每个字节通道一个 skew 匹配集 (constraint skew (max 0.254mm))（±10 mil）；DQS/CK 差分对 (constraint skew (max 0.0254mm) (within_diff_pairs))（1 mil）；via_count (max 2) |
| [HSD-SCH-009](../skills/ee-high-speed/references/rules.md#HSD-SCH-009) | DDR3 的 Vref 与 VTT 用 1% 分压并就近去耦 | must | Vref 网络 track_width min 30 mil，对其他网络 clearance min 15 mil |
| [HSD-VER-002](../skills/ee-high-speed/references/rules.md#HSD-VER-002) | 出板前用自定义规则跑 DRC，并核对长度口径 | must | out.json 中 type 为 skew / length / diff_pair_gap / diff_pair_uncoupled / via_count 的违规数量 = 0；规则文件语法检查（Board Setup 的 Check rule syntax）通过 |
| [HVS-FLR-001](../skills/ee-hv-safety/references/rules.md#HVS-FLR-001) | 定义隔离栅禁布区，任何层都不得有铜跨越 | must | (rule "barrier keepout" (constraint disallow track via zone pad) (condition "A.intersectsArea('barrier')")) 并对隔离器件豁免；kicad-cli pcb drc 零违规 |
| [HVS-PLC-001](../skills/ee-hv-safety/references/rules.md#HVS-PLC-001) | 焊盘不得缩短隔离器件封装的爬电与间隙 | must | 跨栅网络类之间的 creepage ≥ 要求值，零违规 |
| [HVS-RTE-001](../skills/ee-hv-safety/references/rules.md#HVS-RTE-001) | 按表取爬电距离，加强绝缘加倍 | must | 按网络类写规则：(rule "HV creepage" (condition "A.hasNetclass('HV')") (constraint creepage (min <表值>)))，DRC 无 Creepage violation |
| [HVS-VER-001](../skills/ee-hv-safety/references/rules.md#HVS-VER-001) | 用 KiCad 的 creepage 与 clearance 规则做 DRC | must | 解析 JSON，Creepage violation、Clearance violation、Edge clearance violation 计数均为 0 |
| [RF-FLR-002](../skills/ee-rf/references/rules.md#RF-FLR-002) | 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝 | must | keepout 违例数为 0。 |
| [RF-PLN-001](../skills/ee-rf/references/rules.md#RF-PLN-001) | 射频区地平面整块不分割，芯片底焊盘多打过孔 | must | 无未连接的 GND 孤岛；zone 最小宽度、连接性规则不报错。 |
| [RF-RTE-001](../skills/ee-rf/references/rules.md#RF-RTE-001) | 射频线按 50 Ω 设计，线宽（及间隙）全程恒定 | must | track_width 规则违例数为 0。 |
| [THM-RTE-005](../skills/ee-thermal/references/rules.md#THM-RTE-005) | 散热过孔要实连到尽可能多的层，不用热焊盘 | must | 散热焊盘及其内的过孔 zone_connection = solid，所连的每个铜层都有对应的铜皮覆盖 |
| [ANA-RTE-003](../skills/ee-analog/references/rules.md#ANA-RTE-003) | 模拟输入走线远离开关节点和数字信号 | should | 为模拟网络类与数字/开关网络类设定更大的间距规则；DRC 不得有该规则的违例 |
| [AUD-NET-001](../skills/ee-audio/references/rules.md#AUD-NET-001) | Class-D 输出、自举、Vsense 和电源分别设网络类 | should | 对 OUT*、BST*、VSNS* 等网络类设最小线宽与间距约束；DRC 报告中无违规 |
| [AUD-RTE-001](../skills/ee-audio/references/rules.md#AUD-RTE-001) | Class-D 输出走线宽、短、成对并等长 | should | 输出网络线宽 ≥0.762 mm，并检查是否在两层均有走线 |
| [DFM-LIB-005](../skills/ee-dfm/references/rules.md#DFM-LIB-005) | 通孔封装的孔径按引脚加余量并满足孔环 | should | annular_width 约束 min 0.25 mm（硬限 0.18 mm 作 error 下限） |
| [DFM-LIB-007](../skills/ee-dfm/references/rules.md#DFM-LIB-007) | 丝印与焊盘保持间距 | should | 设置 silk_clearance min 0.15 mm（建议 0.25 mm），要求 0 个丝印压焊盘违规 |
| [DFM-MFG-007](../skills/ee-dfm/references/rules.md#DFM-MFG-007) | 丝印文字与线宽达到可制造下限 | should | text_height min 1.0 mm、text_thickness min 0.15 mm，针对 F.Silkscreen / B.Silkscreen，零违规 |
| [DFM-RTE-004](../skills/ee-dfm/references/rules.md#DFM-RTE-004) | 过孔覆盖方式与孔径、间距要匹配 | should | 所有过孔钻孔 ≤ 0.4 mm（盖油），超过 0.5 mm 的过孔列表为零；untented 过孔到其它裸铜的距离 ≥ 0.2 mm |
| [EMC-PLN-001](../skills/ee-emc-esd/references/rules.md#EMC-PLN-001) | 两层板地铺铜栅格化，消除只有一端连接的地岛 | should | 确保 DRC 中不存在孤岛/未连接铜皮警告，或明确豁免 |
| [GEN-FLR-003](../skills/ee-general-pcb/references/rules.md#GEN-FLR-003) | 各子系统的走线只在自己的分区内，跨区只走指定通道 | should | 在数字区画规则区域 'dig_zone'，加 (rule no_analog_in_digital (condition "A.intersectsArea('dig_zone') && A.hasNetclass('Analog')") (constraint disallow track via))，反向再建一条 'ana_zone' 规则 |
| [GEN-LIB-003](../skills/ee-general-pcb/references/rules.md#GEN-LIB-003) | 每个封装画闭合的 courtyard 并满足外扩量 | should | DRC 不得有 courtyard 重叠违规；重叠被 DRC 作为违规报告，不要在 DRC 设置里把该项设为忽略。 |
| [GEN-LIB-007](../skills/ee-general-pcb/references/rules.md#GEN-LIB-007) | 库只有一个来源：项目内库表且纳入版本控制 | should | 不得出现 Footprint doesn't match copy in library、Footprint not found in libraries（二者默认都只是 Warning）。 |
| [GEN-NET-007](../skills/ee-general-pcb/references/rules.md#GEN-NET-007) | 排查孤立标签、单引脚网络和意外短接 | should | Missing connection between items（默认 Error）与 Items shorting two nets（默认 Error）为 0；刻意短接处使用 net tie 并且不触发短路违规。 |
| [GEN-PLN-001](../skills/ee-general-pcb/references/rules.md#GEN-PLN-001) | 先保证完整地平面，地层不走线、不被过孔排切成槽 | should | GND 区域的 Minimum width 设 ≥ 0.2 mm 以去掉窄颈；加 (rule no_sig_in_gnd_layer (layer In1.Cu) (condition "A.NetName != 'GND'") (constraint disallow track)) —— In1.Cu 为 4 层板的地层 |
| [GEN-PLN-004](../skills/ee-general-pcb/references/rules.md#GEN-PLN-004) | 2 层板用地网格 / 整面地铺铜并多打缝合过孔 | should | “Isolated copper fill”类（孤岛）违规数 = 0；“Via is not connected or is connected on only one layer” = 0 |
| [GEN-PLN-007](../skills/ee-general-pcb/references/rules.md#GEN-PLN-007) | 去掉死铜和孤岛，不让铺铜悬空 | should | 违规类型“Isolated copper fill”（孤岛）数 = 0，“Copper sliver”数 = 0；注意 KiCad 只对至少有一处电气连接的区域去孤岛，完全未连接的区域不会被去掉 |
| [GEN-PLN-008](../skills/ee-general-pcb/references/rules.md#GEN-PLN-008) | 通孔焊盘用热焊盘，SMD 地焊盘和去耦地直接连 | should | (rule smd_gnd_solid (condition "A.Pad_Type == 'SMD' && A.NetName == 'GND'") (constraint zone_connection solid)) 与 (rule pth_gnd_relief (condition "A.Pad_Type == 'Through-hole' && A.NetName == 'GND'") (constraint zone_con… |
| [GEN-RTE-009](../skills/ee-general-pcb/references/rules.md#GEN-RTE-009) | 敏感信号和时钟尽量不打过孔 | should | (rule no_via_clock (condition "A.hasNetclass('Clock') // A.hasNetclass('Sensitive')") (constraint via_count (max 0))) —— 个别确需换层的网络在规则里按网络名排除，并配套执行 GEN-RTE-003 |
| [GEN-RTE-010](../skills/ee-general-pcb/references/rules.md#GEN-RTE-010) | 干扰源与敏感线间距至少 3 倍线宽 | should | 按网络类写规则，例如 0.2 mm 线宽的 Clock 网络类：(rule clock_3w (condition "A.hasNetclass('Clock') && !B.hasNetclass('Clock')") (constraint clearance (min 0.6mm)))；DRC 0 error |
| [GEN-RTE-013](../skills/ee-general-pcb/references/rules.md#GEN-RTE-013) | 晶振下方不走信号，时钟走线周围用地包裹 | should | (rule xtal_no_signals (condition "A.intersectsCourtyard('Y1') && !A.hasNetclass('Clock') && A.NetName != 'GND'") (constraint disallow track via)) —— Y1 为晶振位号 |
| [GEN-STK-004](../skills/ee-general-pcb/references/rules.md#GEN-STK-004) | 2 层板：底层做地参考，元件只放顶层 | should | (rule "no_bottom_parts" (layer B.Cu) (constraint disallow footprint)) 禁止底层元件；底层走线统计用 geometry_script |
| [GEN-STK-006](../skills/ee-general-pcb/references/rules.md#GEN-STK-006) | 网络类宽度只是默认值，必须用自定义规则落成 DRC | should | 加入 (version 1) (rule power_width (layer outer) (condition "A.hasNetclass('Power')") (constraint track_width (min 0.5mm))) 与 (rule power_via (condition "A.hasNetclass('Power') && A.Type == 'Via'") (constraint via_diameter… |
| [HSD-NET-003](../skills/ee-high-speed/references/rules.md#HSD-NET-003) | 在 .kicad_dru 中为高速网络类写长度/偏斜/间距规则 | should | 规则文件语法通过；含目标规则的板文件 DRC 输出里没有 'Skew between tracks out of range'、'Track length out of range'、'Differential pair gap out of range'、'Differential uncoupled length too long'、'Too many or too few vias on a connection' 违规 |
| [HSD-RTE-001](../skills/ee-high-speed/references/rules.md#HSD-RTE-001) | 差分对全程对称平行，未耦合段只允许出现在引出和连接器处 | should | 对差分网络类设 diff_pair_gap (min,max) 与 diff_pair_uncoupled (max 6.35mm)（0.25 inch）；PCIe 引脚入口处使用多弯折的未耦合段按 AN10373 另设 max 45 mil；DRC 无 'Differential uncoupled length too long' / 'Differential pair gap out of range' |
| [HSD-RTE-004](../skills/ee-high-speed/references/rules.md#HSD-RTE-004) | 按接口取线对间距并避开时钟线，相邻层正交布线 | should | 为 USB/PCIe/以太网等网络类写 (constraint clearance (min <值>))：对时钟/周期类 ≥ 50 mil，对其它类 ≥ 30 mil，对间 ≥ 5W；DRC 无 clearance 违规 |
| [HSD-RTE-008](../skills/ee-high-speed/references/rules.md#HSD-RTE-008) | 限制每条高速线的过孔数，两线保持一致 | should | 为各接口网络类写 (constraint via_count (max N))，N 取 parameters；DRC 无 'Too many or too few vias on a connection' |
| [HSD-RTE-009](../skills/ee-high-speed/references/rules.md#HSD-RTE-009) | 高速线总长不超过接口与器件的限值 | should | 为各接口网络类写 (constraint length (max <限值>))，DRC 无 'Track length out of range'；注意 KiCad 长度调谐器默认把过孔的层间高度计入长度（Board Setup > Constraints），DRC 与 Net Inspector 的口径可能不同，见 HSD-VER-002 |
| [HVS-FLR-002](../skills/ee-hv-safety/references/rules.md#HVS-FLR-002) | 危险电压铜皮与板边、安装孔、外壳可触及件也要满足间距 | should | (rule "HV edge" (constraint edge_clearance (min <表值>)) (condition "A.hasNetclass('HV')")) 零违规；安装孔（含镀铜螺丝孔）另用 clearance 规则 |
| [HVS-NET-001](../skills/ee-hv-safety/references/rules.md#HVS-NET-001) | 隔离两侧用独立网络名和网络类，让 DRC 能识别 | should | HV 网络类的自定义规则（clearance、creepage）生效，见 HVS-VER-001 |
| [HVS-PLN-001](../skills/ee-hv-safety/references/rules.md#HVS-PLN-001) | 铺铜、热焊盘也受 HV 网络类间距约束 | should | 先重新填充所有 zone 再跑 DRC；HV 网络类的 clearance 与 creepage 规则零违规 |
| [HVS-RTE-003](../skills/ee-hv-safety/references/rules.md#HVS-RTE-003) | 电气间隙由瞬态过压定，单独核对，爬电不得小于间隙 | should | (constraint physical_clearance (min X)) 对 HV 网络类，检查不同电位对象的空气直线距离，零违规 |
| [HVS-STK-002](../skills/ee-hv-safety/references/rules.md#HVS-STK-002) | 低压（非安规）间距按 IPC-2221B 表设 DRC | should | 按各网络组的峰值工作电压分配网络类，clearance 取表值与板厂能力较大者；DRC 零违规 |
| [RF-LIB-001](../skills/ee-rf/references/rules.md#RF-LIB-001) | 天线/模组封装自带厂商禁布区并保持不改 | should | 运行 DRC，keepout 类违例数为 0（天线自身焊盘除外）。 |
| [RF-NET-001](../skills/ee-rf/references/rules.md#RF-NET-001) | 射频网络单独设网络类，线宽恒定、不分支 | should | 自定义规则：(rule rf_width (condition "A.NetClass == 'RF'") (constraint track_width (min W) (max W)))，W 取 tline_calc 结果； 另加 clearance 规则锁定 CPWG 间隙。DRC 违例数为 0。 |
| [RF-PLN-004](../skills/ee-rf/references/rules.md#RF-PLN-004) | 匹配区走线和焊盘到邻近地铜至少 0.5 mm | should | (rule rf_match_gnd_clearance (condition "A.NetClass == 'RF' && B.Type == 'Zone'") (constraint clearance (min 0.5mm))) 仅对匹配区域生效；CPWG 馈线区另设间隙规则。DRC 违例为 0。 |
| [GEN-FLR-008](../skills/ee-general-pcb/references/rules.md#GEN-FLR-008) | 安装孔预先定位，孔径和孔距满足板厂，并留地回流接点 | consider | (rule mount_hole_size (condition "A.Type == 'Pad' && A.Pad_Type == 'NPTH, mechanical'") (constraint hole_size (min 0.5mm))) 与 (rule hole2hole (constraint hole_to_hole (min 0.45mm)))；DRC 0 error |
| [GEN-PLC-007](../skills/ee-general-pcb/references/rules.md#GEN-PLC-007) | 晶振周围留出隔离区，不放无关元件 | consider | (rule xtal_keepout (condition "A.intersectsCourtyard('Y1') && !A.hasNetclass('Clock')") (constraint disallow track via zone)) —— Y1 为晶振位号；Clock 网络类包含 OSC 网络 |
| [GEN-RTE-006](../skills/ee-general-pcb/references/rules.md#GEN-RTE-006) | MCU 供电走线按厂商给的最小宽度 | consider | (rule v3p3_width (condition "A.hasNetclass('Power3V3')") (constraint track_width (min 0.635mm))) |
| [HSD-PLN-003](../skills/ee-high-speed/references/rules.md#HSD-PLN-003) | 高速线两侧铺地时保持 3–5 倍线宽间隙，缝合需验证 | consider | 为高速差分网络类与铜区（zone）之间写 clearance 规则，min = 3W（W 取该类线宽；条件用 hasNetclass() 选线，zone 对象的类型条件按 KiCad 文档的 Type 属性写，先在测试板上验证规则生效）；DRC 无违规 |

### 可部分自动化（22）

[ANA-NET-001](../skills/ee-analog/references/rules.md#ANA-NET-001)、[DFM-RTE-002](../skills/ee-dfm/references/rules.md#DFM-RTE-002)、[EMC-FLR-003](../skills/ee-emc-esd/references/rules.md#EMC-FLR-003)、[GEN-NET-003](../skills/ee-general-pcb/references/rules.md#GEN-NET-003)、[HSD-RTE-012](../skills/ee-high-speed/references/rules.md#HSD-RTE-012)、[PWR-RTE-001](../skills/ee-power/references/rules.md#PWR-RTE-001)、[PWR-RTE-002](../skills/ee-power/references/rules.md#PWR-RTE-002)、[RF-RTE-005](../skills/ee-rf/references/rules.md#RF-RTE-005)、[AUD-STK-001](../skills/ee-audio/references/rules.md#AUD-STK-001)、[DFM-LIB-004](../skills/ee-dfm/references/rules.md#DFM-LIB-004)、[DFM-PLN-002](../skills/ee-dfm/references/rules.md#DFM-PLN-002)、[DFM-RTE-001](../skills/ee-dfm/references/rules.md#DFM-RTE-001)、[GEN-NET-002](../skills/ee-general-pcb/references/rules.md#GEN-NET-002)、[GEN-PLC-003](../skills/ee-general-pcb/references/rules.md#GEN-PLC-003)、[GEN-STK-008](../skills/ee-general-pcb/references/rules.md#GEN-STK-008)、[HSD-RTE-003](../skills/ee-high-speed/references/rules.md#HSD-RTE-003)、[HSD-RTE-010](../skills/ee-high-speed/references/rules.md#HSD-RTE-010)、[HVS-RTE-002](../skills/ee-hv-safety/references/rules.md#HVS-RTE-002)、[PWR-PLC-002](../skills/ee-power/references/rules.md#PWR-PLC-002)、[PWR-PLN-001](../skills/ee-power/references/rules.md#PWR-PLN-001)、[GEN-RTE-007](../skills/ee-general-pcb/references/rules.md#GEN-RTE-007)、[LPW-RTE-001](../skills/ee-low-power/references/rules.md#LPW-RTE-001)

### 人工 / 实测（1）

见各规则详情；此处不列。

## `netlist_diff` — 网表一致性

full 19 · partial 7 · manual 0

可用工具：KiCad schematic-vs-PCB parity (kicad-cli pcb drc --schematic-parity)（bundled）；KiCad netlist export + pin-set netlist diff (kicad-cli sch export netlist)（bundled）；IPC-D-356 netlist from PCB (kicad-cli pcb export ipcd356)（bundled）；Third-party KiCad file libraries (kiutils, kicad-skip, sexpdata)（not_installed）

### 可完全自动化（19）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [ANA-NET-001](../skills/ee-analog/references/rules.md#ANA-NET-001) | 分流电阻的 sense 抽头用独立网络 | must | 对网络 CS_P/CS_N 列出所有焊盘：必须只有 {shunt sense pad, amp IN+/IN-, 滤波 R/C 的焊盘}，不含功率网络的焊盘；原理图与 PCB 的网表一致 |
| [DFM-NET-001](../skills/ee-dfm/references/rules.md#DFM-NET-001) | BOM、CPL 与 PCB 必须一一对应 | must | 三个位号集合应相等（扣除标记 DNP / 排除的）；任何一边多或少都失败；位号需大写比较 |
| [DFM-NET-002](../skills/ee-dfm/references/rules.md#DFM-NET-002) | 位号不得靠大小写区分 | must | 把所有位号转大写后检查是否有重复 |
| [GEN-LIB-005](../skills/ee-general-pcb/references/rules.md#GEN-LIB-005) | 自动核对符号引脚与封装焊盘一致 | must | 报告中不得出现 Pad net doesn't match schematic（默认 Warning）、Footprint doesn't match symbol's footprint filters（默认 Ignore， 需手动打开）、Footprint component type doesn't match footprint pads（默认 Ignore，需手动打开）。 |
| [GEN-NET-004](../skills/ee-general-pcb/references/rules.md#GEN-NET-004) | 网络只在原理图里改，PCB 变更要反向标注 | must | 每次 PCB 变更之后，在更新原理图并完成正向更新后重新运行，退出码为 0（无任何严重级别的奇偶性差异）。 |
| [GEN-NET-005](../skills/ee-general-pcb/references/rules.md#GEN-NET-005) | 原理图与 PCB 奇偶性检查要连警告一起设为门禁 | must | 退出码为 0；JSON 报告中奇偶性类的违规数为 0（JSON 键名随 KiCad 版本核对）。固定 KiCad 主版本，因为不同版本的检查项和默认严重级别会变。 |
| [HSD-NET-001](../skills/ee-high-speed/references/rules.md#HSD-NET-001) | 差分对网络按同基名加 P/N 或 +/- 后缀命名 | must | 遍历网络名，匹配 *_P/*_N 与 *+/*-（含层级前缀）；任何网络其对侧同基名网络不存在或后缀风格不一致则报错；对已声明为差分接口的网络列表（USB D+/D−、MDI、DQS、CK、LVDS 对）逐一验证成对 |
| [PWR-LIB-001](../skills/ee-power/references/rules.md#PWR-LIB-001) | 1117 类 SOT-223 的散热 tab 必须接 VOUT | must | 找所有 1117 类器件，tab 焊盘(通常是第 4 号焊盘)的网络名必须等于该器件引脚 2 的网络名，否则报错。 |
| [PWR-SCH-012](../skills/ee-power/references/rules.md#PWR-SCH-012) | 电机两端并联续流二极管并核算额定值 | must | 对每个驱动电感性负载的 MOSFET，其漏极网络上必须存在一个二极管，阳极接漏极网络、阴极接电机正电源网络；缺失则报错。 |
| [AUD-NET-001](../skills/ee-audio/references/rules.md#AUD-NET-001) | Class-D 输出、自举、Vsense 和电源分别设网络类 | should | 所有连接 Class-D OUT/BST/VSNS 引脚的网络必须属于对应网络类，未分配即为失败 |
| [DFM-MFG-010](../skills/ee-dfm/references/rules.md#DFM-MFG-010) | 每个电源轨与关键信号至少有一个探测点 | should | 每个电源 / 地网络至少有 1 个（推荐 2 个）TestPoint 封装；列出没有测试点的网络 |
| [GEN-NET-006](../skills/ee-general-pcb/references/rules.md#GEN-NET-006) | 出图前做网表差异对比并附 IPC-D-356 | should | 分别提取 (位号, 引脚号, 网络名) 三元组的集合，计算三组之间的差集；原理图 vs PCB 差集必须为空； 当前 vs 上一版的差集必须全部能在变更记录里找到对应条目。 |
| [GEN-SCH-012](../skills/ee-general-pcb/references/rules.md#GEN-SCH-012) | 全部元件完成标注，位号唯一且稳定 | should | 不得出现 Duplicate footprints、Missing footprint、Extra footprint（默认均为 Warning）。 |
| [GEN-SCH-013](../skills/ee-general-pcb/references/rules.md#GEN-SCH-013) | 可选件和调试件标记 DNP 并保证属性两边一致 | should | 不得出现 Footprint attributes don't match symbol（Value、DNP、Exclude from BOM 不一致，默认 Warning）。 |
| [HSD-NET-002](../skills/ee-high-speed/references/rules.md#HSD-NET-002) | DDR 信号分网络类与字节通道，限定可交换范围 | should | 每个 DDR 网络属于且仅属于一个网络类；每个字节通道的 DQ[7:0]、DQS_P/N、DM 同组；输出各组成员表供长度匹配规则引用 |
| [HVS-NET-001](../skills/ee-hv-safety/references/rules.md#HVS-NET-001) | 隔离两侧用独立网络名和网络类，让 DRC 能识别 | should | 对网表里每个元件，收集其引脚所属的域（PRI/SEC）；除白名单（隔离器、变压器、光耦、Y 电容）外，同时含两域引脚的元件数 = 0 |
| [LPW-ARC-008](../skills/ee-low-power/references/rules.md#LPW-ARC-008) | 按唤醒源与保持内容选 MCU 睡眠模式（ESP32-C3） | should | 每个标记为 deep_sleep_wake 的网络必须连到 ESP32-C3 的 GPIO0–GPIO5 引脚；否则判失败。再检查唤醒网络在睡眠期的静态电平与有效边沿方向一致 |
| [PWR-LIB-002](../skills/ee-power/references/rules.md#PWR-LIB-002) | 四端子开尔文分流电阻封装要分开力端与感测端 | should | 分流电阻的两个感测焊盘网络只能出现在 INA199 的 IN+/IN- 以及少量滤波元件上，不允许连到负载电流所在的铜皮。 |
| [PWR-PLN-002](../skills/ee-power/references/rules.md#PWR-PLN-002) | 信号地与功率地在 IC 地点单点汇合 | should | 若设计中把 AGND、PGND 分为不同网络，必须通过唯一的 0 ohm/网桥或在 IC 下方的铜连接。 |

### 可部分自动化（7）

[GEN-NET-008](../skills/ee-general-pcb/references/rules.md#GEN-NET-008)、[LPW-SCH-002](../skills/ee-low-power/references/rules.md#LPW-SCH-002)、[LPW-SCH-003](../skills/ee-low-power/references/rules.md#LPW-SCH-003)、[LPW-SCH-009](../skills/ee-low-power/references/rules.md#LPW-SCH-009)、[RF-ARC-003](../skills/ee-rf/references/rules.md#RF-ARC-003)、[RF-NET-001](../skills/ee-rf/references/rules.md#RF-NET-001)、[RF-SCH-004](../skills/ee-rf/references/rules.md#RF-SCH-004)

## `bom_check` — BOM / 器件参数检查

full 33 · partial 67 · manual 1

可用工具：KiCad BOM / position export (kicad-cli sch export bom, pcb export pos)（bundled）

### 可完全自动化（33）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [ANA-ARC-003](../skills/ee-analog/references/rules.md#ANA-ARC-003) | 核对电流检测增益档和输出量程 | must | 计算 Vout_fs；要求 Vout_fs <= V+ - 0.2 V 且 <= 选定 ADC 衰减档的量程；同时检查原理图注释中写的增益与数据手册表一致 |
| [AUD-SCH-014](../skills/ee-audio/references/rules.md#AUD-SCH-014) | 自举电容按数据手册的容量、介质和耐压选 | must | 电容规格（C、介质、V）满足上述参数，并计入直流偏压降额 |
| [DFM-MFG-003](../skills/ee-dfm/references/rules.md#DFM-MFG-003) | BOM 文件格式与内容 | must | 表头恰好含 Comment、Designator、Footprint、LCSC Part #；每行 LCSC 料号匹配 ^C[0-9]+$；位号无重复、全大写；不含 DNP 零件 |
| [GEN-ARC-007](../skills/ee-general-pcb/references/rules.md#GEN-ARC-007) | 按电源轨做功耗预算并计入峰值电流 | must | 每条轨：sum(Ipeak_i) x (1 + 余量比例) <= 稳压器额定输出且 <= 输入源能力；线性稳压器 P = (Vin_max - Vout) x Iout， Tj = Tamb_max + P x theta_JA 必须小于 Tj_max（PD(max) = (TJmax - Tamb)/theta_JA）。余量比例由项目策略给定。 |
| [GEN-VER-008](../skills/ee-general-pcb/references/rules.md#GEN-VER-008) | 下单前按固定门禁逐项签核 | must | 门禁 3：每个非 DNP 行有 MPN 和 LCSC 号且在库中匹配（见 GEN-ARC-005、GEN-LIB-008）。 |
| [HSD-SCH-002](../skills/ee-high-speed/references/rules.md#HSD-SCH-002) | LVDS 接收端用 100 Ω（±2%）差分端接电阻 | must | 对每对 LVDS 接收网络检查存在一个跨接 P/N 的电阻，阻值 = 介质差分阻抗（典型 100 Ω），容差 ≤ 2%（即 1% 或 0.5% 电阻） |
| [HSD-SCH-004](../skills/ee-high-speed/references/rules.md#HSD-SCH-004) | 按协议决定是否串联隔直电容及其值和封装 | must | 对每个 TX 差分网络检查串联器件为电容，值在允许范围，封装 ≤ 0603，对内两颗相同；对 USB2 D+/D− 检查没有串联电容 |
| [HVS-SCH-003](../skills/ee-hv-safety/references/rules.md#HVS-SCH-003) | 跨隔离栅的电容必须是安规 Y 电容 | must | 所有一端在初级网络、另一端在次级网络的电容，其料号带 Y1 / Y2 认证标注与 AC 额定电压 |
| [LPW-ARC-012](../skills/ee-low-power/references/rules.md#LPW-ARC-012) | 无线突发电流下电源内阻不能把电压拉到下限以下 | must | R_int_max × I_peak < V_open_min − V_min，其中 R_int 取电池寿命末期值；LDO 取其最大输出电流（AMS1117 限流 900–1500 mA）是否 ≥ 500 mA |
| [LPW-SCH-006](../skills/ee-low-power/references/rules.md#LPW-SCH-006) | 使能与栅极控制线在复位和深睡期间要有确定电平 | must | 找出所有 MOSFET 栅极、负载开关 EN 和 LDO EN 网络，检查是否有一个电阻连接到关断电平（N-MOS 到 GND、P-MOS 到源极），并在睡眠状态表里记录该网络的默认电平；缺失即失败 |
| [PWR-ARC-002](../skills/ee-power/references/rules.md#PWR-ARC-002) | 按最坏耗散核算 LDO 结温（SOT-223 AMS1117） | must | 对每个 LDO：Vin_max 取上游最大电压（如 5.25 V），Iout_max 取各负载峰值之和，算 P 和 Tj；要求 Tj <= 125 C 且 P <= 数据手册 PD。示例板的算例：(5-3.3)*0.35 A=0.595 W，按 150 C/W 温升 89 C，环境 40 C 时 Tj 约 129 C，超限，需换大铜面积、LM1117 类低热阻器件，或改用开关稳压器。 |
| [ANA-SCH-001](../skills/ee-analog/references/rules.md#ANA-SCH-001) | SAR ADC 输入 RC：C ≥ 20 倍采样电容，用 C0G | should | C >= 20*CSH；介质字段为 C0G/NP0；电阻容差 <= 1% |
| [ANA-SCH-002](../skills/ee-analog/references/rules.md#ANA-SCH-002) | Σ-Δ ADC 差分输入：Cdiff ≥ 10 × Ccm，R < 1 kΩ | should | C_DIFF/C_CM >= 10；R 总和 < 1 kohm；C 介质为 C0G；两路输入电阻值相同 |
| [ANA-SCH-003](../skills/ee-analog/references/rules.md#ANA-SCH-003) | INA199 输入滤波：串联电阻 ≤ 10 Ω | should | 两个串联电阻相等且 <= 10 ohm；用上式算增益误差并计入预算 |
| [ANA-SCH-009](../skills/ee-analog/references/rules.md#ANA-SCH-009) | NTC 热敏电阻：限制激励避免自热 | should | P = I^2*R_ntc(Tmax)；P/耗散常数(mW/degC) 得到自热温升，要求小于温度误差预算份额 |
| [DFM-MFG-006](../skills/ee-dfm/references/rules.md#DFM-MFG-006) | 不贴的零件和通孔件同时移出 BOM 与 CPL | should | 原理图中 DNP / 通孔手焊标记的位号既不在 BOM 也不在 CPL 中；订单备注里列出这些位号及后续处理 |
| [DFM-SCH-001](../skills/ee-dfm/references/rules.md#DFM-SCH-001) | 原理图符号里带 LCSC 料号字段和 DNP 标记 | should | 对每个未标 DNP 且封装为 SMD 的符号，LCSC 字段匹配正则 ^C[0-9]+$；DNP 符号的 exclude_from_bom 为真 |
| [GEN-ARC-005](../skills/ee-general-pcb/references/rules.md#GEN-ARC-005) | 封装与器件选择要匹配贴片厂的库和工艺 | should | BOM 每个非 DNP 行都必须有 LCSC Part #（格式 Cxxxx）且能在库中匹配；统计 Basic / Preferred / Extended 数量， 匹配不到的行为失败；输出唯一扩展库料种数及对应费用。 |
| [GEN-LIB-008](../skills/ee-general-pcb/references/rules.md#GEN-LIB-008) | 库器件携带制造商、型号、数据手册和厂方料号 | should | 导出 CSV 后脚本检查：非 DNP 行的 MPN、LCSC、Datasheet 非空；LCSC 匹配 ^C[0-9]+$；同 (Value, Footprint) 只对应一个 LCSC 号。 |
| [GEN-SCH-013](../skills/ee-general-pcb/references/rules.md#GEN-SCH-013) | 可选件和调试件标记 DNP 并保证属性两边一致 | should | DNP 行有明确的启用条件说明；贴装用的 BOM（--exclude-dnp）不含 DNP 行；设计 BOM 与贴装 BOM 的差集正好等于 DNP 清单。 |
| [LPW-ARC-004](../skills/ee-low-power/references/rules.md#LPW-ARC-004) | 全板最高的最低工作电压决定电池终止电压 | should | FEP = max(各器件 V_min)，输出决定 FEP 的器件；FEP 必须 ≤ 电池在最坏负载、最低温度下的预期电压 |
| [LPW-LIB-001](../skills/ee-low-power/references/rules.md#LPW-LIB-001) | 在符号或 BOM 里记录低功耗参数及其测试条件 | should | 所有常开轨上的有源器件和电容都必须有 Iq_max、Isd、V_min 字段和条件字符串；缺失即失败 |
| [LPW-MFG-002](../skills/ee-low-power/references/rules.md#LPW-MFG-002) | 预留可单独测量睡眠电流的断点或测试点 | should | 检查 3V3 主轨与 5 V 入口上是否存在标注为 CURRENT_BREAK 的跳线/测试点位号；缺失则报告 |
| [LPW-SCH-008](../skills/ee-low-power/references/rules.md#LPW-SCH-008) | 指示灯是睡眠电流大户，要由 GPIO 驱动并在睡眠中熄灭 | should | 找出阳极/阴极经电阻连到常开轨且无晶体管/GPIO 控制的 LED 支路，I = (V_rail − Vf)/R 累加；有则报告 |
| [LPW-SCH-011](../skills/ee-low-power/references/rules.md#LPW-SCH-011) | 电池反接保护用低压降 FET，不用串联二极管 | should | V_drop = I_peak × Rds(on)_max(Vgs_min, Tmax)，要求 V_battery_min − V_drop ≥ FEP；Vgs_min 取电池放电终点电压 |
| [PWR-ARC-005](../skills/ee-power/references/rules.md#PWR-ARC-005) | 降压电感按纹波比与峰值电流选型 | should | dIL=(Vin-Vout)*D/(L*fsw)；检查 Isat_min(温度降额后) >= Iout_max + dIL/2，且 dIL/Iout_max 位于 0.2~0.4。 |
| [PWR-ARC-007](../skills/ee-power/references/rules.md#PWR-ARC-007) | 电机 MOSFET 按堵转电流核算导通损耗和结温 | should | Tj=Ta_max+Istall^2*Rds_on(Vgs,Tj_hot)*RthetaJA；要求 Tj <= 150 C 并留出降额；同时检查 Istall 不超过数据手册连续漏极电流（AO3400A: 5.7 A@25 C，4.7 A@70 C，均为 1 in2 2 oz 铜）。 |
| [PWR-SCH-004](../skills/ee-power/references/rules.md#PWR-SCH-004) | TVS 按击穿电压、钳位电压、峰值电流三条选型 | should | 三条判据逐项比较：VBR_min > Vrail_max；VC_max@IPP < min(后级 Abs Max Vin)；IPP > 预期峰值电流。 |
| [PWR-SCH-009](../skills/ee-power/references/rules.md#PWR-SCH-009) | 降压输出电容按有效电容和穿越频率阻抗核算 | should | 按数据手册推荐的最小/最大输出电容范围核对 C_eff(降额后) 落入范围，内补偿芯片尤其要用推荐的 L、C 组合。 |
| [PWR-SCH-010](../skills/ee-power/references/rules.md#PWR-SCH-010) | 降压输入电容核算纹波有效值并并联高频旁路电容 | should | I_in_rms = Iout*sqrt(D*(1-D)) 在 Vin_max、Vin_min 两端取最大，对比所选电容在 fsw 下的额定纹波电流（按并联个数和降额）；同时用偏置曲线核有效电容。 |
| [PWR-SCH-015](../skills/ee-power/references/rules.md#PWR-SCH-015) | 电源上的磁珠/LC 滤波器按偏置降额并阻尼 | should | I_dc_load / I_rated <= 0.4；DCR 引起的压降使 3.3 V 轨最低值仍满足模块下限。 |
| [PWR-SCH-016](../skills/ee-power/references/rules.md#PWR-SCH-016) | 反馈分压与基准容差下的输出电压最坏情况 | should | 固定输出：Vout_min=Vnom*(1-tol-load_reg-line_reg) 与 Vout_max 对比负载限值。 |
| [PWR-VER-007](../skills/ee-power/references/rules.md#PWR-VER-007) | 估算效率与损耗预算并与热限比较 | consider | LDO：P=(Vin-Vout)*Iout+Vin*Iq；二极管：P=Iout*Vf*(1-D)，如 AN-1229 的例子 5 A、Vf=0.5 V、D=0.4 时 1.5 W。 |

### 可部分自动化（67）

[DFM-ARC-001](../skills/ee-dfm/references/rules.md#DFM-ARC-001)、[DFM-ARC-004](../skills/ee-dfm/references/rules.md#DFM-ARC-004)、[DFM-MFG-005](../skills/ee-dfm/references/rules.md#DFM-MFG-005)、[EMC-ARC-002](../skills/ee-emc-esd/references/rules.md#EMC-ARC-002)、[EMC-SCH-008](../skills/ee-emc-esd/references/rules.md#EMC-SCH-008)、[HSD-MFG-001](../skills/ee-high-speed/references/rules.md#HSD-MFG-001)、[HSD-SCH-010](../skills/ee-high-speed/references/rules.md#HSD-SCH-010)、[HVS-ARC-001](../skills/ee-hv-safety/references/rules.md#HVS-ARC-001)、[HVS-ARC-006](../skills/ee-hv-safety/references/rules.md#HVS-ARC-006)、[HVS-SCH-001](../skills/ee-hv-safety/references/rules.md#HVS-SCH-001)、[HVS-SCH-002](../skills/ee-hv-safety/references/rules.md#HVS-SCH-002)、[LPW-SCH-005](../skills/ee-low-power/references/rules.md#LPW-SCH-005)、[PWR-ARC-006](../skills/ee-power/references/rules.md#PWR-ARC-006)、[PWR-SCH-007](../skills/ee-power/references/rules.md#PWR-SCH-007)、[RF-ARC-004](../skills/ee-rf/references/rules.md#RF-ARC-004)、[ANA-ARC-001](../skills/ee-analog/references/rules.md#ANA-ARC-001)、[ANA-ARC-002](../skills/ee-analog/references/rules.md#ANA-ARC-002)、[ANA-ARC-010](../skills/ee-analog/references/rules.md#ANA-ARC-010)、[ANA-SCH-006](../skills/ee-analog/references/rules.md#ANA-SCH-006)、[ANA-SCH-008](../skills/ee-analog/references/rules.md#ANA-SCH-008)、[ANA-SCH-013](../skills/ee-analog/references/rules.md#ANA-SCH-013)、[ANA-VER-001](../skills/ee-analog/references/rules.md#ANA-VER-001)、[AUD-ARC-001](../skills/ee-audio/references/rules.md#AUD-ARC-001)、[AUD-ARC-004](../skills/ee-audio/references/rules.md#AUD-ARC-004)、[AUD-SCH-001](../skills/ee-audio/references/rules.md#AUD-SCH-001)、[AUD-SCH-002](../skills/ee-audio/references/rules.md#AUD-SCH-002)、[AUD-SCH-012](../skills/ee-audio/references/rules.md#AUD-SCH-012)、[AUD-SCH-015](../skills/ee-audio/references/rules.md#AUD-SCH-015)、[DFM-ARC-002](../skills/ee-dfm/references/rules.md#DFM-ARC-002)、[DFM-ARC-003](../skills/ee-dfm/references/rules.md#DFM-ARC-003)、[DFM-MFG-011](../skills/ee-dfm/references/rules.md#DFM-MFG-011)、[EMC-SCH-004](../skills/ee-emc-esd/references/rules.md#EMC-SCH-004)、[GEN-ARC-002](../skills/ee-general-pcb/references/rules.md#GEN-ARC-002)、[GEN-ARC-003](../skills/ee-general-pcb/references/rules.md#GEN-ARC-003)、[GEN-ARC-004](../skills/ee-general-pcb/references/rules.md#GEN-ARC-004)、[GEN-ARC-010](../skills/ee-general-pcb/references/rules.md#GEN-ARC-010)、[GEN-SCH-016](../skills/ee-general-pcb/references/rules.md#GEN-SCH-016)、[HSD-SCH-005](../skills/ee-high-speed/references/rules.md#HSD-SCH-005)、[HSD-SCH-007](../skills/ee-high-speed/references/rules.md#HSD-SCH-007)、[HSD-SCH-008](../skills/ee-high-speed/references/rules.md#HSD-SCH-008)、[HVS-ARC-005](../skills/ee-hv-safety/references/rules.md#HVS-ARC-005)、[LPW-ARC-001](../skills/ee-low-power/references/rules.md#LPW-ARC-001)、[LPW-ARC-002](../skills/ee-low-power/references/rules.md#LPW-ARC-002)、[LPW-ARC-003](../skills/ee-low-power/references/rules.md#LPW-ARC-003)、[LPW-ARC-005](../skills/ee-low-power/references/rules.md#LPW-ARC-005)、[LPW-ARC-006](../skills/ee-low-power/references/rules.md#LPW-ARC-006)、[LPW-ARC-007](../skills/ee-low-power/references/rules.md#LPW-ARC-007)、[LPW-ARC-011](../skills/ee-low-power/references/rules.md#LPW-ARC-011)、[LPW-NET-001](../skills/ee-low-power/references/rules.md#LPW-NET-001)、[LPW-SCH-001](../skills/ee-low-power/references/rules.md#LPW-SCH-001)、[LPW-SCH-004](../skills/ee-low-power/references/rules.md#LPW-SCH-004)、[LPW-SCH-010](../skills/ee-low-power/references/rules.md#LPW-SCH-010)、[LPW-SCH-014](../skills/ee-low-power/references/rules.md#LPW-SCH-014)、[PWR-ARC-001](../skills/ee-power/references/rules.md#PWR-ARC-001)、[PWR-ARC-004](../skills/ee-power/references/rules.md#PWR-ARC-004)、[PWR-PLC-004](../skills/ee-power/references/rules.md#PWR-PLC-004)、[PWR-SCH-003](../skills/ee-power/references/rules.md#PWR-SCH-003)、[PWR-SCH-006](../skills/ee-power/references/rules.md#PWR-SCH-006)、[RF-ARC-003](../skills/ee-rf/references/rules.md#RF-ARC-003)、[RF-SCH-002](../skills/ee-rf/references/rules.md#RF-SCH-002)、[RF-SCH-003](../skills/ee-rf/references/rules.md#RF-SCH-003)、[RF-SCH-006](../skills/ee-rf/references/rules.md#RF-SCH-006)、[THM-ARC-008](../skills/ee-thermal/references/rules.md#THM-ARC-008)、[EMC-SCH-007](../skills/ee-emc-esd/references/rules.md#EMC-SCH-007)、[EMC-VER-006](../skills/ee-emc-esd/references/rules.md#EMC-VER-006)、[LPW-ARC-010](../skills/ee-low-power/references/rules.md#LPW-ARC-010)、[LPW-VER-006](../skills/ee-low-power/references/rules.md#LPW-VER-006)

### 人工 / 实测（1）

见各规则详情；此处不列。

## `geometry_script` — 几何脚本 (pcbnew)

full 106 · partial 104 · manual 0

可用工具：DRC proximity via helper rule areas + assertion (placement 'within N mm of pin')（bundled）；KiCad board statistics (kicad-cli pcb export stats)（bundled）；pcbnew Python in KiCad's bundled interpreter (geometry scripts)（bundled）；Third-party KiCad file libraries (kiutils, kicad-skip, sexpdata)（not_installed）；KiKit (panelization / fab export)（not_installed）；KiCad 10 IPC API (kicad-python / kipy) — needs a running KiCad GUI（not_installed）；Gerber / drill reading libraries (gerbonara, pygerber, pcb-tools)（not_installed）

### 可完全自动化（106）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [ANA-RTE-001](../skills/ee-analog/references/rules.md#ANA-RTE-001) | 分流电阻到放大器必须用开尔文（四线）走线 | must | 读 CS_P/CS_N 网络的所有走线与过孔，确认它们在 PCB 上只连接到分流电阻的 sense 焊盘、放大器输入引脚和滤波元件的焊盘；并检查没有铜皮（灌铜）把 sense 焊盘与功率网络连起来 |
| [AUD-PLC-001](../skills/ee-audio/references/rules.md#AUD-PLC-001) | Class-D 去耦与自举电容紧贴引脚并控制回路电感 | must | 对每个 Class-D 电源/自举引脚找最近的去耦/自举电容焊盘，测焊盘中心距并确认同层；最小电容 ≤1 mm（具体型号以手册为准） |
| [AUD-RTE-002](../skills/ee-audio/references/rules.md#AUD-RTE-002) | 开关网络与其他信号在相邻层不平行重叠 | must | 对开关网络类的每段铜，在相邻层查找非 GND 网络的铜段，计算平行重叠长度；中间无完整地层时必须为 0 |
| [DFM-LIB-002](../skills/ee-dfm/references/rules.md#DFM-LIB-002) | 两端片式元件的两个焊盘必须完全对称 | must | 比较两焊盘尺寸、形状、阻焊边距、钢网边距，并检查两焊盘中心关于封装原点对称；任何差异（> 0.01 mm）报错 |
| [DFM-MFG-001](../skills/ee-dfm/references/rules.md#DFM-MFG-001) | Gerber 输出集合完整、带 X2 属性、单位为 mm | must | 每个文件有 %TF.FileFunction 与 %TF.FilePolarity；存在 FileFunction=Profile 的文件且为闭合轮廓；MO 为 MM，FS 小数位 ≥ 5；所有文件原点一致；层数与板子叠层一致；zip 内无嵌套目录 |
| [DFM-MFG-002](../skills/ee-dfm/references/rules.md#DFM-MFG-002) | 钻孔文件按 PTH / NPTH 分开并用成品孔径 | must | 存在 *-PTH.drl 与 *-NPTH.drl 两个文件；单位 METRIC；孔径集合与 .kicad_pcb 里焊盘 / 过孔的成品孔径一致 |
| [DFM-MFG-004](../skills/ee-dfm/references/rules.md#DFM-MFG-004) | CPL 坐标文件的列、单位与方向 | must | 同一位号的 X、Y 差 ≤ 0.01 mm，旋转差 0（mod 360），层一致 |
| [DFM-RTE-002](../skills/ee-dfm/references/rules.md#DFM-RTE-002) | 2 层板不要在 SMD 焊盘里放开口过孔 | must | 遍历所有过孔，检查中心是否落在任一 SMD 焊盘轮廓内（除白名单：QFN 等散热焊盘）；命中则失败 |
| [DFM-VER-003](../skills/ee-dfm/references/rules.md#DFM-VER-003) | 下单前核对 CPL 与板文件的几何一致 | must | 对每个位号：/X−X'/ ≤ 0.01 mm、/Y−Y'/ ≤ 0.01 mm、旋转一致（含偏移表）；点在 Edge.Cuts 多边形内；Layer 与封装层一致 |
| [EMC-FLR-003](../skills/ee-emc-esd/references/rules.md#EMC-FLR-003) | 连接器到 TVS 之间划 ESD 入口禁布区 | must | 取每个连接器引脚焊盘到对应 TVS 焊盘之间的走线包络，向外扩 2 mm（2 mm 为经验值，来源未给）；包络内不得出现不属于该受保护网络的铜（走线、过孔、焊盘），否则报错 |
| [EMC-PLC-001](../skills/ee-emc-esd/references/rules.md#EMC-PLC-001) | TVS 紧靠连接器引脚，被保护 IC 远离 TVS | must | 对每个 ESD 保护网络：测连接器焊盘→TVS 信号焊盘的走线路径长度 d1，TVS 信号焊盘→被保护 IC 引脚的路径长度 d4，要求 d4 > d1，并输出 d1（越短越好，建议 d1 ≤ 10 mm 作评审阈值，该阈值为经验值） |
| [EMC-RTE-001](../skills/ee-emc-esd/references/rules.md#EMC-RTE-001) | 每条快速信号下方保持连续回流路径 | must | 沿每条目标走线按 0.5 mm 步进取样点，判断对层或同层 1 mm 内是否有地铜（填充区已填充；0.5 mm、1 mm 均为本库经验取值，来源未给）；输出无地覆盖长度占比及位置，快速网络目标 100% 覆盖 |
| [EMC-RTE-003](../skills/ee-emc-esd/references/rules.md#EMC-RTE-003) | ESD 入口走线直通 TVS，无 stub、无过孔、拐角 ≤45° | must | 对每个 ESD 保护网络建走线连通图：连接器焊盘到 TVS 信号焊盘之间过孔数 = 0；该路径上除 TVS 外没有其他分支；各线段拐角 ≤ 45° |
| [EMC-RTE-004](../skills/ee-emc-esd/references/rules.md#EMC-RTE-004) | TVS 地脚接同层地铺铜，紧邻过孔缝合到相邻地层 | must | 对每个 TVS 的地焊盘，量到最近地过孔的距离（目标 ≤ 焊盘间距的 1 倍，经验值）并统计 2 mm 内地过孔数；检查该焊盘是否直接连入同层地铺铜而非走细线（走线宽度 ≥ 0.5 mm 或直接铺铜；2 mm、0.5 mm 均为本库经验值，来源未给） |
| [GEN-FLR-007](../skills/ee-general-pcb/references/rules.md#GEN-FLR-007) | 板框闭合，铜到板边满足板厂最小间距 | must | 对 Edge.Cuts 取闭合多边形，计算所有铜对象（线、焊盘、铺铜填充）到其最小距离，通过判据 ≥ 0.2 mm |
| [GEN-PLN-009](../skills/ee-general-pcb/references/rules.md#GEN-PLN-009) | 天线下方和周围所有铜层禁布，铺铜前先画禁布区 | must | 取所有铜层的走线、过孔、焊盘与区域填充多边形，检查是否有任何顶点 / 线段落入天线禁布矩形；通过判据：数量 = 0 |
| [GEN-RTE-002](../skills/ee-general-pcb/references/rules.md#GEN-RTE-002) | 信号线不得跨越参考平面的分割槽或缝隙 | must | 对所有非电源网络的每个走线段，取其中点所在位置在参考层的填充：若不在任何 GND 填充内（或线段穿越填充边界），则标为“跨槽”；通过判据：跨槽线段数 = 0（桥接位置白名单除外） |
| [HSD-RTE-005](../skills/ee-high-speed/references/rules.md#HSD-RTE-005) | 高速线全程走在连续参考面上，远离参考面边缘和空洞 | must | 对每个高速网络的每段走线（外层），取相邻内层/对面层的 GND 铜区：线中心线必须在铜内，且到参考面外缘的距离 ≥ 90 mil，到参考面内空洞边缘的距离 ≥ 1.5W（两者是不同的判据，不要取 max；SMD 焊盘处的挖空除外）；输出违反的线段；换层段检查两层 GND 是否同网络 |
| [HSD-STK-001](../skills/ee-high-speed/references/rules.md#HSD-STK-001) | 高速线紧邻完整 GND 参考面，外层微带优先 | must | 对每个高速网络的每一段走线，取相邻内层（叠层表）上投影区域的铜填充：该区域必须完全被同一网络（GND）的铜覆盖；输出被缺铜或被不同网络覆盖的线段长度，通过判据为 0 |
| [HVS-FLR-001](../skills/ee-hv-safety/references/rules.md#HVS-FLR-001) | 定义隔离栅禁布区，任何层都不得有铜跨越 | must | 枚举所有层上与禁布区相交的铜对象，除白名单跨栅元件焊盘外应为 0 |
| [HVS-PLC-001](../skills/ee-hv-safety/references/rules.md#HVS-PLC-001) | 焊盘不得缩短隔离器件封装的爬电与间隙 | must | 对每个隔离器件，取输入侧焊盘与输出侧焊盘之间的最短距离（含周围铜皮、丝印无关），与要求的爬电值比较 |
| [HVS-SCH-003](../skills/ee-hv-safety/references/rules.md#HVS-SCH-003) | 跨隔离栅的电容必须是安规 Y 电容 | must | Y 电容两端焊盘之间距离与焊盘到邻近他网络铜的距离满足 HVS-RTE-001 的加强/基本查表值 |
| [PWR-PLC-003](../skills/ee-power/references/rules.md#PWR-PLC-003) | 续流二极管与 IC 同层，短而宽直连 SW 和 GND | must | 二极管阴极焊盘 -> IC SW 焊盘、二极管阳极焊盘 -> IC GND 焊盘的铜路径：层必须相同，过孔数 = 0，路径长度尽量短(建议 < 5 mm 作为合格初值，来源未给数值)。 |
| [PWR-RTE-001](../skills/ee-power/references/rules.md#PWR-RTE-001) | SW 节点铜皮只留够载流的最小面积 | must | 统计 SW 网络在所有层的铜面积(焊盘+走线+铺铜)，与载流所需面积比较(宽度按 PWR-RTE-005)；检查 SW 铜皮正下方、正对面层是否有其他网络的走线或被割开的地平面。 |
| [PWR-RTE-002](../skills/ee-power/references/rules.md#PWR-RTE-002) | 热回路走线不经过孔，必须时并联多孔 | must | 列出热回路路径(CIN+ -> VIN -> SW -> 续流管 -> CIN-)上的所有过孔，要求数量为 0；若 > 0 则输出并联数量与孔径，作为需要评审的例外。 |
| [PWR-RTE-005](../skills/ee-power/references/rules.md#PWR-RTE-005) | 大电流走线按 IPC-2152 和温升目标定宽 | must | 对每个标注电流 I 的网络，取全部铜路径(走线、过孔、焊盘颈部)中最窄处宽度 W，按所选铜厚和 IPC-2152 数据换算温升 dT，要求 dT <= 20 C(默认)；同时 W >= 保守经验值(取 AN-1149 的 15 mil/A，作为快速筛选)。 |
| [PWR-RTE-007](../skills/ee-power/references/rules.md#PWR-RTE-007) | 电流检测放大器输入走开尔文线接到分流电阻焊盘 | must | 检查 IN+/IN- 网络：每个网络仅连接到分流电阻的一个感测焊盘和放大器引脚(及滤波元件)，铜路径不与大电流网络共用铜皮；两线长度差小于 20%(阈值为初值，来源未给)。 |
| [RF-FLR-002](../skills/ee-rf/references/rules.md#RF-FLR-002) | 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝 | must | 取禁布区多边形（含悬出板外部分），遍历所有层的 track、via、zone 填充、pad、封装 courtyard，与多边形相交的数量为 0（天线自身焊盘除外）； 并检查螺丝孔/定位柱坐标。 |
| [RF-RTE-001](../skills/ee-rf/references/rules.md#RF-RTE-001) | 射频线按 50 Ω 设计，线宽（及间隙）全程恒定 | must | 遍历射频网络的 track 段，线宽集合大小为 1（焊盘过渡除外），等于 tline_calc 的 W；CPWG 时测与同层地铜的间隙恒定。 |
| [ANA-FLR-001](../skills/ee-analog/references/rules.md#ANA-FLR-001) | 把模拟区与数字/射频/开关区分开 | should | 给元件打标签（analog/digital/RF），在板上画出两个分区多边形；统计：模拟标签元件是否全部在模拟区内、数字网络走线是否进入模拟区、模拟网络走线是否进入数字区，越界即不通过（跨界的转换器引脚除外） |
| [ANA-LIB-001](../skills/ee-analog/references/rules.md#ANA-LIB-001) | 分流电阻用四端子封装并保留开尔文焊盘 | should | 遍历标注为 shunt 的封装，要求焊盘数 >= 4 或带独立 sense 焊盘；两个 sense 焊盘分别属于 CS_P/CS_N 网络，不与电流焊盘网络相同 |
| [ANA-PLC-001](../skills/ee-analog/references/rules.md#ANA-PLC-001) | 分流电阻紧贴电流检测放大器 | should | 测 CS_P、CS_N 两个网络的走线总长度，要求都不超过设计设定的上限，且两者长度差不超过设定的失配上限 |
| [ANA-PLC-002](../skills/ee-analog/references/rules.md#ANA-PLC-002) | 电流检测放大器的旁路电容贴脚且不打孔 | should | 找出 V+ 引脚网络上最近的电容，量焊盘中心距，并检查电容焊盘到引脚焊盘的路径上是否有过孔；距离阈值按本板设定（建议 <= 3 mm） |
| [ANA-PLC-003](../skills/ee-analog/references/rules.md#ANA-PLC-003) | ADC 基准与电源电容贴近引脚的距离上限 | should | 对 REF、AVDD、DVDD 引脚找去耦电容，测焊盘中心距，分别 <= 2.54 mm、<= 5.08 mm；检查走线路径上无过孔 |
| [ANA-RTE-002](../skills/ee-analog/references/rules.md#ANA-RTE-002) | 两条 sense 线等长、等宽、同层并排 | should | 对 CS_P 与 CS_N 网络：比较总长度（差 <= 设定值）、最小线宽（相同）、层（相同）、两线之间平均间距（<= 设定值），输出环路面积 |
| [ANA-RTE-003](../skills/ee-analog/references/rules.md#ANA-RTE-003) | 模拟输入走线远离开关节点和数字信号 | should | 对每条模拟网络走线，找到所有数字网络走线与它的平行段长度和最小间距；以及数字走线是否位于模拟元件焊盘的正下方（相邻层） |
| [ANA-RTE-005](../skills/ee-analog/references/rules.md#ANA-RTE-005) | 敏感模拟线下方保持连续的返回平面 | should | 对每条模拟信号走线，沿走线取样，检查正下方（相邻参考层）是否有地铜覆盖，列出未覆盖段及其长度 |
| [AUD-FLR-002](../skills/ee-audio/references/rules.md#AUD-FLR-002) | 定 AGND/DGND 策略：默认单一地平面分区，按 codec 手册例外 | should | 若有拆地：统计穿越分割缝的信号走线数，除桥上以外必须为 0；若单平面：检查模拟区内无数字走线 |
| [AUD-LIB-001](../skills/ee-audio/references/rules.md#AUD-LIB-001) | MEMS 话筒封装库带声孔与垫圈尺寸 | should | 遍历话筒封装的钻孔，确认存在 NPTH（非金属化）声孔，孔径落在上述范围；声孔周围无其他铜或过孔占用 |
| [AUD-PLN-002](../skills/ee-audio/references/rules.md#AUD-PLN-002) | 信号线不得跨越或切割地平面 | should | 提取 GND 铜区轮廓，找出缝隙和被走线切割的位置，数每条信号线与缝隙/切割的相交次数；桥以外必须为 0 |
| [AUD-RTE-001](../skills/ee-audio/references/rules.md#AUD-RTE-001) | Class-D 输出走线宽、短、成对并等长 | should | 测 OUT_P、OUT_N 到滤波器之间走线长度差，并测两线并行段的平均间距；报告超出基线的项 |
| [DFM-FLR-003](../skills/ee-dfm/references/rules.md#DFM-FLR-003) | 高大件和应力敏感件远离分板线 | should | 给定 V-cut 线坐标，对所有高度 > 阈值或标记为应力敏感的封装计算本体到线的最小距离 ≥ 2.0 mm；对所有铜对象计算到线的距离 ≥ 0.4 mm |
| [DFM-FLR-006](../skills/ee-dfm/references/rules.md#DFM-FLR-006) | 元件离板边与工艺边保持足够距离 | should | 对所有 SMD 焊盘计算到 Edge.Cuts 的最小距离，小于 3 mm 的列出；MARK 点净空区边到板边 ≥ 3.35 mm |
| [DFM-PLC-003](../skills/ee-dfm/references/rules.md#DFM-PLC-003) | 放置 3 个不对称的全局 MARK 点 | should | 数量 ≥ 2（推荐 3）；三点两两距离互不相同（不对称）；每个点的铜径 1.0 mm、阻焊开口 ≥ 2.0 mm；2.0 mm 圆内无其它铜 / 孔 / 丝印；到 Edge.Cuts 距离 ≥ 3.35 mm |
| [EMC-PLC-003](../skills/ee-emc-esd/references/rules.md#EMC-PLC-003) | 去耦电容贴电源脚，回路面积最小 | should | 对每个电源引脚找最近的去耦电容，量电容电源焊盘—电源脚、电容地焊盘—地脚（或最近地过孔）的距离，并估算回路面积；回路面积最小排序，最差 3 个输出供评审；检查连接走线长宽比 ≤ 3 |
| [EMC-PLN-001](../skills/ee-emc-esd/references/rules.md#EMC-PLN-001) | 两层板地铺铜栅格化，消除只有一端连接的地岛 | should | 对每块地 zone 统计与其他地铜（经过孔/焊盘）的独立连接点数，少于 2 或为孤立岛者报错；DRC 另开「未连接铜皮」检查 |
| [EMC-RTE-002](../skills/ee-emc-esd/references/rules.md#EMC-RTE-002) | 不跨平面分割/槽走线，必须跨时加缝合电容 | should | 对每条走线的各段，检查其正下方参考层是否被分割线/槽/反焊盘阵列切断；有则列出，并确认附近 ≤ 1 µF 缝合电容 |
| [EMC-RTE-005](../skills/ee-emc-esd/references/rules.md#EMC-RTE-005) | 快沿/时钟走线要短，超过阈值要端接 | should | 量每条时钟/快沿网络的走线总长，超过 101.6 mm 报警，超过 304.8 mm 要求存在串联端接电阻（由 EMC-SCH-001 检查） |
| [GEN-FLR-003](../skills/ee-general-pcb/references/rules.md#GEN-FLR-003) | 各子系统的走线只在自己的分区内，跨区只走指定通道 | should | 为每个分区定义矩形；对每条网络类为 Analog 的走线与过孔，检查是否落在数字区矩形内，对 Digital 网络反之；通过判据：违规线段数 = 0（指定通道内的跨区信号列入白名单） |
| [GEN-LIB-003](../skills/ee-general-pcb/references/rules.md#GEN-LIB-003) | 每个封装画闭合的 courtyard 并满足外扩量 | should | 对每个封装，计算焊盘与 F.Fab 本体外框的包络，courtyard 外框到包络的最小距离必须 >= 对应分类的外扩量； 缺少 F.CrtYd 图形的封装直接失败。 |
| [GEN-PLC-002](../skills/ee-general-pcb/references/rules.md#GEN-PLC-002) | 每个电源引脚一个去耦电容，小容值最近 | should | 对每个 IC 的每个电源引脚，找同网络、值为 100 nF（或最小容值）的电容，量引脚焊盘中心到电容电源焊盘中心的距离 d，及两者间走线的长度 / 宽度比；通过判据：d ≤ 项目设定值（建议 ≤ 3 mm，经验阈值，按封装调整）且长宽比 ≤ 3；每个电源引脚都存在这样的电容，共用的需在 note 登记 |
| [GEN-PLC-003](../skills/ee-general-pcb/references/rules.md#GEN-PLC-003) | 去耦电容地焊盘就近接地，用过孔或直连地铜 | should | 对每个去耦电容的 GND 焊盘，找最近的 GND 过孔或 GND 铺铜连接，量焊盘边缘到过孔边缘距离和连接线长；通过判据：连接线长 ≤ 焊盘宽度的 1 倍（经验阈值）或焊盘与 GND 铜直连（thermal relief 的辐条数 ≥ 2，见 GEN-PLN-008） |
| [GEN-PLC-005](../skills/ee-general-pcb/references/rules.md#GEN-PLC-005) | 电源入口和稳压器处放大电容，模块进线前放 10 µF | should | 取电源入口连接器电源焊盘，找同网络最近的 ≥ 10 µF 电容，量焊盘间距离，通过判据 ≤ 项目设定值（建议 ≤ 10 mm，经验阈值）；对模块 / MCU 的电源引脚同样检查是否有 10 µF 在其入口 |
| [GEN-PLC-006](../skills/ee-general-pcb/references/rules.md#GEN-PLC-006) | 晶振贴近 MCU，走线短且对称，周围有地环 | should | 取 OSC_IN / OSC_OUT 两条网络的走线长度 L1、L2 与过孔数；通过判据：L1、L2 ≤ 项目设定值（建议 ≤ 10 mm，经验阈值）且 /L1−L2/ ≤ 20%（经验阈值），过孔数 = 0；检查 CL1 / CL2 到晶振的距离对称 |
| [GEN-PLC-009](../skills/ee-general-pcb/references/rules.md#GEN-PLC-009) | ESD / TVS 器件紧靠连接器，保护对象放得更远 | should | 对每个被 TVS 保护的连接器信号，量 d1 = 连接器焊盘到 TVS 信号焊盘距离，d2 = TVS 信号焊盘到被保护 IC 引脚距离；通过判据：d1 ≤ 项目设定值（建议 ≤ 5 mm，经验阈值）且 d2 ≥ 3×d1（比例为经验阈值，SLVA680 只要求 d2 远大于 d1） |
| [GEN-PLN-001](../skills/ee-general-pcb/references/rules.md#GEN-PLN-001) | 先保证完整地平面，地层不走线、不被过孔排切成槽 | should | ①在地参考层统计非 GND 网络的走线长度，4 层板通过判据 = 0，2 层板 ≤ 项目登记的跳线总长；②对该层所有过孔 / 通孔焊盘，计算相邻两个反焊盘（孔径 + 2×间隙）之间的铜桥宽度，通过判据 ≥ 0.3 mm（经验阈值），并检查 GND 填充多边形的最窄颈宽 |
| [GEN-PLN-002](../skills/ee-general-pcb/references/rules.md#GEN-PLN-002) | 默认用一整块地平面，靠分区而不是分割隔离模拟数字 | should | 统计每个铜层上名为 GND / AGND / DGND 的区域数量与是否互相断开，通过判据：每层地区域只有 1 块连通体（允许因为走线造成的次要岛状碎片，另见 GEN-PLN-007） |
| [GEN-PLN-004](../skills/ee-general-pcb/references/rules.md#GEN-PLN-004) | 2 层板用地网格 / 整面地铺铜并多打缝合过孔 | should | 取每层所有 GND 填充连通区，统计每个连通区被过孔 / 其他层 GND 铜连接的点数；通过判据：每个面积大于项目设定值的 GND 区域连接点数 ≥ 2；另检查顶层信号线与底层信号线交叉点旁 3 mm 内是否有 GND 过孔（经验阈值） |
| [GEN-PLN-005](../skills/ee-general-pcb/references/rules.md#GEN-PLN-005) | MCU 下方做地岛，去耦和晶振的地接在上面 | should | 取 MCU（或模块 GND 焊盘区）外包框向外扩 6.35 mm 形成矩形，计算其内底层 GND 填充面积占比，通过判据 ≥ 90%（占比阈值为经验值）；检查去耦电容 GND 焊盘是否位于该矩形内 |
| [GEN-PLN-006](../skills/ee-general-pcb/references/rules.md#GEN-PLN-006) | 地铜用缝合过孔连接，间距不超过 λ/20 | should | 取 GND 过孔坐标，对射频区域和板周边路径（沿板边内缩 1 mm 的多边形）上相邻 GND 过孔的最大间距，通过判据 ≤ λ_eff/20（λ_eff = c / (f·√εeff)，εeff 取 2.8，f 取最高关注频率；2.45 GHz 时约 3.7 mm）。该 εeff 与 Sierra 示例（1 GHz→9 mm）反推一致，为推导值 |
| [GEN-PLN-007](../skills/ee-general-pcb/references/rules.md#GEN-PLN-007) | 去掉死铜和孤岛，不让铺铜悬空 | should | 对每个 zone 的每个填充连通块，检查是否至少含一个同网络焊盘 / 过孔 / 走线；通过判据：无孤块 |
| [GEN-PLN-010](../skills/ee-general-pcb/references/rules.md#GEN-PLN-010) | 晶振下方做完整地参考，区域内不放其他网络的铜 | should | 取晶振 courtyard 外扩 1 mm（外扩量为经验取值），检查相邻层 GND 填充覆盖率 ≥ 100%（无反焊盘 / 槽 / 他网络铜），且各层中无非 GND 非 OSC 网络的铜；通过判据：违规 = 0 |
| [GEN-PLN-011](../skills/ee-general-pcb/references/rules.md#GEN-PLN-011) | 芯片底部接地焊盘用多个过孔接地平面 | should | 取每个 EPAD 焊盘的外包框，统计落在其中的 GND 过孔数；通过判据：ESP32-C3 芯片 EPAD ≥ 9，其他芯片 / 模块 EPAD 按各自数据手册；另检查 EPAD 与地铜的实心连接（GEN-PLN-008） |
| [GEN-RTE-001](../skills/ee-general-pcb/references/rules.md#GEN-RTE-001) | 每条信号线下方保持连续的回流参考铜 | should | 对 Clock / PWM / 高速网络的每个走线段每 0.5 mm 取采样点，在其参考层（2 层板为对面铜层；多层板为相邻平面层）查点是否落在 GND 填充内，且以采样点为中心 ±2h 范围的填充覆盖率 ≥ 90%；通过判据：违规采样点占比 ≤ 5%（占比阈值为经验值）。h 取叠层介质厚度（JLC 1.6 mm 2 层板约 1.5 mm） |
| [GEN-RTE-004](../skills/ee-general-pcb/references/rules.md#GEN-RTE-004) | 电源线与地线并行贴近，环路长宽比不超过 3:1 | should | 对每个 IC 的电源网络，沿从稳压器 / 去耦电容到 IC 电源引脚的连接取每段走线的长度 / 宽度比（宽度取该段最窄处），通过判据 ≤ 3；并检查该段正下方相邻层有无 GND 铜（≥ 90% 长度，经验阈值） |
| [GEN-RTE-008](../skills/ee-general-pcb/references/rules.md#GEN-RTE-008) | 快信号避免 T 形分支和长残桩 | should | 对 Clock 类网络计算图中度 ≥ 3 的节点（分支点），并量每个引出段长度；通过判据：时钟网络分支点数 = 0，或引出段长度 ≤ 项目设定值（建议 ≤ 2 mm，经验阈值） |
| [GEN-RTE-009](../skills/ee-general-pcb/references/rules.md#GEN-RTE-009) | 敏感信号和时钟尽量不打过孔 | should | 统计各敏感网络的过孔数，晶振 OSC 网络必须为 0 |
| [GEN-RTE-010](../skills/ee-general-pcb/references/rules.md#GEN-RTE-010) | 干扰源与敏感线间距至少 3 倍线宽 | should | 对 Clock / PWM 网络与 Sensitive 网络的每对走线，找平行（夹角 < 10°）且间距 < 3W 的段，累计长度；通过判据：累计长度 ≤ 项目设定值（建议 ≤ 5 mm，经验阈值） |
| [GEN-RTE-013](../skills/ee-general-pcb/references/rules.md#GEN-RTE-013) | 晶振下方不走信号，时钟走线周围用地包裹 | should | 取晶振 courtyard 区域，检查所有层中是否存在非 OSC / GND 网络的走线、过孔、铜皮；检查 OSC 网络上的测试点焊盘（Fabrication_Property == 'Test point pad' 或位号 TP*）数量必须为 0；通过判据：违规项 = 0 |
| [GEN-RTE-014](../skills/ee-general-pcb/references/rules.md#GEN-RTE-014) | 连接器先到 TVS 再到 IC，路径短直无桩无过孔 | should | 对每个 ESD 网络：①连接器焊盘→TVS 焊盘之间过孔数 = 0 且线段无分叉；②其间拐角 ≤ 45°；③距离该路径 2 mm 内无其他网络的走线（未保护网络；2 mm 为经验阈值，SLVA680A 只要求不相邻、未给距离）；④TVS 地焊盘到最近 GND 过孔距离 ≤ 焊盘宽度（经验阈值）；通过判据：四项全满足 |
| [GEN-SCH-011](../skills/ee-general-pcb/references/rules.md#GEN-SCH-011) | 在原理图中为电源轨和关键信号预留测试点 | should | 每个 TP 焊盘直径 >= 0.8 mm（首选 1.0 mm），与最近的其他测试点中心距 >= 1.27 mm（首选 1.9 mm），与板边 >= 3.175 mm（首选 5 mm），与最近元件 >= 1.0 mm（首选 1.5 mm），全部在同一面。夹具数值以实际测试厂要求为准。 |
| [GEN-STK-002](../skills/ee-general-pcb/references/rules.md#GEN-STK-002) | 4 层板信号层贴近邻接平面，两平面间用厚芯板 | should | 取 F.Cu 与 In1.Cu 之间介质厚度 d1、B.Cu 与 In2.Cu 之间 d3、In1 与 In2 之间 d2；通过判据 d1 < 0.254 mm 且 d3 < 0.254 mm 且 d2 > 1.016 mm |
| [GEN-STK-003](../skills/ee-general-pcb/references/rules.md#GEN-STK-003) | 每个走线层邻接参考平面，高频线埋在两平面之间 | should | 遍历叠层，对每个含 ≥1 条走线的铜层，判断上或下相邻铜层是否为 GND / PWR 平面层；对 6 层板判断是否出现相邻两信号层且外侧无平面（SIG-SIG-PLANE-PLANE-SIG-SIG 模式） |
| [GEN-STK-004](../skills/ee-general-pcb/references/rules.md#GEN-STK-004) | 2 层板：底层做地参考，元件只放顶层 | should | 统计 B.Cu 上非 GND 网络的走线总长与焊盘数（应接近 0，仅允许少量必要跳线）；对每条顶层高速 / 时钟网络采样（每 1 mm 一点），检查该点正下方 B.Cu 是否落在 GND 填充区内，通过判据 ≥ 95% 的采样点在 GND 铜内（95% 为经验阈值） |
| [GEN-STK-007](../skills/ee-general-pcb/references/rules.md#GEN-STK-007) | 按电流和温升算线宽，IPC-2221 作保守下限 | should | 对每个电源 / 电机网络，最窄走线宽度 ≥ 上一条算出的宽度；过窄处报警 |
| [HSD-FLR-001](../skills/ee-high-speed/references/rules.md#HSD-FLR-001) | 以太网前端分区：PHY、磁件、RJ45 的距离与隔离 | should | 量 PHY 焊盘到磁件焊盘、磁件到 RJ45 焊盘、PHY 到板边、晶体到 PHY 振荡器引脚的距离，对照上述数值；量其它高速网络到 MDI 线对的最小距离 ≥ 0.3 inch |
| [HSD-PLC-003](../skills/ee-high-speed/references/rules.md#HSD-PLC-003) | 端接电阻按类型放在驱动端或接收端，stub 尽量短 | should | 对网表中标记为端接的电阻：量其焊盘到对应 IC 引脚焊盘的走线长度（不是直线距离），串联 R 距离上限由项目设定（来源只要求紧靠驱动引脚）；LVDS 端接 ≤ 12.7 mm；以太网 49.9 Ω ≤ 10 mm |
| [HSD-PLC-004](../skills/ee-high-speed/references/rules.md#HSD-PLC-004) | 高速 IC 每个电源脚就近去耦，小电容最近，过孔贴焊盘 | should | 对每个电源引脚找最近的去耦电容，量焊盘中心距、电容地焊盘到过孔的距离、过孔数；通过判据：小值电容距离最小，pad-to-via < 10 mil，每个电容 ≥ 2 个地过孔；DDR 器件按每侧 4 颗另行判定 |
| [HSD-PLN-002](../skills/ee-high-speed/references/rules.md#HSD-PLN-002) | 以太网磁件下无铜，机壳地与数字地隔离 | should | 取磁件外框（及到 RJ45 的区域），检查所有铜层在该区域内无非机壳地铜、无非以太网网络的走线/过孔；检查机壳地铜与数字地铜的最小间距 ≥ 20 mil |
| [HSD-RTE-006](../skills/ee-high-speed/references/rules.md#HSD-RTE-006) | 换层过孔旁就近放地缝合过孔，且差分两线过孔对称 | should | 对高速网络的每个信号过孔：找 200 mil 内的 GND 过孔数，≥ 1（USB/PCIe 对 ≥ 2 并两侧对称）；每对差分线的过孔数相等，沿线位置差 ≤ 1 mm；不满足则报错 |
| [HSD-RTE-010](../skills/ee-high-speed/references/rules.md#HSD-RTE-010) | 高速线少拐弯，拐角不小于 135° | should | 遍历高速网络的相邻线段，计算夹角（直线为 180°）：< 135° 报错；对夹角 < 180° 的拐点检查两侧线段长度 ≥ 1.5W |
| [HSD-RTE-011](../skills/ee-high-speed/references/rules.md#HSD-RTE-011) | 高速差分线不放测试点，远离晶振、开关电源和磁性器件 | should | 列出高速网络上的测试点焊盘（TP 前缀或 testpoint 属性），数量应为 0；对晶体、振荡器、开关稳压器电感、磁件等器件的外框膨胀 N mm（项目设定）后与高速线相交则报错 |
| [HVS-ARC-004](../skills/ee-hv-safety/references/rules.md#HVS-ARC-004) | 海拔超过 2000 m 时间隙要乘修正系数 | should | 把修正后的间隙值写入 HV 网络类的 clearance 与 creepage 规则，DRC 零违规 |
| [LPW-RTE-002](../skills/ee-low-power/references/rules.md#LPW-RTE-002) | 突发电流路径要核算走线与过孔的 IR 压降 | should | 对 5 V 入口→稳压器→3V3→模块脚路径求 Σ R，I_peak = 500 mA 时压降 ≤ 预算（预算 = 3.0 V 下限余量 − 纹波限值，由 LPW-ARC-012 给出） |
| [PWR-PLC-002](../skills/ee-power/references/rules.md#PWR-PLC-002) | 高频旁路电容紧贴 VIN/GND，大电容可稍远 | should | 测 CBYPASS 焊盘到 IC VIN/GND 引脚焊盘中心距离(要求尽量小，建议小于 2 mm 作为合格初值)；CBYPASS 与 IC 同层；CIN 到 CBYPASS 距离 <= 20 mm；CIN 地焊盘与 CO 地焊盘中心距 >= 10 mm。 |
| [PWR-PLN-003](../skills/ee-power/references/rules.md#PWR-PLN-003) | 降压 IC 散热焊盘用 0.3 mm 小孔阵列接地 | should | 对每个带散热焊盘的电源 IC：统计焊盘内过孔数、孔径、相邻中心距；要求孔径 0.3~0.33 mm，间距 1.0~1.2 mm，过孔连接到地平面且无热隔离(thermal relief)。 |
| [PWR-RTE-006](../skills/ee-power/references/rules.md#PWR-RTE-006) | 换层大电流路径按电流估算并联过孔数量 | should | 对每条标注电流 I 的网络，找出所有换层位置，统计并联过孔数 N，要求 N >= max(2, ceil(I / 1 A))(采用 SLVA773 的较宽松值，保守者取 ceil(I/0.2 A))；输出 N 与电流。 |
| [PWR-RTE-008](../skills/ee-power/references/rules.md#PWR-RTE-008) | 3.3 V 电源走线按 Espressif 最小线宽 | should | 对 +3V3 网络从稳压器到模块各电源引脚的全路径取最窄处，要求 >= 25 mil(0.635 mm)；VDD3P3 对应网络段 >= 20 mil；输出列表。 |
| [RF-ARC-006](../skills/ee-rf/references/rules.md#RF-ARC-006) | GNSS 无源天线馈线不超过 10 cm，更长用有源天线 | should | 取 GNSS 接收机 RF_IN 网络，累加从天线焊盘/连接器到 RF_IN 引脚的走线长度，<= 100 mm；超过则必须改为有源天线并核对偏置与 DC 隔离。 |
| [RF-PLC-002](../skills/ee-rf/references/rules.md#RF-PLC-002) | 射频电源脚去耦：小值最近、同层、各自接地过孔 | should | 对每个射频电源脚找出所有去耦电容：按容值升序，到引脚的距离应不递减；电容与 IC 同层； 每个电容 GND 焊盘最近的 GND 过孔仅连接 1 个元件焊盘（无共用）。 |
| [RF-PLN-002](../skills/ee-rf/references/rules.md#RF-PLN-002) | 接地缝合过孔间距不超过 λ/20（按介质内波长） | should | 沿射频线两侧及射频区边缘的顶层 GND 铜边界，取相邻 GND 过孔间距，最大值 <= 3 mm（保守取 λg/20 向下取整）；大块地铜内部相邻 GND 过孔的中心距 <= 5 mm（Nordic：至少每 5 mm 一个过孔，是间距而非到最近过孔的距离）。 |
| [RF-RTE-002](../skills/ee-rf/references/rules.md#RF-RTE-002) | 射频线尽量短，无短截线、分支和测试点 | should | RF 网络必须是链状拓扑：每个节点只连接链中相邻两个焊盘和至多一个并联元件；分支长度（非主链 track）为 0；无 TestPoint 封装挂在 RF 网络上。 |
| [RF-RTE-003](../skills/ee-rf/references/rules.md#RF-RTE-003) | 射频线拐弯用圆弧或 135° 折线，不画未切角的直角 | should | 遍历射频 track 相邻线段，转角 <= 45°（内角 >= 135°）；圆弧段用多段近似，每段转角 <= 45°。 |
| [RF-RTE-004](../skills/ee-rf/references/rules.md#RF-RTE-004) | 射频路径上不打过孔 | should | RF 网络上的 via 数量 == 0。 |
| [RF-STK-003](../skills/ee-rf/references/rules.md#RF-STK-003) | 分立射频优先 4 层；2 层板底层须为整块实心地 | should | 双层板：沿每段射频线及射频 IC/匹配网络投影采样，底层同位置必须有 GND 铜（无间断、无信号线）；四层板：L2 在射频区无切割、无走线。 |
| [THM-RTE-002](../skills/ee-thermal/references/rules.md#THM-RTE-002) | 散热过孔的孔径、间距与数量 | should | 统计每个裸露焊盘内的过孔数量、钻孔径、最近邻间距；孔径 ≤ 0.33 mm、间距在 1.0–1.2 mm，数量接近焊盘能容纳的最大值；孔径同时不低于板厂过孔下限 |
| [ANA-PLC-004](../skills/ee-analog/references/rules.md#ANA-PLC-004) | 匹配电阻同向、紧邻，沿等温线排布 | consider | 对标记为 matched 的电阻对：封装一致、旋转角相同、中心距 <= 设定上限、到热源的距离相等（差 <= 设定上限） |
| [DFM-MFG-009](../skills/ee-dfm/references/rules.md#DFM-MFG-009) | 测试点的尺寸、间距与可达性 | consider | 焊盘直径、两两中心距、到最近元件本体 / 板边距离满足上述阈值；所有测试点在同一铜层；焊盘存在阻焊开口（无阻焊覆盖） |
| [EMC-PLN-002](../skills/ee-emc-esd/references/rules.md#EMC-PLN-002) | 板边地环与缝合过孔间距小于 λ/20 | consider | 沿板边地环统计相邻缝合过孔的中心距，最大值 < λ/20（λ 按 f_max 与 εr 估算，f_max 由需求给定） |
| [EMC-RTE-006](../skills/ee-emc-esd/references/rules.md#EMC-RTE-006) | ESD 路径和快沿线避免 90° 拐角（有条件） | consider | 对 ESD 入口网络和被标记为快沿的网络，列出所有拐角角度，> 45° 者报警；其他网络仅统计不判失败 |
| [GEN-PLC-007](../skills/ee-general-pcb/references/rules.md#GEN-PLC-007) | 晶振周围留出隔离区，不放无关元件 | consider | 对每个晶振，枚举所有与它无电气关联的元件，量晶振外包框到其外包框最短距离，并检查晶振 courtyard 内是否有他网络的走线 / 过孔；通过判据：没有他网络走线 / 过孔进入晶振 courtyard，无关元件间距 ≥ 项目设定值（TI 给 25.4 mm，紧凑板按评估放宽） |
| [GEN-PLC-008](../skills/ee-general-pcb/references/rules.md#GEN-PLC-008) | 串联电阻靠近驱动端放置 | consider | 对每个标记为串联端接的电阻（值 22~100 Ω，位于 MCU 输出网络上；此为识别用的宽范围，宽于 parameters 中 TI 建议的输出脚 50~100 Ω），量它的 MCU 侧焊盘到驱动引脚焊盘的距离，通过判据 ≤ 项目设定值（建议 ≤ 5 mm，经验阈值）；该电阻 MCU 侧不得再分叉出其他负载 |
| [GEN-RTE-006](../skills/ee-general-pcb/references/rules.md#GEN-RTE-006) | MCU 供电走线按厂商给的最小宽度 | consider | 对 3V3 主网络的走线段最窄宽度取 min，应 ≥ 0.635 mm（模块板为 3V3 到模块电源引脚之间的走线）；其它电源网络 ≥ 0.254 mm；跨层处并联过孔 ≥ 2 |
| [GEN-RTE-007](../skills/ee-general-pcb/references/rules.md#GEN-RTE-007) | 拐角默认用 45° 或圆弧，90° 并非一概有害 | consider | 对每对共端点的线段计算方向变化角，转角 ≥ 80° 视为 90° 拐角；通过判据（严格集合：RF / 快速 / ESD 路径网络类）：90° 拐角数 = 0；普通网络仅报告数量不判失败 |
| [GEN-RTE-012](../skills/ee-general-pcb/references/rules.md#GEN-RTE-012) | 噪声走线不放在板子最外沿 | consider | 取 Clock / PWM / Switching 网络走线到 Edge.Cuts 的最短距离，通过判据 ≥ 项目设定值（建议 ≥ 3 mm，经验阈值）；回流平面（GND 铜）应延伸到走线外至少 2h（见 GEN-RTE-001） |
| [GEN-RTE-015](../skills/ee-general-pcb/references/rules.md#GEN-RTE-015) | 快速信号走线长度限制在约 1/50 波长以内 | consider | 取 Clock / PWM / 快边沿网络的走线总长，通过判据 ≤ 101.6 mm；超出的网络需登记串联端接（见 GEN-PLC-008）或豁免理由 |

### 可部分自动化（104）

[DFM-LIB-006](../skills/ee-dfm/references/rules.md#DFM-LIB-006)、[EMC-SCH-009](../skills/ee-emc-esd/references/rules.md#EMC-SCH-009)、[GEN-LIB-002](../skills/ee-general-pcb/references/rules.md#GEN-LIB-002)、[HSD-RTE-012](../skills/ee-high-speed/references/rules.md#HSD-RTE-012)、[HSD-VER-002](../skills/ee-high-speed/references/rules.md#HSD-VER-002)、[HVS-RTE-001](../skills/ee-hv-safety/references/rules.md#HVS-RTE-001)、[HVS-VER-001](../skills/ee-hv-safety/references/rules.md#HVS-VER-001)、[PWR-PLC-001](../skills/ee-power/references/rules.md#PWR-PLC-001)、[PWR-RTE-003](../skills/ee-power/references/rules.md#PWR-RTE-003)、[PWR-SCH-012](../skills/ee-power/references/rules.md#PWR-SCH-012)、[RF-FLR-001](../skills/ee-rf/references/rules.md#RF-FLR-001)、[RF-PLN-001](../skills/ee-rf/references/rules.md#RF-PLN-001)、[RF-RTE-005](../skills/ee-rf/references/rules.md#RF-RTE-005)、[THM-LIB-001](../skills/ee-thermal/references/rules.md#THM-LIB-001)、[THM-RTE-005](../skills/ee-thermal/references/rules.md#THM-RTE-005)、[ANA-FLR-002](../skills/ee-analog/references/rules.md#ANA-FLR-002)、[ANA-PLN-001](../skills/ee-analog/references/rules.md#ANA-PLN-001)、[ANA-PLN-002](../skills/ee-analog/references/rules.md#ANA-PLN-002)、[AUD-FLR-001](../skills/ee-audio/references/rules.md#AUD-FLR-001)、[AUD-MFG-001](../skills/ee-audio/references/rules.md#AUD-MFG-001)、[AUD-PLC-002](../skills/ee-audio/references/rules.md#AUD-PLC-002)、[AUD-PLC-003](../skills/ee-audio/references/rules.md#AUD-PLC-003)、[AUD-PLN-001](../skills/ee-audio/references/rules.md#AUD-PLN-001)、[AUD-RTE-003](../skills/ee-audio/references/rules.md#AUD-RTE-003)、[AUD-RTE-004](../skills/ee-audio/references/rules.md#AUD-RTE-004)、[AUD-RTE-005](../skills/ee-audio/references/rules.md#AUD-RTE-005)、[DFM-FLR-001](../skills/ee-dfm/references/rules.md#DFM-FLR-001)、[DFM-FLR-005](../skills/ee-dfm/references/rules.md#DFM-FLR-005)、[DFM-LIB-001](../skills/ee-dfm/references/rules.md#DFM-LIB-001)、[DFM-LIB-003](../skills/ee-dfm/references/rules.md#DFM-LIB-003)、[DFM-LIB-005](../skills/ee-dfm/references/rules.md#DFM-LIB-005)、[DFM-MFG-012](../skills/ee-dfm/references/rules.md#DFM-MFG-012)、[DFM-PLC-001](../skills/ee-dfm/references/rules.md#DFM-PLC-001)、[DFM-RTE-001](../skills/ee-dfm/references/rules.md#DFM-RTE-001)、[DFM-VER-002](../skills/ee-dfm/references/rules.md#DFM-VER-002)、[EMC-FLR-001](../skills/ee-emc-esd/references/rules.md#EMC-FLR-001)、[EMC-FLR-002](../skills/ee-emc-esd/references/rules.md#EMC-FLR-002)、[EMC-FLR-004](../skills/ee-emc-esd/references/rules.md#EMC-FLR-004)、[EMC-FLR-005](../skills/ee-emc-esd/references/rules.md#EMC-FLR-005)、[EMC-PLC-002](../skills/ee-emc-esd/references/rules.md#EMC-PLC-002)、[EMC-PLC-004](../skills/ee-emc-esd/references/rules.md#EMC-PLC-004)、[EMC-PLN-003](../skills/ee-emc-esd/references/rules.md#EMC-PLN-003)、[EMC-SCH-001](../skills/ee-emc-esd/references/rules.md#EMC-SCH-001)、[EMC-SCH-002](../skills/ee-emc-esd/references/rules.md#EMC-SCH-002)、[EMC-SCH-006](../skills/ee-emc-esd/references/rules.md#EMC-SCH-006)、[EMC-STK-001](../skills/ee-emc-esd/references/rules.md#EMC-STK-001)、[GEN-FLR-001](../skills/ee-general-pcb/references/rules.md#GEN-FLR-001)、[GEN-FLR-002](../skills/ee-general-pcb/references/rules.md#GEN-FLR-002)、[GEN-FLR-004](../skills/ee-general-pcb/references/rules.md#GEN-FLR-004)、[GEN-FLR-005](../skills/ee-general-pcb/references/rules.md#GEN-FLR-005)、[GEN-FLR-006](../skills/ee-general-pcb/references/rules.md#GEN-FLR-006)、[GEN-LIB-004](../skills/ee-general-pcb/references/rules.md#GEN-LIB-004)、[GEN-LIB-006](../skills/ee-general-pcb/references/rules.md#GEN-LIB-006)、[GEN-PLC-004](../skills/ee-general-pcb/references/rules.md#GEN-PLC-004)、[GEN-PLN-003](../skills/ee-general-pcb/references/rules.md#GEN-PLN-003)、[GEN-RTE-003](../skills/ee-general-pcb/references/rules.md#GEN-RTE-003)、[GEN-RTE-005](../skills/ee-general-pcb/references/rules.md#GEN-RTE-005)、[GEN-STK-001](../skills/ee-general-pcb/references/rules.md#GEN-STK-001)、[GEN-STK-008](../skills/ee-general-pcb/references/rules.md#GEN-STK-008)、[HSD-ARC-001](../skills/ee-high-speed/references/rules.md#HSD-ARC-001)、[HSD-FLR-002](../skills/ee-high-speed/references/rules.md#HSD-FLR-002)、[HSD-NET-004](../skills/ee-high-speed/references/rules.md#HSD-NET-004)、[HSD-PLC-001](../skills/ee-high-speed/references/rules.md#HSD-PLC-001)、[HSD-PLC-002](../skills/ee-high-speed/references/rules.md#HSD-PLC-002)、[HSD-RTE-001](../skills/ee-high-speed/references/rules.md#HSD-RTE-001)、[HSD-RTE-003](../skills/ee-high-speed/references/rules.md#HSD-RTE-003)、[HSD-RTE-007](../skills/ee-high-speed/references/rules.md#HSD-RTE-007)、[HSD-RTE-014](../skills/ee-high-speed/references/rules.md#HSD-RTE-014)、[HSD-VER-001](../skills/ee-high-speed/references/rules.md#HSD-VER-001)、[HVS-LIB-001](../skills/ee-hv-safety/references/rules.md#HVS-LIB-001)、[HVS-RTE-002](../skills/ee-hv-safety/references/rules.md#HVS-RTE-002)、[LPW-PLC-001](../skills/ee-low-power/references/rules.md#LPW-PLC-001)、[PWR-FLR-001](../skills/ee-power/references/rules.md#PWR-FLR-001)、[PWR-FLR-002](../skills/ee-power/references/rules.md#PWR-FLR-002)、[PWR-PLC-004](../skills/ee-power/references/rules.md#PWR-PLC-004)、[PWR-PLC-006](../skills/ee-power/references/rules.md#PWR-PLC-006)、[PWR-PLC-007](../skills/ee-power/references/rules.md#PWR-PLC-007)、[PWR-PLN-001](../skills/ee-power/references/rules.md#PWR-PLN-001)、[PWR-PLN-002](../skills/ee-power/references/rules.md#PWR-PLN-002)、[PWR-PLN-004](../skills/ee-power/references/rules.md#PWR-PLN-004)、[PWR-RTE-004](../skills/ee-power/references/rules.md#PWR-RTE-004)、[RF-FLR-004](../skills/ee-rf/references/rules.md#RF-FLR-004)、[RF-FLR-005](../skills/ee-rf/references/rules.md#RF-FLR-005)、[RF-LIB-001](../skills/ee-rf/references/rules.md#RF-LIB-001)、[RF-MFG-001](../skills/ee-rf/references/rules.md#RF-MFG-001)、[RF-PLC-001](../skills/ee-rf/references/rules.md#RF-PLC-001)、[RF-PLN-003](../skills/ee-rf/references/rules.md#RF-PLN-003)、[RF-PLN-005](../skills/ee-rf/references/rules.md#RF-PLN-005)、[RF-SCH-004](../skills/ee-rf/references/rules.md#RF-SCH-004)、[RF-SCH-008](../skills/ee-rf/references/rules.md#RF-SCH-008)、[RF-STK-001](../skills/ee-rf/references/rules.md#RF-STK-001)、[RF-STK-002](../skills/ee-rf/references/rules.md#RF-STK-002)、[THM-PLC-001](../skills/ee-thermal/references/rules.md#THM-PLC-001)、[THM-PLN-001](../skills/ee-thermal/references/rules.md#THM-PLN-001)、[THM-PLN-002](../skills/ee-thermal/references/rules.md#THM-PLN-002)、[THM-PLN-003](../skills/ee-thermal/references/rules.md#THM-PLN-003)、[THM-RTE-004](../skills/ee-thermal/references/rules.md#THM-RTE-004)、[ANA-PLN-003](../skills/ee-analog/references/rules.md#ANA-PLN-003)、[ANA-RTE-004](../skills/ee-analog/references/rules.md#ANA-RTE-004)、[ANA-STK-001](../skills/ee-analog/references/rules.md#ANA-STK-001)、[DFM-PLC-004](../skills/ee-dfm/references/rules.md#DFM-PLC-004)、[GEN-RTE-011](../skills/ee-general-pcb/references/rules.md#GEN-RTE-011)、[HSD-STK-003](../skills/ee-high-speed/references/rules.md#HSD-STK-003)、[LPW-RTE-001](../skills/ee-low-power/references/rules.md#LPW-RTE-001)

## `spice` — SPICE 仿真

full 8 · partial 88 · manual 0

可用工具：KiCad netlist export + pin-set netlist diff (kicad-cli sch export netlist)（bundled）；KiCad-bundled libngspice 45.2 driven from Python via ctypes (headless)（bundled）；KiCad schematic → SPICE netlist (kicad-cli sch export netlist --format spice)（bundled）；Standalone ngspice (Homebrew formula)（not_installed）；LTspice (Analog Devices, macOS)（not_installed）；Xyce (Sandia, SPICE-compatible parallel simulator)（not_installed）；Qucs-S (GUI front-end for ngspice / Xyce / Qucsator)（not_installed）；Python SPICE wrappers (PySpice, spicelib, ltspice reader)（not_installed）

### 可完全自动化（8）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [PWR-VER-001](../skills/ee-power/references/rules.md#PWR-VER-001) | 开关电源环路增益相位裕量与穿越频率签核 | must | 读增益 0 dB 的频率 fc 与此处相位裕量 PM、相位 -180 度处的增益裕量 GM；用 .step 扫描 Cout(C_eff，见 PWR-SCH-006)、ESR、Iload、Vin 的所有极值角落，全部满足 PM >= 45 度、GM >= 6 dB、fc 在 [fsw/10, fsw/5] 内。 |
| [PWR-VER-002](../skills/ee-power/references/rules.md#PWR-VER-002) | 负载阶跃响应与 LDO 稳定性的 SPICE 与实测 | must | 10%->90% 阶跃，上升/下降时间 <= 1 us(初值)，读 Vout 最大偏差 dV 与稳定时间，要求 dV 在系统允许范围内且初始尖峰之后振铃不超过 4 次（SLVA115A：通常 4 个振铃以内表示相位裕量足够）；扫描 Cout 极值。 |
| [PWR-VER-004](../skills/ee-power/references/rules.md#PWR-VER-004) | 电机启动/堵转期间核算电源轨跌落与欠压余量 | must | 5 V 源内阻 + 线缆 + PPTC(热态最大电阻) + 母线电容(降额)；电机堵转 1 s，同时 Wi-Fi 脉冲 0.35 A，读 3.3 V 最低值与 LDO 的 Vin-Vout，要求 >= 3.0 V 且 Vin-Vout >= 压差(PWR-ARC-003)。 |
| [EMC-SCH-005](../skills/ee-emc-esd/references/rules.md#EMC-SCH-005) | 磁珠要在噪声频段呈电阻性，且与电容的 LC 需阻尼 | should | AC 扫描 IC 侧电压对输入噪声的传递函数，任何频点增益不得 > 0 dB（无放大），并列出谐振频率 |
| [EMC-SCH-013](../skills/ee-emc-esd/references/rules.md#EMC-SCH-013) | 感性负载必须有续流/钳位路径 | should | 仿真关断瞬态，读开关管 Vds 峰值，须低于其 Vds 额定并留裕量 |
| [PWR-SCH-014](../skills/ee-power/references/rules.md#PWR-SCH-014) | 上电复位时序：电源稳定后再使能，慢速斜坡加监控芯片 | should | 仿真上电斜坡(含慢斜坡 10 ms~100 ms)，读 3.3 V 轨达到 3.0 V 的时刻与 CHIP_EN 越过 VIH 的时刻，要求 CHIP_EN 晚至少 50 us 且 3.3 V 此后不再低于 3.0 V。 |
| [PWR-SCH-016](../skills/ee-power/references/rules.md#PWR-SCH-016) | 反馈分压与基准容差下的输出电压最坏情况 | should | 对 Vref、R1、R2 取容差极值或蒙特卡洛 1000 次，读 Vout 的最小/最大，要求落在 [3.0, 3.6] V 内并留一定余量。 |
| [PWR-VER-003](../skills/ee-power/references/rules.md#PWR-VER-003) | 上电浪涌电流与热插拔电压过冲仿真 | should | 电源阶跃(上升时间 10 us~10 ms 的角落)，串入线缆电阻/电感，读入口电流峰值和稳压器输入电压峰值；要求峰值电流 < PPTC 保持电流与连接器额定电流，Vin 峰值 < 稳压器绝对最大额定值。 |

### 可部分自动化（88）

[ANA-ARC-003](../skills/ee-analog/references/rules.md#ANA-ARC-003)、[ANA-VER-003](../skills/ee-analog/references/rules.md#ANA-VER-003)、[EMC-PLC-001](../skills/ee-emc-esd/references/rules.md#EMC-PLC-001)、[EMC-RTE-004](../skills/ee-emc-esd/references/rules.md#EMC-RTE-004)、[EMC-SCH-008](../skills/ee-emc-esd/references/rules.md#EMC-SCH-008)、[GEN-SCH-005](../skills/ee-general-pcb/references/rules.md#GEN-SCH-005)、[GEN-SCH-007](../skills/ee-general-pcb/references/rules.md#GEN-SCH-007)、[GEN-SCH-015](../skills/ee-general-pcb/references/rules.md#GEN-SCH-015)、[LPW-ARC-012](../skills/ee-low-power/references/rules.md#LPW-ARC-012)、[LPW-SCH-005](../skills/ee-low-power/references/rules.md#LPW-SCH-005)、[LPW-SCH-012](../skills/ee-low-power/references/rules.md#LPW-SCH-012)、[LPW-VER-005](../skills/ee-low-power/references/rules.md#LPW-VER-005)、[PWR-ARC-003](../skills/ee-power/references/rules.md#PWR-ARC-003)、[PWR-ARC-006](../skills/ee-power/references/rules.md#PWR-ARC-006)、[PWR-SCH-007](../skills/ee-power/references/rules.md#PWR-SCH-007)、[PWR-SCH-012](../skills/ee-power/references/rules.md#PWR-SCH-012)、[ANA-ARC-001](../skills/ee-analog/references/rules.md#ANA-ARC-001)、[ANA-ARC-002](../skills/ee-analog/references/rules.md#ANA-ARC-002)、[ANA-ARC-005](../skills/ee-analog/references/rules.md#ANA-ARC-005)、[ANA-ARC-006](../skills/ee-analog/references/rules.md#ANA-ARC-006)、[ANA-ARC-010](../skills/ee-analog/references/rules.md#ANA-ARC-010)、[ANA-SCH-001](../skills/ee-analog/references/rules.md#ANA-SCH-001)、[ANA-SCH-002](../skills/ee-analog/references/rules.md#ANA-SCH-002)、[ANA-SCH-003](../skills/ee-analog/references/rules.md#ANA-SCH-003)、[ANA-SCH-004](../skills/ee-analog/references/rules.md#ANA-SCH-004)、[ANA-SCH-005](../skills/ee-analog/references/rules.md#ANA-SCH-005)、[ANA-SCH-006](../skills/ee-analog/references/rules.md#ANA-SCH-006)、[ANA-SCH-013](../skills/ee-analog/references/rules.md#ANA-SCH-013)、[ANA-VER-001](../skills/ee-analog/references/rules.md#ANA-VER-001)、[ANA-VER-002](../skills/ee-analog/references/rules.md#ANA-VER-002)、[AUD-SCH-002](../skills/ee-audio/references/rules.md#AUD-SCH-002)、[AUD-SCH-003](../skills/ee-audio/references/rules.md#AUD-SCH-003)、[AUD-SCH-004](../skills/ee-audio/references/rules.md#AUD-SCH-004)、[AUD-SCH-005](../skills/ee-audio/references/rules.md#AUD-SCH-005)、[AUD-SCH-007](../skills/ee-audio/references/rules.md#AUD-SCH-007)、[AUD-SCH-008](../skills/ee-audio/references/rules.md#AUD-SCH-008)、[AUD-SCH-009](../skills/ee-audio/references/rules.md#AUD-SCH-009)、[AUD-SCH-010](../skills/ee-audio/references/rules.md#AUD-SCH-010)、[AUD-SCH-011](../skills/ee-audio/references/rules.md#AUD-SCH-011)、[AUD-SCH-013](../skills/ee-audio/references/rules.md#AUD-SCH-013)、[AUD-VER-003](../skills/ee-audio/references/rules.md#AUD-VER-003)、[AUD-VER-004](../skills/ee-audio/references/rules.md#AUD-VER-004)、[EMC-SCH-006](../skills/ee-emc-esd/references/rules.md#EMC-SCH-006)、[EMC-SCH-012](../skills/ee-emc-esd/references/rules.md#EMC-SCH-012)、[EMC-VER-003](../skills/ee-emc-esd/references/rules.md#EMC-VER-003)、[GEN-ARC-008](../skills/ee-general-pcb/references/rules.md#GEN-ARC-008)、[GEN-PLC-002](../skills/ee-general-pcb/references/rules.md#GEN-PLC-002)、[GEN-SCH-016](../skills/ee-general-pcb/references/rules.md#GEN-SCH-016)、[GEN-VER-006](../skills/ee-general-pcb/references/rules.md#GEN-VER-006)、[HSD-ARC-001](../skills/ee-high-speed/references/rules.md#HSD-ARC-001)、[HSD-SCH-001](../skills/ee-high-speed/references/rules.md#HSD-SCH-001)、[HSD-VER-003](../skills/ee-high-speed/references/rules.md#HSD-VER-003)、[LPW-ARC-005](../skills/ee-low-power/references/rules.md#LPW-ARC-005)、[LPW-PLC-001](../skills/ee-low-power/references/rules.md#LPW-PLC-001)、[LPW-SCH-001](../skills/ee-low-power/references/rules.md#LPW-SCH-001)、[LPW-SCH-007](../skills/ee-low-power/references/rules.md#LPW-SCH-007)、[LPW-SCH-010](../skills/ee-low-power/references/rules.md#LPW-SCH-010)、[LPW-SCH-011](../skills/ee-low-power/references/rules.md#LPW-SCH-011)、[LPW-SCH-013](../skills/ee-low-power/references/rules.md#LPW-SCH-013)、[LPW-VER-004](../skills/ee-low-power/references/rules.md#LPW-VER-004)、[PWR-ARC-004](../skills/ee-power/references/rules.md#PWR-ARC-004)、[PWR-ARC-005](../skills/ee-power/references/rules.md#PWR-ARC-005)、[PWR-SCH-001](../skills/ee-power/references/rules.md#PWR-SCH-001)、[PWR-SCH-002](../skills/ee-power/references/rules.md#PWR-SCH-002)、[PWR-SCH-004](../skills/ee-power/references/rules.md#PWR-SCH-004)、[PWR-SCH-005](../skills/ee-power/references/rules.md#PWR-SCH-005)、[PWR-SCH-006](../skills/ee-power/references/rules.md#PWR-SCH-006)、[PWR-SCH-008](../skills/ee-power/references/rules.md#PWR-SCH-008)、[PWR-SCH-009](../skills/ee-power/references/rules.md#PWR-SCH-009)、[PWR-SCH-010](../skills/ee-power/references/rules.md#PWR-SCH-010)、[PWR-SCH-011](../skills/ee-power/references/rules.md#PWR-SCH-011)、[PWR-SCH-015](../skills/ee-power/references/rules.md#PWR-SCH-015)、[PWR-VER-006](../skills/ee-power/references/rules.md#PWR-VER-006)、[RF-SCH-002](../skills/ee-rf/references/rules.md#RF-SCH-002)、[RF-SCH-005](../skills/ee-rf/references/rules.md#RF-SCH-005)、[RF-SCH-007](../skills/ee-rf/references/rules.md#RF-SCH-007)、[RF-VER-003](../skills/ee-rf/references/rules.md#RF-VER-003)、[ANA-ARC-004](../skills/ee-analog/references/rules.md#ANA-ARC-004)、[ANA-PLN-003](../skills/ee-analog/references/rules.md#ANA-PLN-003)、[ANA-RTE-004](../skills/ee-analog/references/rules.md#ANA-RTE-004)、[AUD-SCH-016](../skills/ee-audio/references/rules.md#AUD-SCH-016)、[EMC-SCH-003](../skills/ee-emc-esd/references/rules.md#EMC-SCH-003)、[EMC-SCH-011](../skills/ee-emc-esd/references/rules.md#EMC-SCH-011)、[GEN-VER-005](../skills/ee-general-pcb/references/rules.md#GEN-VER-005)、[PWR-PLC-005](../skills/ee-power/references/rules.md#PWR-PLC-005)、[PWR-VER-007](../skills/ee-power/references/rules.md#PWR-VER-007)、[RF-VER-007](../skills/ee-rf/references/rules.md#RF-VER-007)、[THM-ARC-007](../skills/ee-thermal/references/rules.md#THM-ARC-007)

## `tline_calc` — 传输线 / 载流计算

full 5 · partial 10 · manual 0

可用工具：KiCad PCB Calculator (GUI only)（bundled）；Python re-implementations of IPC-2221 trace width and microstrip Z0（installed）；scikit-rf (RF networks, transmission-line media, Touchstone)（not_installed）

### 可完全自动化（5）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [GEN-SCH-009](../skills/ee-general-pcb/references/rules.md#GEN-SCH-009) | 晶体负载电容按公式计算并留出杂散电容 | should | 输入 CL、Cs、ESR、C0、ppm 预算和 IC 的 gm_crit 参数：输出 C1 = C2、实际 CL、增益裕度 gm / gm_crit（>= 5）、驱动功率 DL（<= 晶体额定）。 公式：CL = C1*C2/(C1+C2)+Cs；gm_crit = 4*ESR*(2*pi*F)^2*(C0+CL)^2。 |
| [GEN-SCH-017](../skills/ee-general-pcb/references/rules.md#GEN-SCH-017) | I2C 上拉电阻按上升时间和灌电流计算 | should | 输入 VCC、IOL、tr 上限、估算 Cb（元件引脚电容加走线电容）：计算 Rp(min) 和 Rp(max)，所选电阻必须落在区间内。 例：Cb = 200 pF、VCC = 3.3 V、Fast mode：Rp 在 0.97 到 1.77 kOhm 之间。 |
| [GEN-STK-007](../skills/ee-general-pcb/references/rules.md#GEN-STK-007) | 按电流和温升算线宽，IPC-2221 作保守下限 | should | 对每条载流网络取峰值 / RMS 电流 I，反解 A=(I/(k·ΔT^0.44))^(1/0.725)，宽度=A/铜厚；板上该网络最窄处宽度 ≥ 计算值。例（本调研按公式算出）：1 oz 外层 ΔT=10 °C：1 A→0.30 mm，3 A→1.37 mm，5 A→2.77 mm；同条件内层 k=0.024：1 A→0.78 mm，3 A→3.56 mm |
| [RF-STK-002](../skills/ee-rf/references/rules.md#RF-STK-002) | 50 Ω 馈线优先用带地共面波导（CPWG） | should | 输入板厂叠层，求 50 Ω 的 W、G；检查 (W + 2G) < H。 |
| [THM-RTE-001](../skills/ee-thermal/references/rules.md#THM-RTE-001) | 大电流走线按 IPC-2152 的温升来定宽 | should | 输入电流、铜厚、内 / 外层、温升预算，求最小线宽；板上对应网络的最窄处（含焊盘颈缩、过孔）不得小于该宽度 |

### 可部分自动化（10）

[HSD-ARC-002](../skills/ee-high-speed/references/rules.md#HSD-ARC-002)、[PWR-RTE-005](../skills/ee-power/references/rules.md#PWR-RTE-005)、[GEN-STK-002](../skills/ee-general-pcb/references/rules.md#GEN-STK-002)、[HSD-RTE-014](../skills/ee-high-speed/references/rules.md#HSD-RTE-014)、[HSD-STK-002](../skills/ee-high-speed/references/rules.md#HSD-STK-002)、[HSD-VER-001](../skills/ee-high-speed/references/rules.md#HSD-VER-001)、[PWR-RTE-006](../skills/ee-power/references/rules.md#PWR-RTE-006)、[RF-PLN-005](../skills/ee-rf/references/rules.md#RF-PLN-005)、[RF-STK-001](../skills/ee-rf/references/rules.md#RF-STK-001)、[PWR-STK-001](../skills/ee-power/references/rules.md#PWR-STK-001)

## `em_sim` — 电磁仿真

full 0 · partial 12 · manual 0

可用工具：scikit-rf (RF networks, transmission-line media, Touchstone)（not_installed）；openEMS (FDTD 3D EM solver) + CSXCAD Python（not_installed）；Elmer FEM (thermal / electrostatics / Joule heating / magnetodynamics)（not_installed）；Commercial SI / PI / EM / thermal suites (not available here)（not_installed）

### 可部分自动化（12）

[AUD-PLC-001](../skills/ee-audio/references/rules.md#AUD-PLC-001)、[EMC-RTE-001](../skills/ee-emc-esd/references/rules.md#EMC-RTE-001)、[PWR-PLC-001](../skills/ee-power/references/rules.md#PWR-PLC-001)、[AUD-PLN-001](../skills/ee-audio/references/rules.md#AUD-PLN-001)、[RF-FLR-005](../skills/ee-rf/references/rules.md#RF-FLR-005)、[RF-PLN-002](../skills/ee-rf/references/rules.md#RF-PLN-002)、[RF-VER-001](../skills/ee-rf/references/rules.md#RF-VER-001)、[RF-VER-004](../skills/ee-rf/references/rules.md#RF-VER-004)、[EMC-STK-002](../skills/ee-emc-esd/references/rules.md#EMC-STK-002)、[HSD-PLN-003](../skills/ee-high-speed/references/rules.md#HSD-PLN-003)、[HSD-VER-004](../skills/ee-high-speed/references/rules.md#HSD-VER-004)、[RF-FLR-006](../skills/ee-rf/references/rules.md#RF-FLR-006)

## `si_sim` — 信号完整性仿真

full 0 · partial 13 · manual 0

可用工具：KiCad-bundled libngspice 45.2 driven from Python via ctypes (headless)（bundled）；scikit-rf (RF networks, transmission-line media, Touchstone)（not_installed）；openEMS (FDTD 3D EM solver) + CSXCAD Python（not_installed）；Reflection / termination checks with ngspice T-line elements (+ IBIS parsers)（bundled）；Commercial SI / PI / EM / thermal suites (not available here)（not_installed）

### 可部分自动化（13）

[HSD-RTE-012](../skills/ee-high-speed/references/rules.md#HSD-RTE-012)、[HSD-RTE-013](../skills/ee-high-speed/references/rules.md#HSD-RTE-013)、[AUD-RTE-005](../skills/ee-audio/references/rules.md#AUD-RTE-005)、[EMC-ARC-004](../skills/ee-emc-esd/references/rules.md#EMC-ARC-004)、[EMC-RTE-005](../skills/ee-emc-esd/references/rules.md#EMC-RTE-005)、[EMC-SCH-001](../skills/ee-emc-esd/references/rules.md#EMC-SCH-001)、[GEN-RTE-008](../skills/ee-general-pcb/references/rules.md#GEN-RTE-008)、[HSD-ARC-004](../skills/ee-high-speed/references/rules.md#HSD-ARC-004)、[HSD-ARC-005](../skills/ee-high-speed/references/rules.md#HSD-ARC-005)、[HSD-NET-004](../skills/ee-high-speed/references/rules.md#HSD-NET-004)、[HSD-RTE-004](../skills/ee-high-speed/references/rules.md#HSD-RTE-004)、[HSD-VER-003](../skills/ee-high-speed/references/rules.md#HSD-VER-003)、[GEN-PLC-008](../skills/ee-general-pcb/references/rules.md#GEN-PLC-008)

## `pi_sim` — 电源完整性仿真

full 0 · partial 7 · manual 0

可用工具：KiCad-bundled libngspice 45.2 driven from Python via ctypes (headless)（bundled）；Track-network IR drop solver (pcbnew dump + numpy/scipy)（installed）；PDN impedance and decoupling via libngspice AC analysis（bundled）；Commercial SI / PI / EM / thermal suites (not available here)（not_installed）

### 可部分自动化（7）

[AUD-SCH-015](../skills/ee-audio/references/rules.md#AUD-SCH-015)、[EMC-PLC-003](../skills/ee-emc-esd/references/rules.md#EMC-PLC-003)、[HSD-PLC-004](../skills/ee-high-speed/references/rules.md#HSD-PLC-004)、[HSD-PLN-001](../skills/ee-high-speed/references/rules.md#HSD-PLN-001)、[HSD-VER-005](../skills/ee-high-speed/references/rules.md#HSD-VER-005)、[PWR-VER-005](../skills/ee-power/references/rules.md#PWR-VER-005)、[RF-SCH-006](../skills/ee-rf/references/rules.md#RF-SCH-006)

## `thermal_sim` — 热仿真

full 7 · partial 8 · manual 3

可用工具：Elmer FEM (thermal / electrostatics / Joule heating / magnetodynamics)（not_installed）；Commercial SI / PI / EM / thermal suites (not available here)（not_installed）；Thermal estimation building blocks (numpy / scipy / networkx; no solver installed)（installed）

### 可完全自动化（7）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [THM-ARC-002](../skills/ee-thermal/references/rules.md#THM-ARC-002) | 在最高环境温度下算每个发热件的结温 | must | 对每个器件计算 Tj，要求 Tj ≤ Tj,max − 余量；列出余量最小的 3 个器件 |
| [THM-ARC-003](../skills/ee-thermal/references/rules.md#THM-ARC-003) | 线性稳压器的功耗按最坏输入电压和最大电流算 | must | PD = (Vin_max − Vout) × Iout_max；θJA,needed = (125 − Ta,max)/PD；要求 θJA,needed ≥ 板子 θJA,effective（见 THM-PLN-001 的铜皮面积表） |
| [THM-ARC-006](../skills/ee-thermal/references/rules.md#THM-ARC-006) | MOSFET 导通损耗按热态 Rds(on) 算 | must | 例：2 A、热态 Rds(on) 约 48 mΩ × 1.5（取 1.43–1.56 的中间值）≈ 72 mΩ → P ≈ 0.29 W；θJA 125 °C/W 时温升约 36 °C；叠加 Ta,max 后 Tj < 150 °C 并有余量 |
| [THM-MFG-001](../skills/ee-thermal/references/rules.md#THM-MFG-001) | 裸露焊盘的焊接面积与空洞要有上限并用 X 光验证 | should | 用 θJA 增加 4–19% 的悲观值重算 Tj，仍然满足限值 |
| [THM-ARC-005](../skills/ee-thermal/references/rules.md#THM-ARC-005) | 高海拔使用时放大 θJA | consider | 把 θJA,effective 乘上目标海拔系数后重算 Tj，仍满足 THM-ARC-002 |
| [THM-RTE-003](../skills/ee-thermal/references/rules.md#THM-RTE-003) | 用过孔阵列的并联热阻核算而不是凭感觉 | consider | R_array ≤ 热预算中分给过孔的份额；需要时说明为什么不用更多过孔或更厚镀铜 |
| [THM-STK-003](../skills/ee-thermal/references/rules.md#THM-STK-003) | 用板面积规则做第一遍可行性检查 | consider | Σ 板上耗散功率 × 15.29 cm²/W 与板面积比较；局部大功耗件用 θJA − θJC 公式估算它需要的铜面积 |

### 可部分自动化（8）

[PWR-ARC-002](../skills/ee-power/references/rules.md#PWR-ARC-002)、[PWR-RTE-005](../skills/ee-power/references/rules.md#PWR-RTE-005)、[THM-ARC-001](../skills/ee-thermal/references/rules.md#THM-ARC-001)、[ANA-FLR-002](../skills/ee-analog/references/rules.md#ANA-FLR-002)、[PWR-ARC-007](../skills/ee-power/references/rules.md#PWR-ARC-007)、[THM-ARC-004](../skills/ee-thermal/references/rules.md#THM-ARC-004)、[THM-STK-001](../skills/ee-thermal/references/rules.md#THM-STK-001)、[THM-VER-005](../skills/ee-thermal/references/rules.md#THM-VER-005)

### 人工 / 实测（3）

见各规则详情；此处不列。

## `emc_precompliance` — EMC 预兼容

full 0 · partial 0 · manual 27

可用工具：Bench instruments (scope / DMM / VNA / power analyzer / thermal camera)（not_installed）

### 人工 / 实测（27）

见各规则详情；此处不列。

## `bench` — 实物测量

full 1 · partial 18 · manual 163

可用工具：Bench instruments (scope / DMM / VNA / power analyzer / thermal camera)（not_installed）

### 可完全自动化（1）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [RF-VER-001](../skills/ee-rf/references/rules.md#RF-VER-001) | 天线端回波损耗 S11 <= -10 dB 覆盖整个工作频段 | should | 在连接器参考面做一端口校准，扫 2.3-2.6 GHz，导入 touchstone： band = skrf.Network('s11.s1p')['2.4-2.4835ghz']，要求 (band.s_db[:,0,0] <= -10).all()。 |

### 可部分自动化（18）

[ANA-VER-005](../skills/ee-analog/references/rules.md#ANA-VER-005)、[LPW-VER-003](../skills/ee-low-power/references/rules.md#LPW-VER-003)、[LPW-VER-005](../skills/ee-low-power/references/rules.md#LPW-VER-005)、[ANA-ARC-007](../skills/ee-analog/references/rules.md#ANA-ARC-007)、[ANA-MFG-001](../skills/ee-analog/references/rules.md#ANA-MFG-001)、[ANA-VER-004](../skills/ee-analog/references/rules.md#ANA-VER-004)、[ANA-VER-004](../skills/ee-analog/references/rules.md#ANA-VER-004)、[AUD-ARC-003](../skills/ee-audio/references/rules.md#AUD-ARC-003)、[AUD-VER-001](../skills/ee-audio/references/rules.md#AUD-VER-001)、[AUD-VER-004](../skills/ee-audio/references/rules.md#AUD-VER-004)、[AUD-VER-005](../skills/ee-audio/references/rules.md#AUD-VER-005)、[LPW-ARC-001](../skills/ee-low-power/references/rules.md#LPW-ARC-001)、[LPW-SCH-013](../skills/ee-low-power/references/rules.md#LPW-SCH-013)、[LPW-VER-002](../skills/ee-low-power/references/rules.md#LPW-VER-002)、[LPW-VER-004](../skills/ee-low-power/references/rules.md#LPW-VER-004)、[ANA-ARC-008](../skills/ee-analog/references/rules.md#ANA-ARC-008)、[LPW-ARC-009](../skills/ee-low-power/references/rules.md#LPW-ARC-009)、[LPW-ARC-013](../skills/ee-low-power/references/rules.md#LPW-ARC-013)

### 人工 / 实测（163）

见各规则详情；此处不列。

## `review` — 人工评审

full 1 · partial 13 · manual 114

可用工具：JLCPCB online DFM / order-side checks（cloud）；Human / LLM review checklist（installed）

### 可完全自动化（1）

| ID | 规则 | 级别 | 检查 |
|---|---|---|---|
| [GEN-VER-009](../skills/ee-general-pcb/references/rules.md#GEN-VER-009) | EDA 文件进版本控制，忽略缓存并给下单版本打标签 | should | git ls-files 中不得出现 fp-info-cache、*-backups/、_autosave-*、~*.lck、*.kicad_prl 等； 项目文件、sym-lib-table、fp-lib-table 和项目库必须已被跟踪；每个已下单版本存在 git 标签，且标签对应的出图包清单文件存在。 |

### 可部分自动化（13）

[DFM-FLR-002](../skills/ee-dfm/references/rules.md#DFM-FLR-002)、[GEN-ARC-009](../skills/ee-general-pcb/references/rules.md#GEN-ARC-009)、[GEN-LIB-001](../skills/ee-general-pcb/references/rules.md#GEN-LIB-001)、[GEN-VER-008](../skills/ee-general-pcb/references/rules.md#GEN-VER-008)、[RF-ARC-002](../skills/ee-rf/references/rules.md#RF-ARC-002)、[ANA-PLN-002](../skills/ee-analog/references/rules.md#ANA-PLN-002)、[GEN-ARC-001](../skills/ee-general-pcb/references/rules.md#GEN-ARC-001)、[GEN-ARC-006](../skills/ee-general-pcb/references/rules.md#GEN-ARC-006)、[GEN-NET-006](../skills/ee-general-pcb/references/rules.md#GEN-NET-006)、[PWR-SCH-001](../skills/ee-power/references/rules.md#PWR-SCH-001)、[PWR-SCH-013](../skills/ee-power/references/rules.md#PWR-SCH-013)、[RF-ARC-001](../skills/ee-rf/references/rules.md#RF-ARC-001)、[RF-FLR-003](../skills/ee-rf/references/rules.md#RF-FLR-003)

### 人工 / 实测（114）

见各规则详情；此处不列。
