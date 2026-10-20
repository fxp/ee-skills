# 示例板（猫咪喂食器）— 相关规则清单

295 条，按级别（must → should → consider）再按领域排序。由 `catalog/*.yaml` 生成。

## must（81）

| ID | 规则 | 环节 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-ARC-007](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-007) | 按电源轨做功耗预算并计入峰值电流 | 架构与选型 | high | bom_check (full) |
| [GEN-ARC-009](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-009) | 核对每条数字链路的电平兼容与过压 | 架构与选型 | high | review (partial) |
| [GEN-FLR-007](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-007) | 板框闭合，铜到板边满足板厂最小间距 | 分区规划 | high | drc (full) |
| [GEN-LIB-001](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-001) | 符号的引脚号、名称和电气类型逐脚对照数据手册 | 符号封装库 | high | erc (full) |
| [GEN-LIB-002](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-002) | 焊盘图形取自厂商推荐或 IPC-7351 并1:1核对 | 符号封装库 | medium | geometry_script (partial) |
| [GEN-LIB-005](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-005) | 自动核对符号引脚与封装焊盘一致 | 符号封装库 | high | erc (full) |
| [GEN-NET-004](../../skills/ee-general-pcb/references/rules.md#GEN-NET-004) | 网络只在原理图里改，PCB 变更要反向标注 | 网表与约束 | high | netlist_diff (full) |
| [GEN-NET-005](../../skills/ee-general-pcb/references/rules.md#GEN-NET-005) | 原理图与 PCB 奇偶性检查要连警告一起设为门禁 | 网表与约束 | high | netlist_diff (full) |
| [GEN-PLN-009](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-009) | 天线下方和周围所有铜层禁布，铺铜前先画禁布区 | 平面与铺铜 | high | drc (full) |
| [GEN-RTE-002](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-002) | 信号线不得跨越参考平面的分割槽或缝隙 | 布线 | high | geometry_script (full) |
| [GEN-SCH-004](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-004) | 为每个输入定义确定电平，不允许悬空 | 原理图 | high | erc (partial) |
| [GEN-SCH-005](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-005) | 执行器驱动脚在上电和复位期间必须保持关断 | 原理图 | high | erc (full) |
| [GEN-SCH-006](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-006) | strapping / boot 引脚按手册配置且不加冲突负载 | 原理图 | high | erc (partial) |
| [GEN-SCH-007](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-007) | 复位 / 使能引脚不得悬空并满足上电时序 ⚠ | 原理图 | high | spice (partial) |
| [GEN-SCH-015](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-015) | 从数据手册典型电路出发并遵守元件限制说明 ⚠ | 原理图 | high | spice (partial) |
| [GEN-STK-005](../../skills/ee-general-pcb/references/rules.md#GEN-STK-005) | 按板厂能力设板级约束，不贴着极限设计 | 叠层与规则 | high | drc (full) |
| [GEN-VER-001](../../skills/ee-general-pcb/references/rules.md#GEN-VER-001) | ERC 零违规，例外逐条带理由，禁止整类静音 | 签核验证 | high | erc (full) |
| [GEN-VER-008](../../skills/ee-general-pcb/references/rules.md#GEN-VER-008) | 下单前按固定门禁逐项签核 | 签核验证 | medium | erc (full) |
| [PWR-ARC-002](../../skills/ee-power/references/rules.md#PWR-ARC-002) | 按最坏耗散核算 LDO 结温（SOT-223 AMS1117） ⚠ | 架构与选型 | high | bom_check (full) |
| [PWR-ARC-003](../../skills/ee-power/references/rules.md#PWR-ARC-003) | LDO 输入电压保持高于压差并留裕量 | 架构与选型 | high | spice (partial) |
| [PWR-ARC-006](../../skills/ee-power/references/rules.md#PWR-ARC-006) | 3.3 V 栅极驱动选用逻辑电平 MOSFET | 架构与选型 | high | bom_check (partial) |
| [PWR-LIB-001](../../skills/ee-power/references/rules.md#PWR-LIB-001) | 1117 类 SOT-223 的散热 tab 必须接 VOUT | 符号封装库 | high | netlist_diff (full) |
| [PWR-RTE-005](../../skills/ee-power/references/rules.md#PWR-RTE-005) | 大电流走线按 IPC-2152 和温升目标定宽 ⚠ | 布线 | high | geometry_script (full) |
| [PWR-RTE-007](../../skills/ee-power/references/rules.md#PWR-RTE-007) | 电流检测放大器输入走开尔文线接到分流电阻焊盘 | 布线 | high | geometry_script (full) |
| [PWR-SCH-007](../../skills/ee-power/references/rules.md#PWR-SCH-007) | AMS1117 输出用满足 ESR 窗口的钽电容 ⚠ | 原理图 | high | bom_check (partial) |
| [PWR-SCH-012](../../skills/ee-power/references/rules.md#PWR-SCH-012) | 电机两端并联续流二极管并核算额定值 | 原理图 | medium | netlist_diff (full) |
| [PWR-VER-002](../../skills/ee-power/references/rules.md#PWR-VER-002) | 负载阶跃响应与 LDO 稳定性的 SPICE 与实测 | 签核验证 | high | spice (full) |
| [PWR-VER-004](../../skills/ee-power/references/rules.md#PWR-VER-004) | 电机启动/堵转期间核算电源轨跌落与欠压余量 | 签核验证 | medium | spice (full) |
| [LPW-ARC-012](../../skills/ee-low-power/references/rules.md#LPW-ARC-012) | 无线突发电流下电源内阻不能把电压拉到下限以下 | 架构与选型 | high | bom_check (full) |
| [LPW-SCH-005](../../skills/ee-low-power/references/rules.md#LPW-SCH-005) | 掉电域的信号要隔离，防止经 I/O 二极管反向供电 | 原理图 | high | bom_check (partial) |
| [LPW-SCH-006](../../skills/ee-low-power/references/rules.md#LPW-SCH-006) | 使能与栅极控制线在复位和深睡期间要有确定电平 | 原理图 | high | bom_check (full) |
| [LPW-VER-003](../../skills/ee-low-power/references/rules.md#LPW-VER-003) | 在真实板、真实固件、真实电压下验收睡眠电流 | 签核验证 | high | bench (partial) |
| [LPW-VER-005](../../skills/ee-low-power/references/rules.md#LPW-VER-005) | 无线突发时在负载端实测电压跌落与纹波 | 签核验证 | high | bench (partial) |
| [RF-ARC-004](../../skills/ee-rf/references/rules.md#RF-ARC-004) | 不要改动预认证模组的天线与匹配配置 | 架构与选型 | high | bom_check (partial) |
| [RF-FLR-001](../../skills/ee-rf/references/rules.md#RF-FLR-001) | 天线放板边或板角，馈点贴近板边，辐射部分悬出板外 | 分区规划 | high | geometry_script (partial) |
| [RF-FLR-002](../../skills/ee-rf/references/rules.md#RF-FLR-002) | 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝 | 分区规划 | high | drc (full) |
| [ANA-ARC-003](../../skills/ee-analog/references/rules.md#ANA-ARC-003) | 核对电流检测增益档和输出量程 ⚠ | 架构与选型 | high | bom_check (full) |
| [ANA-NET-001](../../skills/ee-analog/references/rules.md#ANA-NET-001) | 分流电阻的 sense 抽头用独立网络 | 网表与约束 | high | netlist_diff (full) |
| [ANA-RTE-001](../../skills/ee-analog/references/rules.md#ANA-RTE-001) | 分流电阻到放大器必须用开尔文（四线）走线 | 布线 | high | geometry_script (full) |
| [ANA-VER-003](../../skills/ee-analog/references/rules.md#ANA-VER-003) | 稳定性签核：环路增益 + 阶跃，覆盖角点条件 | 签核验证 | high | spice (partial) |
| [ANA-VER-005](../../skills/ee-analog/references/rules.md#ANA-VER-005) | 实测 HX711 的 PD_SCK 时序，别触发掉电 | 签核验证 | high | bench (partial) |
| [HSD-RTE-002](../../skills/ee-high-speed/references/rules.md#HSD-RTE-002) | 按接口限定差分对内偏斜 ⚠ | 布线 | high | drc (full) |
| [HSD-RTE-005](../../skills/ee-high-speed/references/rules.md#HSD-RTE-005) | 高速线全程走在连续参考面上，远离参考面边缘和空洞 | 布线 | high | geometry_script (full) |
| [HSD-SCH-006](../../skills/ee-high-speed/references/rules.md#HSD-SCH-006) | USB-C 受电设备在 CC1、CC2 各接 5.1 kΩ 下拉 | 原理图 | high | erc (full) |
| [EMC-ARC-002](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-002) | ESD 目标等级按产品标准定，不靠 IC 的 HBM/CDM | 架构与选型 | high | bom_check (partial) |
| [EMC-FLR-003](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-003) | 连接器到 TVS 之间划 ESD 入口禁布区 | 分区规划 | high | geometry_script (full) |
| [EMC-PLC-001](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-001) | TVS 紧靠连接器引脚，被保护 IC 远离 TVS | 器件布局 | high | geometry_script (full) |
| [EMC-RTE-001](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-001) | 每条快速信号下方保持连续回流路径 | 布线 | high | geometry_script (full) |
| [EMC-RTE-003](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-003) | ESD 入口走线直通 TVS，无 stub、无过孔、拐角 ≤45° | 布线 | high | geometry_script (full) |
| [EMC-RTE-004](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-004) | TVS 地脚接同层地铺铜，紧邻过孔缝合到相邻地层 | 布线 | high | geometry_script (full) |
| [EMC-SCH-008](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-008) | TVS 按 VRWM、VBR、VC、IPP、电容选型 | 原理图 | high | bom_check (partial) |
| [EMC-SCH-009](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-009) | 所有用户可触及端口和电源入口都要有 ESD 路径 | 原理图 | high | geometry_script (partial) |
| [EMC-VER-002](../../skills/ee-emc-esd/references/rules.md#EMC-VER-002) | ESD 测试：金属壳打壳体接触放电，绝缘件打空气放电 | 签核验证 | high | bench (manual) |
| [HVS-ARC-001](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-001) | 先划分电压域：ELV/SELV 与危险电压 | 架构与选型 | medium | bom_check (partial) |
| [HVS-ARC-006](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-006) | 锂电池包必须有电芯级保护 IC | 架构与选型 | medium | bom_check (partial) |
| [HVS-RTE-001](../../skills/ee-hv-safety/references/rules.md#HVS-RTE-001) | 按表取爬电距离，加强绝缘加倍 ⚠ | 布线 | medium | drc (full) |
| [HVS-SCH-001](../../skills/ee-hv-safety/references/rules.md#HVS-SCH-001) | 电池输出串联保险丝或自恢复保险丝 | 原理图 | medium | bom_check (partial) |
| [THM-ARC-001](../../skills/ee-thermal/references/rules.md#THM-ARC-001) | 数据手册的 θJA 只对它的测试板成立 | 架构与选型 | high | thermal_sim (partial) |
| [THM-ARC-002](../../skills/ee-thermal/references/rules.md#THM-ARC-002) | 在最高环境温度下算每个发热件的结温 | 架构与选型 | high | thermal_sim (full) |
| [THM-ARC-003](../../skills/ee-thermal/references/rules.md#THM-ARC-003) | 线性稳压器的功耗按最坏输入电压和最大电流算 ⚠ | 架构与选型 | high | thermal_sim (full) |
| [THM-ARC-006](../../skills/ee-thermal/references/rules.md#THM-ARC-006) | MOSFET 导通损耗按热态 Rds(on) 算 | 架构与选型 | high | thermal_sim (full) |
| [THM-LIB-001](../../skills/ee-thermal/references/rules.md#THM-LIB-001) | 带裸露焊盘的封装必须有等大的散热焊盘并焊在板上 | 符号封装库 | high | geometry_script (partial) |
| [DFM-ARC-001](../../skills/ee-dfm/references/rules.md#DFM-ARC-001) | 按所选 JLC 贴片档位的能力边界选型 ⚠ | 架构与选型 | high | bom_check (partial) |
| [DFM-ARC-004](../../skills/ee-dfm/references/rules.md#DFM-ARC-004) | 器件必须耐受 JLC 回流峰值并核对 MSL | 架构与选型 | medium | bom_check (partial) |
| [DFM-LIB-002](../../skills/ee-dfm/references/rules.md#DFM-LIB-002) | 两端片式元件的两个焊盘必须完全对称 | 符号封装库 | medium | geometry_script (full) |
| [DFM-LIB-006](../../skills/ee-dfm/references/rules.md#DFM-LIB-006) | 封装必须与数据手册极性一致并有可见的 1 脚 / 极性标记 | 符号封装库 | medium | geometry_script (partial) |
| [DFM-MFG-001](../../skills/ee-dfm/references/rules.md#DFM-MFG-001) | Gerber 输出集合完整、带 X2 属性、单位为 mm | 出图与制造 | high | geometry_script (full) |
| [DFM-MFG-002](../../skills/ee-dfm/references/rules.md#DFM-MFG-002) | 钻孔文件按 PTH / NPTH 分开并用成品孔径 | 出图与制造 | high | geometry_script (full) |
| [DFM-MFG-003](../../skills/ee-dfm/references/rules.md#DFM-MFG-003) | BOM 文件格式与内容 | 出图与制造 | medium | bom_check (full) |
| [DFM-MFG-004](../../skills/ee-dfm/references/rules.md#DFM-MFG-004) | CPL 坐标文件的列、单位与方向 ⚠ | 出图与制造 | medium | geometry_script (full) |
| [DFM-MFG-005](../../skills/ee-dfm/references/rules.md#DFM-MFG-005) | 逐个核对 JLC 库与 KiCad 封装的旋转差 | 出图与制造 | medium | bom_check (partial) |
| [DFM-NET-001](../../skills/ee-dfm/references/rules.md#DFM-NET-001) | BOM、CPL 与 PCB 必须一一对应 | 网表与约束 | medium | netlist_diff (full) |
| [DFM-PLC-002](../../skills/ee-dfm/references/rules.md#DFM-PLC-002) | 封装 courtyard 不得重叠 ⚠ | 器件布局 | low | drc (full) |
| [DFM-PLN-001](../../skills/ee-dfm/references/rules.md#DFM-PLN-001) | 铜皮与走线到板边、V-cut 线的距离 | 平面与铺铜 | high | drc (full) |
| [DFM-RTE-002](../../skills/ee-dfm/references/rules.md#DFM-RTE-002) | 2 层板不要在 SMD 焊盘里放开口过孔 ⚠ | 布线 | medium | geometry_script (full) |
| [DFM-STK-001](../../skills/ee-dfm/references/rules.md#DFM-STK-001) | DRC 的线宽线距不低于板厂能力并留余量 ⚠ | 叠层与规则 | high | drc (full) |
| [DFM-STK-002](../../skills/ee-dfm/references/rules.md#DFM-STK-002) | 钻孔、过孔与孔环的最小值 ⚠ | 叠层与规则 | high | drc (full) |
| [DFM-STK-003](../../skills/ee-dfm/references/rules.md#DFM-STK-003) | 焊盘与走线、孔与走线的间距下限 | 叠层与规则 | high | drc (full) |
| [DFM-STK-004](../../skills/ee-dfm/references/rules.md#DFM-STK-004) | 阻焊桥与阻焊开口的最小值 ⚠ | 叠层与规则 | high | drc (full) |
| [DFM-VER-001](../../skills/ee-dfm/references/rules.md#DFM-VER-001) | 用板厂能力而不是 EDA 默认值跑 DRC | 签核验证 | high | drc (full) |
| [DFM-VER-003](../../skills/ee-dfm/references/rules.md#DFM-VER-003) | 下单前核对 CPL 与板文件的几何一致 | 签核验证 | medium | geometry_script (full) |

## should（183）

| ID | 规则 | 环节 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-ARC-002](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-002) | 按产品等级对元件电压 / 电流 / 功率降额 ⚠ | 架构与选型 | high | bom_check (partial) |
| [GEN-ARC-003](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-003) | 陶瓷电容按直流偏压后的有效容值取值 | 架构与选型 | high | bom_check (partial) |
| [GEN-ARC-004](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-004) | 选型时核对生命周期并为关键件备好替代料 ⚠ | 架构与选型 | medium | bom_check (partial) |
| [GEN-ARC-005](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-005) | 封装与器件选择要匹配贴片厂的库和工艺 | 架构与选型 | high | bom_check (full) |
| [GEN-ARC-006](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-006) | MCU / 模块选型前做引脚预算并剔除受限引脚 | 架构与选型 | high | review (partial) |
| [GEN-ARC-008](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-008) | 先定上电时序与复位释放条件 | 架构与选型 | high | spice (partial) |
| [GEN-ARC-010](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-010) | 连接器按触点数与温度折算电流并防插错 ⚠ | 架构与选型 | medium | bom_check (partial) |
| [GEN-FLR-001](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-001) | 按功能和噪声等级分区，快逻辑靠近电源、模拟最远 | 分区规划 | high | geometry_script (partial) |
| [GEN-FLR-002](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-002) | 电源入口、稳压器、MCU 依次相邻，地在三者间单点汇合 | 分区规划 | medium | geometry_script (partial) |
| [GEN-FLR-003](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-003) | 各子系统的走线只在自己的分区内，跨区只走指定通道 | 分区规划 | high | geometry_script (full) |
| [GEN-FLR-004](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-004) | 大电流路径和开关环路远离敏感小信号 | 分区规划 | medium | geometry_script (partial) |
| [GEN-FLR-005](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-005) | 连接器集中在板边，噪声源与晶振远离连接器 | 分区规划 | medium | geometry_script (partial) |
| [GEN-FLR-006](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-006) | 带板载天线的模块放在板边，天线区空出 ⚠ | 分区规划 | high | geometry_script (partial) |
| [GEN-LIB-004](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-004) | 带散热焊盘的封装补全焊盘编号、过孔与钢网开窗 ⚠ | 符号封装库 | high | geometry_script (partial) |
| [GEN-LIB-006](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-006) | 3D 模型对准焊盘并核对与贴片厂的旋转约定 | 符号封装库 | medium | geometry_script (partial) |
| [GEN-LIB-007](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-007) | 库只有一个来源：项目内库表且纳入版本控制 | 符号封装库 | high | erc (full) |
| [GEN-LIB-008](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-008) | 库器件携带制造商、型号、数据手册和厂方料号 | 符号封装库 | high | bom_check (full) |
| [GEN-NET-002](../../skills/ee-general-pcb/references/rules.md#GEN-NET-002) | 网络类承载约束并保证每个网络都有归属 | 网表与约束 | high | erc (full) |
| [GEN-NET-006](../../skills/ee-general-pcb/references/rules.md#GEN-NET-006) | 出图前做网表差异对比并附 IPC-D-356 | 网表与约束 | medium | netlist_diff (full) |
| [GEN-PLC-002](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-002) | 每个电源引脚一个去耦电容，小容值最近 | 器件布局 | high | geometry_script (full) |
| [GEN-PLC-003](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-003) | 去耦电容地焊盘就近接地，用过孔或直连地铜 | 器件布局 | high | geometry_script (full) |
| [GEN-PLC-004](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-004) | 电源电流必须穿过去耦电容焊盘再到引脚 | 器件布局 | medium | geometry_script (partial) |
| [GEN-PLC-005](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-005) | 电源入口和稳压器处放大电容，模块进线前放 10 µF | 器件布局 | medium | geometry_script (full) |
| [GEN-PLC-009](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-009) | ESD / TVS 器件紧靠连接器，保护对象放得更远 ⚠ | 器件布局 | high | geometry_script (full) |
| [GEN-PLN-001](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-001) | 先保证完整地平面，地层不走线、不被过孔排切成槽 | 平面与铺铜 | high | geometry_script (full) |
| [GEN-PLN-002](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-002) | 默认用一整块地平面，靠分区而不是分割隔离模拟数字 ⚠ | 平面与铺铜 | high | geometry_script (full) |
| [GEN-PLN-004](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-004) | 2 层板用地网格 / 整面地铺铜并多打缝合过孔 | 平面与铺铜 | high | geometry_script (full) |
| [GEN-PLN-005](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-005) | MCU 下方做地岛，去耦和晶振的地接在上面 ⚠ | 平面与铺铜 | medium | geometry_script (full) |
| [GEN-PLN-006](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-006) | 地铜用缝合过孔连接，间距不超过 λ/20 ⚠ | 平面与铺铜 | medium | geometry_script (full) |
| [GEN-PLN-007](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-007) | 去掉死铜和孤岛，不让铺铜悬空 ⚠ | 平面与铺铜 | medium | drc (full) |
| [GEN-PLN-008](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-008) | 通孔焊盘用热焊盘，SMD 地焊盘和去耦地直接连 ⚠ | 平面与铺铜 | medium | drc (full) |
| [GEN-PLN-011](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-011) | 芯片底部接地焊盘用多个过孔接地平面 | 平面与铺铜 | high | geometry_script (full) |
| [GEN-RTE-001](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-001) | 每条信号线下方保持连续的回流参考铜 | 布线 | high | geometry_script (full) |
| [GEN-RTE-003](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-003) | 信号换层时在过孔旁放地过孔提供回流 | 布线 | medium | geometry_script (partial) |
| [GEN-RTE-004](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-004) | 电源线与地线并行贴近，环路长宽比不超过 3:1 | 布线 | high | geometry_script (full) |
| [GEN-RTE-005](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-005) | 电源分配单点或星形，别串成菊花链 ⚠ | 布线 | high | geometry_script (partial) |
| [GEN-RTE-010](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-010) | 干扰源与敏感线间距至少 3 倍线宽 ⚠ | 布线 | medium | drc (full) |
| [GEN-RTE-014](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-014) | 连接器先到 TVS 再到 IC，路径短直无桩无过孔 | 布线 | high | geometry_script (full) |
| [GEN-SCH-003](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-003) | 每个电源引脚（对）都画出规定值的去耦电容 ⚠ | 原理图 | high | erc (partial) |
| [GEN-SCH-008](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-008) | 未用引脚按手册处理并显式标注 | 原理图 | high | erc (full) |
| [GEN-SCH-010](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-010) | 为每个可编程器件引出调试 / 烧录接口 | 原理图 | medium | erc (partial) |
| [GEN-SCH-011](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-011) | 在原理图中为电源轨和关键信号预留测试点 ⚠ | 原理图 | medium | erc (full) |
| [GEN-SCH-013](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-013) | 可选件和调试件标记 DNP 并保证属性两边一致 | 原理图 | high | bom_check (full) |
| [GEN-SCH-014](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-014) | 每个对外连接器线路都要有保护决策 ⚠ | 原理图 | medium | erc (partial) |
| [GEN-SCH-016](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-016) | 关键位置标注容差、耐压和取值依据 | 原理图 | medium | bom_check (partial) |
| [GEN-STK-001](../../skills/ee-general-pcb/references/rules.md#GEN-STK-001) | 按最高频率与辐射风险选层数，2 层板要补偿 ⚠ | 叠层与规则 | medium | geometry_script (partial) |
| [GEN-STK-004](../../skills/ee-general-pcb/references/rules.md#GEN-STK-004) | 2 层板：底层做地参考，元件只放顶层 | 叠层与规则 | high | geometry_script (full) |
| [GEN-STK-006](../../skills/ee-general-pcb/references/rules.md#GEN-STK-006) | 网络类宽度只是默认值，必须用自定义规则落成 DRC | 叠层与规则 | high | drc (full) |
| [GEN-STK-007](../../skills/ee-general-pcb/references/rules.md#GEN-STK-007) | 按电流和温升算线宽，IPC-2221 作保守下限 ⚠ | 叠层与规则 | medium | tline_calc (full) |
| [GEN-STK-008](../../skills/ee-general-pcb/references/rules.md#GEN-STK-008) | 载流层间过孔至少两个，并按孔壁截面估算电流 ⚠ | 叠层与规则 | medium | geometry_script (partial) |
| [GEN-VER-002](../../skills/ee-general-pcb/references/rules.md#GEN-VER-002) | 按类别理解 ERC 违规，PWR_FLAG 只放在真实电源源头 | 签核验证 | high | erc (partial) |
| [GEN-VER-007](../../skills/ee-general-pcb/references/rules.md#GEN-VER-007) | 首次上电按步骤逐轨进行并限流 | 签核验证 | medium | bench (manual) |
| [PWR-ARC-001](../../skills/ee-power/references/rules.md#PWR-ARC-001) | 3.3 V 主电源按模块峰值电流留足裕量 | 架构与选型 | high | bom_check (partial) |
| [PWR-ARC-004](../../skills/ee-power/references/rules.md#PWR-ARC-004) | 全陶瓷输出场合选「陶瓷稳定」型 LDO | 架构与选型 | high | bom_check (partial) |
| [PWR-ARC-007](../../skills/ee-power/references/rules.md#PWR-ARC-007) | 电机 MOSFET 按堵转电流核算导通损耗和结温 | 架构与选型 | high | bom_check (full) |
| [PWR-FLR-001](../../skills/ee-power/references/rules.md#PWR-FLR-001) | 电机/开关电源功率区与模拟、射频区分区 | 分区规划 | medium | geometry_script (partial) |
| [PWR-FLR-002](../../skills/ee-power/references/rules.md#PWR-FLR-002) | 电源入口按防护、储能、稳压顺序布局 | 分区规划 | high | geometry_script (partial) |
| [PWR-LIB-002](../../skills/ee-power/references/rules.md#PWR-LIB-002) | 四端子开尔文分流电阻封装要分开力端与感测端 | 符号封装库 | high | netlist_diff (full) |
| [PWR-PLC-007](../../skills/ee-power/references/rules.md#PWR-PLC-007) | LDO 输入输出电容靠近引脚，负载走线宽 | 器件布局 | medium | geometry_script (partial) |
| [PWR-PLN-001](../../skills/ee-power/references/rules.md#PWR-PLN-001) | 变换器热回路下方保持连续地平面 ⚠ | 平面与铺铜 | medium | geometry_script (partial) |
| [PWR-PLN-004](../../skills/ee-power/references/rules.md#PWR-PLN-004) | 电机电流回路用独立地铜，单点接到逻辑地 | 平面与铺铜 | medium | geometry_script (partial) |
| [PWR-RTE-006](../../skills/ee-power/references/rules.md#PWR-RTE-006) | 换层大电流路径按电流估算并联过孔数量 ⚠ | 布线 | medium | geometry_script (full) |
| [PWR-RTE-008](../../skills/ee-power/references/rules.md#PWR-RTE-008) | 3.3 V 电源走线按 Espressif 最小线宽 | 布线 | high | geometry_script (full) |
| [PWR-SCH-001](../../skills/ee-power/references/rules.md#PWR-SCH-001) | 保险丝（PPTC）放在 TVS 上游 ⚠ | 原理图 | medium | review (partial) |
| [PWR-SCH-002](../../skills/ee-power/references/rules.md#PWR-SCH-002) | 提供真正串联的反接保护，并核算反接时的应力 | 原理图 | medium | spice (partial) |
| [PWR-SCH-003](../../skills/ee-power/references/rules.md#PWR-SCH-003) | PPTC 按最高环境温度下的保持电流选型 | 原理图 | medium | bom_check (partial) |
| [PWR-SCH-004](../../skills/ee-power/references/rules.md#PWR-SCH-004) | TVS 按击穿电压、钳位电压、峰值电流三条选型 | 原理图 | high | bom_check (full) |
| [PWR-SCH-005](../../skills/ee-power/references/rules.md#PWR-SCH-005) | 线缆热插拔的输入端抑制陶瓷电容谐振过冲 | 原理图 | medium | spice (partial) |
| [PWR-SCH-006](../../skills/ee-power/references/rules.md#PWR-SCH-006) | 陶瓷电容按直流偏置、温度、公差降额后再核算 | 原理图 | high | bom_check (partial) |
| [PWR-SCH-008](../../skills/ee-power/references/rules.md#PWR-SCH-008) | 限制 LDO 输出端并联的小陶瓷旁路电容 | 原理图 | high | spice (partial) |
| [PWR-SCH-011](../../skills/ee-power/references/rules.md#PWR-SCH-011) | 电机 MOSFET 栅极加下拉电阻和串联电阻 | 原理图 | high | erc (full) |
| [PWR-SCH-013](../../skills/ee-power/references/rules.md#PWR-SCH-013) | 有刷电机接线端并联 0.1 uF 陶瓷电容 | 原理图 | medium | review (partial) |
| [PWR-SCH-014](../../skills/ee-power/references/rules.md#PWR-SCH-014) | 上电复位时序：电源稳定后再使能，慢速斜坡加监控芯片 | 原理图 | high | spice (full) |
| [PWR-SCH-015](../../skills/ee-power/references/rules.md#PWR-SCH-015) | 电源上的磁珠/LC 滤波器按偏置降额并阻尼 | 原理图 | medium | bom_check (full) |
| [PWR-SCH-016](../../skills/ee-power/references/rules.md#PWR-SCH-016) | 反馈分压与基准容差下的输出电压最坏情况 | 原理图 | medium | spice (full) |
| [PWR-VER-003](../../skills/ee-power/references/rules.md#PWR-VER-003) | 上电浪涌电流与热插拔电压过冲仿真 | 签核验证 | medium | spice (full) |
| [LPW-ARC-001](../../skills/ee-low-power/references/rules.md#LPW-ARC-001) | 先建立分状态的平均电流与电荷预算 | 架构与选型 | high | bom_check (partial) |
| [LPW-ARC-002](../../skills/ee-low-power/references/rules.md#LPW-ARC-002) | 用输入端折算公式核算常开轨待机电流 | 架构与选型 | high | bom_check (partial) |
| [LPW-ARC-005](../../skills/ee-low-power/references/rules.md#LPW-ARC-005) | 按实际待机负载选稳压器，而不是只看标称 Iq | 架构与选型 | high | bom_check (partial) |
| [LPW-ARC-006](../../skills/ee-low-power/references/rules.md#LPW-ARC-006) | 线性稳压器的 Iq 是睡眠电流的下限 ⚠ | 架构与选型 | high | bom_check (partial) |
| [LPW-ARC-007](../../skills/ee-low-power/references/rules.md#LPW-ARC-007) | 用负载开关划分电源域，切断高漏电子系统 | 架构与选型 | high | bom_check (partial) |
| [LPW-ARC-008](../../skills/ee-low-power/references/rules.md#LPW-ARC-008) | 按唤醒源与保持内容选 MCU 睡眠模式（ESP32-C3） | 架构与选型 | high | netlist_diff (full) |
| [LPW-MFG-002](../../skills/ee-low-power/references/rules.md#LPW-MFG-002) | 预留可单独测量睡眠电流的断点或测试点 | 出图与制造 | medium | bom_check (full) |
| [LPW-NET-001](../../skills/ee-low-power/references/rules.md#LPW-NET-001) | 用 BOM 加网表脚本核算常开轨漏电与 Iq 总和 | 网表与约束 | medium | bom_check (partial) |
| [LPW-PLC-001](../../skills/ee-low-power/references/rules.md#LPW-PLC-001) | 突发负载的大电容放在电池或电源入口侧，按总电荷定容 | 器件布局 | high | spice (partial) |
| [LPW-RTE-002](../../skills/ee-low-power/references/rules.md#LPW-RTE-002) | 突发电流路径要核算走线与过孔的 IR 压降 | 布线 | medium | geometry_script (full) |
| [LPW-SCH-001](../../skills/ee-low-power/references/rules.md#LPW-SCH-001) | 核算常开轨上每条电阻支路的静态电流（V/R） | 原理图 | high | bom_check (partial) |
| [LPW-SCH-002](../../skills/ee-low-power/references/rules.md#LPW-SCH-002) | 睡眠期 GPIO 电平与外部上下拉必须一致 | 原理图 | medium | netlist_diff (partial) |
| [LPW-SCH-003](../../skills/ee-low-power/references/rules.md#LPW-SCH-003) | 未用引脚不得悬空，按芯片规定处理 ⚠ | 原理图 | high | erc (partial) |
| [LPW-SCH-008](../../skills/ee-low-power/references/rules.md#LPW-SCH-008) | 指示灯是睡眠电流大户，要由 GPIO 驱动并在睡眠中熄灭 | 原理图 | medium | bom_check (full) |
| [LPW-SCH-009](../../skills/ee-low-power/references/rules.md#LPW-SCH-009) | 外设用自带掉电模式或断电，并保证睡眠中保持该状态（HX711） | 原理图 | high | netlist_diff (partial) |
| [LPW-SCH-010](../../skills/ee-low-power/references/rules.md#LPW-SCH-010) | INA199 没有关断脚，睡眠预算要含其 Iq 与 1 MΩ 泄漏路径 | 原理图 | high | bom_check (partial) |
| [LPW-SCH-013](../../skills/ee-low-power/references/rules.md#LPW-SCH-013) | 缓慢升降或不稳定的电源要用电压监控器复位 | 原理图 | high | bench (partial) |
| [LPW-SCH-014](../../skills/ee-low-power/references/rules.md#LPW-SCH-014) | 常开轨和备份轨上的大电容要计漏电，优先低漏电类型 | 原理图 | medium | bom_check (partial) |
| [LPW-VER-001](../../skills/ee-low-power/references/rules.md#LPW-VER-001) | 选对测睡眠电流的仪表：burden 电压、量程与分辨率 | 签核验证 | high | bench (manual) |
| [LPW-VER-002](../../skills/ee-low-power/references/rules.md#LPW-VER-002) | 平均电流用整个占空周期的累计电荷来测 | 签核验证 | high | bench (partial) |
| [RF-ARC-003](../../skills/ee-rf/references/rules.md#RF-ARC-003) | 优先选预认证射频模组，量大再做分立射频 | 架构与选型 | medium | bom_check (partial) |
| [RF-FLR-003](../../skills/ee-rf/references/rules.md#RF-FLR-003) | 外壳内天线周围留净空，金属件远离天线 ⚠ | 分区规划 | high | review (partial) |
| [RF-FLR-004](../../skills/ee-rf/references/rules.md#RF-FLR-004) | 天线远离晶振、高速时钟、开关电源、电机以及 USB/UART | 分区规划 | medium | geometry_script (partial) |
| [RF-FLR-005](../../skills/ee-rf/references/rules.md#RF-FLR-005) | 单极类天线按厂商参考板提供足够的地平面 | 分区规划 | high | geometry_script (partial) |
| [RF-LIB-001](../../skills/ee-rf/references/rules.md#RF-LIB-001) | 天线/模组封装自带厂商禁布区并保持不改 | 符号封装库 | high | drc (full) |
| [RF-SCH-007](../../skills/ee-rf/references/rules.md#RF-SCH-007) | 模组 3V3 脚旁放 10 µF + 0.1 µF，扛住发射电流尖峰 | 原理图 | high | spice (partial) |
| [RF-STK-003](../../skills/ee-rf/references/rules.md#RF-STK-003) | 分立射频优先 4 层；2 层板底层须为整块实心地 ⚠ | 叠层与规则 | high | geometry_script (full) |
| [RF-VER-006](../../skills/ee-rf/references/rules.md#RF-VER-006) | 在最终产品上实测吞吐量与通信距离 | 签核验证 | high | bench (manual) |
| [ANA-ARC-001](../../skills/ee-analog/references/rules.md#ANA-ARC-001) | 选型前先做误差预算（失调/漂移/增益/容差） | 架构与选型 | high | bom_check (partial) |
| [ANA-ARC-002](../../skills/ee-analog/references/rules.md#ANA-ARC-002) | 按失调与量程选分流电阻阻值 ⚠ | 架构与选型 | high | bom_check (partial) |
| [ANA-ARC-005](../../skills/ee-analog/references/rules.md#ANA-ARC-005) | 放大器带宽/建立时间要小于最短导通时间 | 架构与选型 | high | spice (partial) |
| [ANA-ARC-007](../../skills/ee-analog/references/rules.md#ANA-ARC-007) | ESP32-C3 内置 ADC 的误差与使用边界 | 架构与选型 | high | bench (partial) |
| [ANA-ARC-009](../../skills/ee-analog/references/rules.md#ANA-ARC-009) | 称重电桥：排查引线电阻对比例测量的破坏 | 架构与选型 | high | bench (manual) |
| [ANA-FLR-001](../../skills/ee-analog/references/rules.md#ANA-FLR-001) | 把模拟区与数字/射频/开关区分开 | 分区规划 | high | geometry_script (full) |
| [ANA-FLR-002](../../skills/ee-analog/references/rules.md#ANA-FLR-002) | 精密元件远离热源和板边气流 | 分区规划 | high | geometry_script (partial) |
| [ANA-LIB-001](../../skills/ee-analog/references/rules.md#ANA-LIB-001) | 分流电阻用四端子封装并保留开尔文焊盘 | 符号封装库 | high | geometry_script (full) |
| [ANA-MFG-001](../../skills/ee-analog/references/rules.md#ANA-MFG-001) | 出厂/首次上电做零点与增益两点校准 | 出图与制造 | high | bench (partial) |
| [ANA-PLC-001](../../skills/ee-analog/references/rules.md#ANA-PLC-001) | 分流电阻紧贴电流检测放大器 | 器件布局 | high | geometry_script (full) |
| [ANA-PLC-002](../../skills/ee-analog/references/rules.md#ANA-PLC-002) | 电流检测放大器的旁路电容贴脚且不打孔 | 器件布局 | high | geometry_script (full) |
| [ANA-PLN-001](../../skills/ee-analog/references/rules.md#ANA-PLN-001) | 整块地平面 + 分区走线，优先于分割 AGND/DGND ⚠ | 平面与铺铜 | high | geometry_script (partial) |
| [ANA-RTE-002](../../skills/ee-analog/references/rules.md#ANA-RTE-002) | 两条 sense 线等长、等宽、同层并排 | 布线 | high | geometry_script (full) |
| [ANA-RTE-003](../../skills/ee-analog/references/rules.md#ANA-RTE-003) | 模拟输入走线远离开关节点和数字信号 | 布线 | high | drc (full) |
| [ANA-RTE-005](../../skills/ee-analog/references/rules.md#ANA-RTE-005) | 敏感模拟线下方保持连续的返回平面 | 布线 | high | geometry_script (full) |
| [ANA-SCH-003](../../skills/ee-analog/references/rules.md#ANA-SCH-003) | INA199 输入滤波：串联电阻 ≤ 10 Ω | 原理图 | high | bom_check (full) |
| [ANA-SCH-004](../../skills/ee-analog/references/rules.md#ANA-SCH-004) | REF 接地时给零电流区留死区余量 | 原理图 | high | spice (partial) |
| [ANA-SCH-005](../../skills/ee-analog/references/rules.md#ANA-SCH-005) | INA199 输出到 ADC 引脚：先串电阻再接 100 nF ⚠ | 原理图 | medium | spice (partial) |
| [ANA-SCH-007](../../skills/ee-analog/references/rules.md#ANA-SCH-007) | HX711 的数字电源跟随 MCU，模拟电源去耦 | 原理图 | high | review (manual) |
| [ANA-SCH-008](../../skills/ee-analog/references/rules.md#ANA-SCH-008) | HX711 输入共模电压要落在允许范围内 | 原理图 | high | bom_check (partial) |
| [ANA-VER-001](../../skills/ee-analog/references/rules.md#ANA-VER-001) | SPICE 做最坏情况 + Monte Carlo + 温度扫描对账 | 签核验证 | medium | spice (partial) |
| [ANA-VER-004](../../skills/ee-analog/references/rules.md#ANA-VER-004) | 输入短路噪声实测与有效分辨率 | 签核验证 | high | bench (partial) |
| [HSD-ARC-003](../../skills/ee-high-speed/references/rules.md#HSD-ARC-003) | 高速接口板按速率确定最少层数 ⚠ | 架构与选型 | medium | review (manual) |
| [HSD-PLC-001](../../skills/ee-high-speed/references/rules.md#HSD-PLC-001) | 连接器侧保护链按 ESD、共模滤波、隔直电容的顺序放置 ⚠ | 器件布局 | high | geometry_script (partial) |
| [HSD-RTE-006](../../skills/ee-high-speed/references/rules.md#HSD-RTE-006) | 换层过孔旁就近放地缝合过孔，且差分两线过孔对称 | 布线 | high | geometry_script (full) |
| [HSD-RTE-014](../../skills/ee-high-speed/references/rules.md#HSD-RTE-014) | 2 层板上的 FS USB 差分线：短、等长、下方整面地 ⚠ | 布线 | medium | tline_calc (partial) |
| [HSD-SCH-003](../../skills/ee-high-speed/references/rules.md#HSD-SCH-003) | 原生 USB 数据线预留串联电阻与对地电容位 ⚠ | 原理图 | high | erc (partial) |
| [HSD-SCH-005](../../skills/ee-high-speed/references/rules.md#HSD-SCH-005) | 按接口速率选择 ESD 器件的电容、工作电压与等级 | 原理图 | high | bom_check (partial) |
| [HSD-SCH-007](../../skills/ee-high-speed/references/rules.md#HSD-SCH-007) | USB VBUS 加 TVS，钳位电压低于下游耐压并按 PD 电压档选型 | 原理图 | high | bom_check (partial) |
| [EMC-ARC-001](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-001) | 按源—路径—受害者拆解每个 EMC 问题 | 架构与选型 | high | review (manual) |
| [EMC-ARC-003](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-003) | 按端口确定 EFT 与浪涌等级和性能判据 | 架构与选型 | high | review (manual) |
| [EMC-ARC-004](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-004) | 边沿速率与时钟频率取满足时序的最慢值 | 架构与选型 | high | si_sim (partial) |
| [EMC-FLR-001](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-001) | 按功能分区，高速逻辑靠电源入口，模拟远离 | 分区规划 | high | geometry_script (partial) |
| [EMC-FLR-002](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-002) | 连接器集中在板边一侧，ESD 敏感电路放中央 | 分区规划 | high | geometry_script (partial) |
| [EMC-FLR-004](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-004) | 电机/继电器/驱动区与 MCU 和模拟采样区分开 | 分区规划 | medium | geometry_script (partial) |
| [EMC-FLR-005](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-005) | MCU 靠稳压器，稳压器靠供电入口，地在三者间单点参考 ⚠ | 分区规划 | medium | geometry_script (partial) |
| [EMC-PLC-002](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-002) | 阻尼电阻贴驱动脚，I/O 旁路电容贴连接器 | 器件布局 | high | geometry_script (partial) |
| [EMC-PLC-003](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-003) | 去耦电容贴电源脚，回路面积最小 | 器件布局 | high | geometry_script (full) |
| [EMC-PLC-004](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-004) | 电机抑制电容和续流件贴电机/感性负载 | 器件布局 | medium | geometry_script (partial) |
| [EMC-PLN-001](../../skills/ee-emc-esd/references/rules.md#EMC-PLN-001) | 两层板地铺铜栅格化，消除只有一端连接的地岛 | 平面与铺铜 | high | geometry_script (full) |
| [EMC-PLN-003](../../skills/ee-emc-esd/references/rules.md#EMC-PLN-003) | 机壳/屏蔽地铜区：宽、短、至少两颗螺丝 | 平面与铺铜 | high | geometry_script (partial) |
| [EMC-RTE-005](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-005) | 快沿/时钟走线要短，超过阈值要端接 | 布线 | high | geometry_script (full) |
| [EMC-SCH-001](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-001) | MCU 输出/时钟脚串联阻尼电阻 ⚠ | 原理图 | high | geometry_script (partial) |
| [EMC-SCH-002](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-002) | EN/复位类敏感脚：短走线加 RC，不加大电容 | 原理图 | high | erc (partial) |
| [EMC-SCH-006](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-006) | 出机壳的线在连接器处加小电容到机壳/屏蔽地 | 原理图 | high | geometry_script (partial) |
| [EMC-SCH-010](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-010) | 保险丝与 TVS 的先后顺序要显式决定 ⚠ | 原理图 | medium | review (manual) |
| [EMC-SCH-012](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-012) | 电机端子并联陶瓷电容（跨端子 + 对外壳） ⚠ | 原理图 | medium | spice (partial) |
| [EMC-SCH-013](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-013) | 感性负载必须有续流/钳位路径 | 原理图 | medium | spice (full) |
| [EMC-STK-001](../../skills/ee-emc-esd/references/rules.md#EMC-STK-001) | 两层板：栅格化地 + 电源地叠放，逼近四层效果 | 叠层与规则 | high | geometry_script (partial) |
| [EMC-VER-001](../../skills/ee-emc-esd/references/rules.md#EMC-VER-001) | 用 LISN 做传导发射预兼容，两根线分别扫 | 签核验证 | medium | emc_precompliance (manual) |
| [EMC-VER-003](../../skills/ee-emc-esd/references/rules.md#EMC-VER-003) | ESD 仿真：IEC 枪模型 + TVS + 寄生电感估算 VESD | 签核验证 | high | spice (partial) |
| [EMC-VER-005](../../skills/ee-emc-esd/references/rules.md#EMC-VER-005) | 电机启停/堵转时在板上抓供电、EN 和采样 | 签核验证 | medium | bench (manual) |
| [HVS-STK-002](../../skills/ee-hv-safety/references/rules.md#HVS-STK-002) | 低压（非安规）间距按 IPC-2221B 表设 DRC | 叠层与规则 | medium | drc (full) |
| [THM-ARC-004](../../skills/ee-thermal/references/rules.md#THM-ARC-004) | 2 层板上预期 θJA 比 4 层测试板的数据差 | 架构与选型 | medium | thermal_sim (partial) |
| [THM-ARC-008](../../skills/ee-thermal/references/rules.md#THM-ARC-008) | 铝电解电容按本体温度算寿命并远离热源 ⚠ | 架构与选型 | medium | bom_check (partial) |
| [THM-PLC-001](../../skills/ee-thermal/references/rules.md#THM-PLC-001) | 热源与怕热元件分开放 ⚠ | 器件布局 | medium | geometry_script (partial) |
| [THM-PLC-002](../../skills/ee-thermal/references/rules.md#THM-PLC-002) | 外壳内的环境温度和空气流动要按实际假设 | 器件布局 | medium | bench (manual) |
| [THM-PLN-001](../../skills/ee-thermal/references/rules.md#THM-PLN-001) | SOT-223 的散热铜面积要按目标 θJA 来定 ⚠ | 平面与铺铜 | high | geometry_script (partial) |
| [THM-PLN-002](../../skills/ee-thermal/references/rules.md#THM-PLN-002) | 散热铜优先放在元件面，再用过孔连到背面 | 平面与铺铜 | high | geometry_script (partial) |
| [THM-RTE-001](../../skills/ee-thermal/references/rules.md#THM-RTE-001) | 大电流走线按 IPC-2152 的温升来定宽 ⚠ | 布线 | low | tline_calc (full) |
| [THM-RTE-002](../../skills/ee-thermal/references/rules.md#THM-RTE-002) | 散热过孔的孔径、间距与数量 | 布线 | high | geometry_script (full) |
| [THM-VER-004](../../skills/ee-thermal/references/rules.md#THM-VER-004) | 在最坏工况、盖好外壳后做稳态热测试 ⚠ | 签核验证 | medium | bench (manual) |
| [DFM-ARC-002](../../skills/ee-dfm/references/rules.md#DFM-ARC-002) | 优先选 JLC 基础库 / Preferred 器件 ⚠ | 架构与选型 | medium | bom_check (partial) |
| [DFM-ARC-003](../../skills/ee-dfm/references/rules.md#DFM-ARC-003) | 下单前核对每个料号的库存与封装匹配 | 架构与选型 | medium | bom_check (partial) |
| [DFM-FLR-001](../../skills/ee-dfm/references/rules.md#DFM-FLR-001) | 为贴片预留工艺边、工装孔与 MARK 点 ⚠ | 分区规划 | medium | geometry_script (partial) |
| [DFM-FLR-005](../../skills/ee-dfm/references/rules.md#DFM-FLR-005) | 外壳与安装孔的配合要吃下制造公差 | 分区规划 | medium | geometry_script (partial) |
| [DFM-FLR-006](../../skills/ee-dfm/references/rules.md#DFM-FLR-006) | 元件离板边与工艺边保持足够距离 ⚠ | 分区规划 | low | geometry_script (full) |
| [DFM-LIB-005](../../skills/ee-dfm/references/rules.md#DFM-LIB-005) | 通孔封装的孔径按引脚加余量并满足孔环 ⚠ | 符号封装库 | medium | drc (full) |
| [DFM-LIB-007](../../skills/ee-dfm/references/rules.md#DFM-LIB-007) | 丝印与焊盘保持间距 | 符号封装库 | high | drc (full) |
| [DFM-MFG-006](../../skills/ee-dfm/references/rules.md#DFM-MFG-006) | 不贴的零件和通孔件同时移出 BOM 与 CPL | 出图与制造 | medium | bom_check (full) |
| [DFM-MFG-007](../../skills/ee-dfm/references/rules.md#DFM-MFG-007) | 丝印文字与线宽达到可制造下限 | 出图与制造 | high | drc (full) |
| [DFM-MFG-010](../../skills/ee-dfm/references/rules.md#DFM-MFG-010) | 每个电源轨与关键信号至少有一个探测点 | 出图与制造 | medium | netlist_diff (full) |
| [DFM-MFG-011](../../skills/ee-dfm/references/rules.md#DFM-MFG-011) | 细间距或需平整焊盘的器件选 ENIG / OSP ⚠ | 出图与制造 | low | bom_check (partial) |
| [DFM-PLC-001](../../skills/ee-dfm/references/rules.md#DFM-PLC-001) | 元件间距满足 JLC 最小间距表 ⚠ | 器件布局 | medium | geometry_script (partial) |
| [DFM-PLC-003](../../skills/ee-dfm/references/rules.md#DFM-PLC-003) | 放置 3 个不对称的全局 MARK 点 ⚠ | 器件布局 | high | geometry_script (full) |
| [DFM-RTE-001](../../skills/ee-dfm/references/rules.md#DFM-RTE-001) | 片式元件两端的铜连接要热平衡 ⚠ | 布线 | medium | geometry_script (partial) |
| [DFM-RTE-004](../../skills/ee-dfm/references/rules.md#DFM-RTE-004) | 过孔覆盖方式与孔径、间距要匹配 | 布线 | high | drc (full) |
| [DFM-SCH-001](../../skills/ee-dfm/references/rules.md#DFM-SCH-001) | 原理图符号里带 LCSC 料号字段和 DNP 标记 | 原理图 | medium | bom_check (full) |
| [DFM-SCH-002](../../skills/ee-dfm/references/rules.md#DFM-SCH-002) | 在原理图里预留固件下载与调试入口 ⚠ | 原理图 | medium | erc (partial) |

## consider（31）

| ID | 规则 | 环节 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-FLR-008](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-008) | 安装孔预先定位，孔径和孔距满足板厂，并留地回流接点 | 分区规划 | medium | drc (full) |
| [GEN-PLC-001](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-001) | 先放固定件，再放 MCU 链，最后放去耦与外围 ⚠ | 器件布局 | low | review (manual) |
| [GEN-PLC-008](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-008) | 串联电阻靠近驱动端放置 | 器件布局 | medium | geometry_script (full) |
| [GEN-RTE-006](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-006) | MCU 供电走线按厂商给的最小宽度 ⚠ | 布线 | high | geometry_script (full) |
| [GEN-RTE-007](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-007) | 拐角默认用 45° 或圆弧，90° 并非一概有害 ⚠ | 布线 | high | geometry_script (full) |
| [GEN-RTE-011](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-011) | 相邻走线层垂直布线，但 2 层板优先保证回流 ⚠ | 布线 | medium | geometry_script (partial) |
| [GEN-VER-005](../../skills/ee-general-pcb/references/rules.md#GEN-VER-005) | 布局前只仿真数据手册答不了的关键块 | 签核验证 | medium | spice (partial) |
| [PWR-STK-001](../../skills/ee-power/references/rules.md#PWR-STK-001) | 按电流选外层铜厚并确认板厂实际铜厚 | 叠层与规则 | medium | tline_calc (partial) |
| [PWR-VER-007](../../skills/ee-power/references/rules.md#PWR-VER-007) | 估算效率与损耗预算并与热限比较 | 签核验证 | medium | bom_check (full) |
| [LPW-ARC-009](../../skills/ee-low-power/references/rules.md#LPW-ARC-009) | Wi-Fi 保持连接还是深睡重连，按平均电流预算选 | 架构与选型 | high | bench (partial) |
| [LPW-ARC-010](../../skills/ee-low-power/references/rules.md#LPW-ARC-010) | 睡眠预算要计入 Flash 待机电流 | 架构与选型 | high | bom_check (partial) |
| [LPW-ARC-013](../../skills/ee-low-power/references/rules.md#LPW-ARC-013) | 定时唤醒精度要求决定 RTC 慢时钟来源 | 架构与选型 | medium | bench (partial) |
| [ANA-ARC-004](../../skills/ee-analog/references/rules.md#ANA-ARC-004) | 按系统约束选择分流电阻位置 | 架构与选型 | high | spice (partial) |
| [ANA-ARC-008](../../skills/ee-analog/references/rules.md#ANA-ARC-008) | HX711 按需选数据率，并丢弃建立期数据 | 架构与选型 | high | bench (partial) |
| [ANA-PLN-003](../../skills/ee-analog/references/rules.md#ANA-PLN-003) | 电机/大电流回路不穿过模拟地区 | 平面与铺铜 | medium | geometry_script (partial) |
| [ANA-SCH-012](../../skills/ee-analog/references/rules.md#ANA-SCH-012) | 模拟电源与数字电源之间加滤波 | 原理图 | high | review (manual) |
| [ANA-STK-001](../../skills/ee-analog/references/rules.md#ANA-STK-001) | 给模拟信号层配一层完整的地 ⚠ | 叠层与规则 | medium | geometry_script (partial) |
| [HSD-PLN-003](../../skills/ee-high-speed/references/rules.md#HSD-PLN-003) | 高速线两侧铺地时保持 3–5 倍线宽间隙，缝合需验证 ⚠ | 平面与铺铜 | medium | drc (full) |
| [EMC-SCH-007](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-007) | 线缆共模电流大时用共模扼流圈或磁环 | 原理图 | medium | bom_check (partial) |
| [EMC-SCH-014](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-014) | 连接器金属壳/机壳地与信号地的连接方式要显式决定 ⚠ | 原理图 | medium | review (manual) |
| [EMC-STK-002](../../skills/ee-emc-esd/references/rules.md#EMC-STK-002) | 20H 规则有争议，不当作强制规则 ⚠ | 叠层与规则 | medium | em_sim (partial) |
| [EMC-VER-006](../../skills/ee-emc-esd/references/rules.md#EMC-VER-006) | 样机阶段逐个拆装滤波件，只保留有实测收益的 | 签核验证 | medium | bom_check (partial) |
| [THM-ARC-007](../../skills/ee-thermal/references/rules.md#THM-ARC-007) | 电机堵转 / 启动的脉冲要对照 MOSFET SOA ⚠ | 架构与选型 | low | spice (partial) |
| [THM-RTE-003](../../skills/ee-thermal/references/rules.md#THM-RTE-003) | 用过孔阵列的并联热阻核算而不是凭感觉 | 布线 | high | thermal_sim (full) |
| [THM-STK-001](../../skills/ee-thermal/references/rules.md#THM-STK-001) | 按功耗选铜厚 ⚠ | 叠层与规则 | high | thermal_sim (partial) |
| [THM-STK-002](../../skills/ee-thermal/references/rules.md#THM-STK-002) | 需要更低热阻时优先加内层地平面 | 叠层与规则 | high | thermal_sim (manual) |
| [THM-STK-003](../../skills/ee-thermal/references/rules.md#THM-STK-003) | 用板面积规则做第一遍可行性检查 | 叠层与规则 | high | thermal_sim (full) |
| [THM-VER-003](../../skills/ee-thermal/references/rules.md#THM-VER-003) | MOSFET 结温可用体二极管压降法做电学测量 | 签核验证 | medium | bench (manual) |
| [THM-VER-005](../../skills/ee-thermal/references/rules.md#THM-VER-005) | 先用热阻网络手算，再决定是否做 FEM | 签核验证 | high | thermal_sim (partial) |
| [DFM-MFG-008](../../skills/ee-dfm/references/rules.md#DFM-MFG-008) | 为序列号 / 二维码预留位置，不再用 JLCJLCJLCJLC ⚠ | 出图与制造 | medium | review (manual) |
| [DFM-MFG-009](../../skills/ee-dfm/references/rules.md#DFM-MFG-009) | 测试点的尺寸、间距与可达性 ⚠ | 出图与制造 | medium | geometry_script (full) |

⚠ = 来源之间有分歧，详情见规则里的「来源分歧」。
