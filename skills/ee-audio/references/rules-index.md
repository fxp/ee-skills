# 音频 — 规则索引

43 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-ARC-001 | 按功率、负载和损耗反推 Class-D 供电电压与限流 | should | high | bom_check(partial) |
| AUD-ARC-003 | 音频指标带测试条件立项（THD+N、SNR、PSRR） | should | high | bench(partial) |
| AUD-ARC-004 | Codec 的 MCLK 取 256×fs 常用频率，避开内部 PLL | should | high | bom_check(partial) |
| AUD-ARC-002 | 按功率、散热、续航和 EMI 预算选 Class-D 或线性功放 | consider | medium | review(manual) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-LIB-001 | MEMS 话筒封装库带声孔与垫圈尺寸 | should | high | geometry_script(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-SCH-014 | 自举电容按数据手册的容量、介质和耐压选 | must | high | erc(full) |
| AUD-SCH-001 | 信号通路电容用 C0G 或薄膜，慎用 X7R/X5R ⚠ | should | high | bom_check(partial) |
| AUD-SCH-002 | 按实际输入阻抗和有效容量核算 AC 耦合转折频率 | should | high | spice(partial) |
| AUD-SCH-003 | 运放驱动容性负载时加隔离电阻并留相位裕度 | should | high | spice(partial) |
| AUD-SCH-004 | 音频端口加 RF 低通：输入、BTL 输出和电源入口 | should | high | spice(partial) |
| AUD-SCH-005 | 驻极体话筒偏置电阻、耦合电容和中点偏置滤波 | should | high | spice(partial) |
| AUD-SCH-006 | 模拟 MEMS 话筒供电去耦、RF 滤波和耦合电容 | should | high | review(manual) |
| AUD-SCH-007 | Codec 模拟电源独立稳压并滤波，MICBIAS 噪声同源 | should | high | spice(partial) |
| AUD-SCH-008 | Codec 线路输出接 Class-D 输入前加 RC 低通 | should | high | spice(partial) |
| AUD-SCH-009 | 抑制 pop/click：匹配输入网络、RC≤1 ms、使能时序 | should | high | spice(partial) |
| AUD-SCH-010 | 耳机输出：隔直电容容量，或无电容架构的接线 | should | high | erc(partial) |
| AUD-SCH-011 | Class-D 输出 LC 滤波器按二阶 Butterworth 设计 | should | high | spice(partial) |
| AUD-SCH-012 | LC 滤波器电感和电容选型：线性度与降额 | should | high | bom_check(partial) |
| AUD-SCH-013 | 免滤波 Class-D 的磁珠 EMI 滤波：电感性元件在前，禁止仅用电容 ⚠ | should | high | spice(partial) |
| AUD-SCH-015 | Class-D 电源引脚分级去耦和大容量电容 | should | high | bom_check(partial) |
| AUD-SCH-016 | 平衡线路输入选高 CMRR 的差分接收器 | consider | medium | spice(partial) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-NET-001 | Class-D 输出、自举、Vsense 和电源分别设网络类 | should | medium | drc(full) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-STK-001 | 含 Class-D 的音频板用 4-6 层，第二层整层做地 | should | high | drc(partial) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-FLR-001 | 音频板分区：模拟输入、数字、Class-D 功率级各占一区 | should | high | geometry_script(partial) |
| AUD-FLR-002 | 定 AGND/DGND 策略：默认单一地平面分区，按 codec 手册例外 ⚠ | should | high | geometry_script(full) |
| AUD-FLR-003 | 平衡接口屏蔽接机壳，信号地与机壳单点连接 | should | medium | review(manual) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-PLC-001 | Class-D 去耦与自举电容紧贴引脚并控制回路电感 | must | high | geometry_script(full) |
| AUD-PLC-002 | Codec 去耦与 VREF/VAG 参考电容紧贴引脚 | should | high | geometry_script(partial) |
| AUD-PLC-003 | 输出滤波器紧靠功放，电感相互隔开并远离输入 | should | high | geometry_script(partial) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-RTE-002 | 开关网络与其他信号在相邻层不平行重叠 | must | high | geometry_script(full) |
| AUD-RTE-001 | Class-D 输出走线宽、短、成对并等长 | should | high | drc(full) |
| AUD-RTE-003 | 音频输入走线短、过完整地、远离开关与 RF | should | high | geometry_script(partial) |
| AUD-RTE-004 | 差分音频信号成对对称走线，并铺在模拟地之上 | should | high | geometry_script(partial) |
| AUD-RTE-005 | I2S/MCLK 时钟点对点、短、远离模拟引脚 | should | medium | si_sim(partial) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-PLN-001 | 器件下方保持完整地层，地引脚强连接，大电流回流不经输入地 | should | high | geometry_script(partial) |
| AUD-PLN-002 | 信号线不得跨越或切割地平面 | should | high | geometry_script(full) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-MFG-001 | MEMS 话筒工艺：声孔不镀铜、钢网破环、回流后禁水洗 | should | high | geometry_script(partial) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| AUD-VER-002 | Class-D 扬声器输出必须差分测量，输出端不接地 | must | high | review(manual) |
| AUD-VER-001 | 按规范测 THD+N/SNR，并用 FFT 交叉验证 | should | high | bench(partial) |
| AUD-VER-003 | 用 ngspice 仿真耦合、偏置网络和滤波器的 AC 与噪声 | should | medium | spice(partial) |
| AUD-VER-004 | 向电源注入纹波测 PSRR 和电源耦合 | should | high | bench(partial) |
| AUD-VER-005 | 静态本底 FFT：查工频谐波、217 Hz 和开关频率成分 | should | medium | bench(partial) |
| AUD-VER-006 | Class-D 辐射预扫：最长喇叭线与最终磁珠/滤波器配置 | should | high | emc_precompliance(manual) |
