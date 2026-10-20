# 通用 / 数模混合 MCU 板 — 规则索引

103 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-ARC-007 | 按电源轨做功耗预算并计入峰值电流 | must | high | bom_check(full) |
| GEN-ARC-009 | 核对每条数字链路的电平兼容与过压 | must | high | review(partial) |
| GEN-ARC-001 | 需求逐条分配到设计元素并指定验证方法 | should | medium | review(partial) |
| GEN-ARC-002 | 按产品等级对元件电压 / 电流 / 功率降额 ⚠ | should | high | bom_check(partial) |
| GEN-ARC-003 | 陶瓷电容按直流偏压后的有效容值取值 | should | high | bom_check(partial) |
| GEN-ARC-004 | 选型时核对生命周期并为关键件备好替代料 ⚠ | should | medium | bom_check(partial) |
| GEN-ARC-005 | 封装与器件选择要匹配贴片厂的库和工艺 | should | high | bom_check(full) |
| GEN-ARC-006 | MCU / 模块选型前做引脚预算并剔除受限引脚 | should | high | review(partial) |
| GEN-ARC-008 | 先定上电时序与复位释放条件 | should | high | spice(partial) |
| GEN-ARC-010 | 连接器按触点数与温度折算电流并防插错 ⚠ | should | medium | bom_check(partial) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-LIB-001 | 符号的引脚号、名称和电气类型逐脚对照数据手册 | must | high | erc(full) |
| GEN-LIB-002 | 焊盘图形取自厂商推荐或 IPC-7351 并1:1核对 | must | medium | geometry_script(partial) |
| GEN-LIB-005 | 自动核对符号引脚与封装焊盘一致 | must | high | erc(full) |
| GEN-LIB-003 | 每个封装画闭合的 courtyard 并满足外扩量 ⚠ | should | medium | drc(full) |
| GEN-LIB-004 | 带散热焊盘的封装补全焊盘编号、过孔与钢网开窗 ⚠ | should | high | geometry_script(partial) |
| GEN-LIB-006 | 3D 模型对准焊盘并核对与贴片厂的旋转约定 | should | medium | geometry_script(partial) |
| GEN-LIB-007 | 库只有一个来源：项目内库表且纳入版本控制 | should | high | erc(full) |
| GEN-LIB-008 | 库器件携带制造商、型号、数据手册和厂方料号 | should | high | bom_check(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-SCH-004 | 为每个输入定义确定电平，不允许悬空 | must | high | erc(partial) |
| GEN-SCH-005 | 执行器驱动脚在上电和复位期间必须保持关断 | must | high | erc(full) |
| GEN-SCH-006 | strapping / boot 引脚按手册配置且不加冲突负载 | must | high | erc(partial) |
| GEN-SCH-007 | 复位 / 使能引脚不得悬空并满足上电时序 ⚠ | must | high | spice(partial) |
| GEN-SCH-015 | 从数据手册典型电路出发并遵守元件限制说明 ⚠ | must | high | spice(partial) |
| GEN-SCH-001 | 按功能块组织原理图，页间只用层次标签连接 | should | medium | erc(full) |
| GEN-SCH-002 | 电源轨用统一的电源符号并规范命名 | should | medium | erc(full) |
| GEN-SCH-003 | 每个电源引脚（对）都画出规定值的去耦电容 ⚠ | should | high | erc(partial) |
| GEN-SCH-008 | 未用引脚按手册处理并显式标注 | should | high | erc(full) |
| GEN-SCH-009 | 晶体负载电容按公式计算并留出杂散电容 ⚠ | should | high | tline_calc(full) |
| GEN-SCH-010 | 为每个可编程器件引出调试 / 烧录接口 | should | medium | erc(partial) |
| GEN-SCH-011 | 在原理图中为电源轨和关键信号预留测试点 ⚠ | should | medium | erc(full) |
| GEN-SCH-012 | 全部元件完成标注，位号唯一且稳定 | should | high | erc(full) |
| GEN-SCH-013 | 可选件和调试件标记 DNP 并保证属性两边一致 | should | high | bom_check(full) |
| GEN-SCH-014 | 每个对外连接器线路都要有保护决策 ⚠ | should | medium | erc(partial) |
| GEN-SCH-016 | 关键位置标注容差、耐压和取值依据 | should | medium | bom_check(partial) |
| GEN-SCH-017 | I2C 上拉电阻按上升时间和灌电流计算 | should | high | tline_calc(full) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-NET-003 | 差分对的两个网络同名并用一致的 _P/_N 后缀 | must | high | erc(full) |
| GEN-NET-004 | 网络只在原理图里改，PCB 变更要反向标注 | must | high | netlist_diff(full) |
| GEN-NET-005 | 原理图与 PCB 奇偶性检查要连警告一起设为门禁 | must | high | netlist_diff(full) |
| GEN-NET-001 | 信号网络显式命名并统一命名风格 ⚠ | should | medium | erc(full) |
| GEN-NET-002 | 网络类承载约束并保证每个网络都有归属 | should | high | erc(full) |
| GEN-NET-006 | 出图前做网表差异对比并附 IPC-D-356 | should | medium | netlist_diff(full) |
| GEN-NET-007 | 排查孤立标签、单引脚网络和意外短接 | should | high | erc(full) |
| GEN-NET-008 | 引脚 / 门交换只在功能等价的引脚间进行 | should | high | netlist_diff(partial) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-STK-005 | 按板厂能力设板级约束，不贴着极限设计 | must | high | drc(full) |
| GEN-STK-001 | 按最高频率与辐射风险选层数，2 层板要补偿 ⚠ | should | medium | geometry_script(partial) |
| GEN-STK-002 | 4 层板信号层贴近邻接平面，两平面间用厚芯板 ⚠ | should | high | geometry_script(full) |
| GEN-STK-003 | 每个走线层邻接参考平面，高频线埋在两平面之间 ⚠ | should | high | geometry_script(full) |
| GEN-STK-004 | 2 层板：底层做地参考，元件只放顶层 | should | high | geometry_script(full) |
| GEN-STK-006 | 网络类宽度只是默认值，必须用自定义规则落成 DRC | should | high | drc(full) |
| GEN-STK-007 | 按电流和温升算线宽，IPC-2221 作保守下限 ⚠ | should | medium | tline_calc(full) |
| GEN-STK-008 | 载流层间过孔至少两个，并按孔壁截面估算电流 ⚠ | should | medium | geometry_script(partial) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-FLR-007 | 板框闭合，铜到板边满足板厂最小间距 | must | high | drc(full) |
| GEN-FLR-001 | 按功能和噪声等级分区，快逻辑靠近电源、模拟最远 | should | high | geometry_script(partial) |
| GEN-FLR-002 | 电源入口、稳压器、MCU 依次相邻，地在三者间单点汇合 | should | medium | geometry_script(partial) |
| GEN-FLR-003 | 各子系统的走线只在自己的分区内，跨区只走指定通道 | should | high | geometry_script(full) |
| GEN-FLR-004 | 大电流路径和开关环路远离敏感小信号 | should | medium | geometry_script(partial) |
| GEN-FLR-005 | 连接器集中在板边，噪声源与晶振远离连接器 | should | medium | geometry_script(partial) |
| GEN-FLR-006 | 带板载天线的模块放在板边，天线区空出 ⚠ | should | high | geometry_script(partial) |
| GEN-FLR-008 | 安装孔预先定位，孔径和孔距满足板厂，并留地回流接点 | consider | medium | drc(full) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-PLC-002 | 每个电源引脚一个去耦电容，小容值最近 | should | high | geometry_script(full) |
| GEN-PLC-003 | 去耦电容地焊盘就近接地，用过孔或直连地铜 | should | high | geometry_script(full) |
| GEN-PLC-004 | 电源电流必须穿过去耦电容焊盘再到引脚 | should | medium | geometry_script(partial) |
| GEN-PLC-005 | 电源入口和稳压器处放大电容，模块进线前放 10 µF | should | medium | geometry_script(full) |
| GEN-PLC-006 | 晶振贴近 MCU，走线短且对称，周围有地环 ⚠ | should | high | geometry_script(full) |
| GEN-PLC-009 | ESD / TVS 器件紧靠连接器，保护对象放得更远 ⚠ | should | high | geometry_script(full) |
| GEN-PLC-001 | 先放固定件，再放 MCU 链，最后放去耦与外围 ⚠ | consider | low | review(manual) |
| GEN-PLC-007 | 晶振周围留出隔离区，不放无关元件 ⚠ | consider | medium | geometry_script(full) |
| GEN-PLC-008 | 串联电阻靠近驱动端放置 | consider | medium | geometry_script(full) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-RTE-002 | 信号线不得跨越参考平面的分割槽或缝隙 | must | high | geometry_script(full) |
| GEN-RTE-001 | 每条信号线下方保持连续的回流参考铜 | should | medium | geometry_script(full) |
| GEN-RTE-003 | 信号换层时在过孔旁放地过孔提供回流 | should | medium | geometry_script(partial) |
| GEN-RTE-004 | 电源线与地线并行贴近，环路长宽比不超过 3:1 | should | high | geometry_script(full) |
| GEN-RTE-005 | 电源分配单点或星形，别串成菊花链 ⚠ | should | high | geometry_script(partial) |
| GEN-RTE-008 | 快信号避免 T 形分支和长残桩 | should | high | geometry_script(full) |
| GEN-RTE-009 | 敏感信号和时钟尽量不打过孔 | should | high | drc(full) |
| GEN-RTE-010 | 干扰源与敏感线间距至少 3 倍线宽 ⚠ | should | medium | drc(full) |
| GEN-RTE-013 | 晶振下方不走信号，时钟走线周围用地包裹 ⚠ | should | high | geometry_script(full) |
| GEN-RTE-014 | 连接器先到 TVS 再到 IC，路径短直无桩无过孔 | should | high | geometry_script(full) |
| GEN-RTE-006 | MCU 供电走线按厂商给的最小宽度 ⚠ | consider | high | geometry_script(full) |
| GEN-RTE-007 | 拐角默认用 45° 或圆弧，90° 并非一概有害 ⚠ | consider | high | geometry_script(full) |
| GEN-RTE-011 | 相邻走线层垂直布线，但 2 层板优先保证回流 ⚠ | consider | medium | geometry_script(partial) |
| GEN-RTE-012 | 噪声走线不放在板子最外沿 ⚠ | consider | medium | geometry_script(full) |
| GEN-RTE-015 | 快速信号走线长度限制在约 1/50 波长以内 ⚠ | consider | high | geometry_script(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-PLN-009 | 天线下方和周围所有铜层禁布，铺铜前先画禁布区 | must | high | drc(full) |
| GEN-PLN-001 | 先保证完整地平面，地层不走线、不被过孔排切成槽 | should | high | geometry_script(full) |
| GEN-PLN-002 | 默认用一整块地平面，靠分区而不是分割隔离模拟数字 ⚠ | should | high | geometry_script(full) |
| GEN-PLN-003 | 必须分割地时，只在一点连接，信号只能走桥 | should | high | geometry_script(partial) |
| GEN-PLN-004 | 2 层板用地网格 / 整面地铺铜并多打缝合过孔 | should | high | geometry_script(full) |
| GEN-PLN-005 | MCU 下方做地岛，去耦和晶振的地接在上面 ⚠ | should | medium | geometry_script(full) |
| GEN-PLN-006 | 地铜用缝合过孔连接，间距不超过 λ/20 ⚠ | should | medium | geometry_script(full) |
| GEN-PLN-007 | 去掉死铜和孤岛，不让铺铜悬空 ⚠ | should | medium | drc(full) |
| GEN-PLN-008 | 通孔焊盘用热焊盘，SMD 地焊盘和去耦地直接连 ⚠ | should | medium | drc(full) |
| GEN-PLN-010 | 晶振下方做完整地参考，区域内不放其他网络的铜 ⚠ | should | high | geometry_script(full) |
| GEN-PLN-011 | 芯片底部接地焊盘用多个过孔接地平面 | should | high | geometry_script(full) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| GEN-VER-001 | ERC 零违规，例外逐条带理由，禁止整类静音 | must | high | erc(full) |
| GEN-VER-008 | 下单前按固定门禁逐项签核 | must | medium | erc(full) |
| GEN-VER-002 | 按类别理解 ERC 违规，PWR_FLAG 只放在真实电源源头 | should | high | erc(partial) |
| GEN-VER-003 | 打开默认被忽略的 ERC 检查 ⚠ | should | high | erc(full) |
| GEN-VER-004 | 布局前由第二人对照数据手册做原理图评审 | should | high | review(manual) |
| GEN-VER-006 | 把仿真与实测对照并记录模型的适用范围 | should | medium | spice(partial) |
| GEN-VER-007 | 首次上电按步骤逐轨进行并限流 | should | medium | bench(manual) |
| GEN-VER-009 | EDA 文件进版本控制，忽略缓存并给下单版本打标签 ⚠ | should | medium | review(full) |
| GEN-VER-005 | 布局前只仿真数据手册答不了的关键块 | consider | medium | spice(partial) |
