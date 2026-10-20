# 平面与铺铜（plane_pour）

37 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-PLN-009](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-009) | 天线下方和周围所有铜层禁布，铺铜前先画禁布区 | must | high | drc (full) |
| [GEN-PLN-001](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-001) | 先保证完整地平面，地层不走线、不被过孔排切成槽 | should | high | geometry_script (full) |
| [GEN-PLN-002](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-002) | 默认用一整块地平面，靠分区而不是分割隔离模拟数字 | should | high | geometry_script (full) |
| [GEN-PLN-003](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-003) | 必须分割地时，只在一点连接，信号只能走桥 | should | high | geometry_script (partial) |
| [GEN-PLN-004](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-004) | 2 层板用地网格 / 整面地铺铜并多打缝合过孔 | should | high | geometry_script (full) |
| [GEN-PLN-005](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-005) | MCU 下方做地岛，去耦和晶振的地接在上面 | should | medium | geometry_script (full) |
| [GEN-PLN-006](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-006) | 地铜用缝合过孔连接，间距不超过 λ/20 | should | medium | geometry_script (full) |
| [GEN-PLN-007](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-007) | 去掉死铜和孤岛，不让铺铜悬空 | should | medium | drc (full) |
| [GEN-PLN-008](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-008) | 通孔焊盘用热焊盘，SMD 地焊盘和去耦地直接连 | should | medium | drc (full) |
| [GEN-PLN-010](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-010) | 晶振下方做完整地参考，区域内不放其他网络的铜 | should | high | geometry_script (full) |
| [GEN-PLN-011](../../skills/ee-general-pcb/references/rules.md#GEN-PLN-011) | 芯片底部接地焊盘用多个过孔接地平面 | should | high | geometry_script (full) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-PLN-001](../../skills/ee-power/references/rules.md#PWR-PLN-001) | 变换器热回路下方保持连续地平面 | should | medium | geometry_script (partial) |
| [PWR-PLN-002](../../skills/ee-power/references/rules.md#PWR-PLN-002) | 信号地与功率地在 IC 地点单点汇合 | should | high | netlist_diff (full) |
| [PWR-PLN-003](../../skills/ee-power/references/rules.md#PWR-PLN-003) | 降压 IC 散热焊盘用 0.3 mm 小孔阵列接地 | should | high | geometry_script (full) |
| [PWR-PLN-004](../../skills/ee-power/references/rules.md#PWR-PLN-004) | 电机电流回路用独立地铜，单点接到逻辑地 | should | medium | geometry_script (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-PLN-001](../../skills/ee-rf/references/rules.md#RF-PLN-001) | 射频区地平面整块不分割，芯片底焊盘多打过孔 | must | high | drc (full) |
| [RF-PLN-002](../../skills/ee-rf/references/rules.md#RF-PLN-002) | 接地缝合过孔间距不超过 λ/20（按介质内波长） | should | high | geometry_script (full) |
| [RF-PLN-003](../../skills/ee-rf/references/rules.md#RF-PLN-003) | 并联接地元件的地脚旁紧贴独立接地过孔 | should | high | geometry_script (partial) |
| [RF-PLN-004](../../skills/ee-rf/references/rules.md#RF-PLN-004) | 匹配区走线和焊盘到邻近地铜至少 0.5 mm | should | medium | drc (full) |
| [RF-PLN-005](../../skills/ee-rf/references/rules.md#RF-PLN-005) | 射频路径下的内层：按厂商参考叠层选实心地或整片禁布 | should | medium | geometry_script (partial) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-PLN-001](../../skills/ee-audio/references/rules.md#AUD-PLN-001) | 器件下方保持完整地层，地引脚强连接，大电流回流不经输入地 | should | high | geometry_script (partial) |
| [AUD-PLN-002](../../skills/ee-audio/references/rules.md#AUD-PLN-002) | 信号线不得跨越或切割地平面 | should | high | geometry_script (full) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-PLN-001](../../skills/ee-analog/references/rules.md#ANA-PLN-001) | 整块地平面 + 分区走线，优先于分割 AGND/DGND | should | high | geometry_script (partial) |
| [ANA-PLN-002](../../skills/ee-analog/references/rules.md#ANA-PLN-002) | 转换器的 AGND/DGND 引脚在器件下方相连 | should | medium | review (partial) |
| [ANA-PLN-003](../../skills/ee-analog/references/rules.md#ANA-PLN-003) | 电机/大电流回路不穿过模拟地区 | consider | medium | geometry_script (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-PLN-001](../../skills/ee-high-speed/references/rules.md#HSD-PLN-001) | 按目标阻抗法设计高速 IC 的电源分配网络 | should | high | pi_sim (partial) |
| [HSD-PLN-002](../../skills/ee-high-speed/references/rules.md#HSD-PLN-002) | 以太网磁件下无铜，机壳地与数字地隔离 | should | high | geometry_script (full) |
| [HSD-PLN-003](../../skills/ee-high-speed/references/rules.md#HSD-PLN-003) | 高速线两侧铺地时保持 3–5 倍线宽间隙，缝合需验证 | consider | medium | drc (full) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-PLN-001](../../skills/ee-emc-esd/references/rules.md#EMC-PLN-001) | 两层板地铺铜栅格化，消除只有一端连接的地岛 | should | high | geometry_script (full) |
| [EMC-PLN-003](../../skills/ee-emc-esd/references/rules.md#EMC-PLN-003) | 机壳/屏蔽地铜区：宽、短、至少两颗螺丝 | should | high | geometry_script (partial) |
| [EMC-PLN-002](../../skills/ee-emc-esd/references/rules.md#EMC-PLN-002) | 板边地环与缝合过孔间距小于 λ/20 | consider | low | geometry_script (full) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-PLN-001](../../skills/ee-hv-safety/references/rules.md#HVS-PLN-001) | 铺铜、热焊盘也受 HV 网络类间距约束 | should | medium | drc (full) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-PLN-001](../../skills/ee-thermal/references/rules.md#THM-PLN-001) | SOT-223 的散热铜面积要按目标 θJA 来定 | should | high | geometry_script (partial) |
| [THM-PLN-002](../../skills/ee-thermal/references/rules.md#THM-PLN-002) | 散热铜优先放在元件面，再用过孔连到背面 | should | high | geometry_script (partial) |
| [THM-PLN-003](../../skills/ee-thermal/references/rules.md#THM-PLN-003) | 别在散热铜皮上垂直于热流切口 | should | high | geometry_script (partial) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-PLN-001](../../skills/ee-dfm/references/rules.md#DFM-PLN-001) | 铜皮与走线到板边、V-cut 线的距离 | must | high | drc (full) |
| [DFM-PLN-002](../../skills/ee-dfm/references/rules.md#DFM-PLN-002) | 铺铜上的焊盘用热焊盘，散热焊盘除外 | should | medium | drc (partial) |
