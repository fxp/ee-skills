# 规则检查器（drc_rule + geometry）

把 `catalog/*.yaml` 里**可完全自动化**的规则变成可重复运行的 pass / fail / error / skipped。设计思路与建设顺序见
`../../references/toolchain.md` §3 与 §3.4（第 1、2 步）。

```bash
python run.py --board X.kicad_pcb --design design/my_board.yaml        # 两个检查器，结果写到 ./ee-results/<今天>/
python run.py --board X.kicad_pcb --design D.yaml --pro X.kicad_pro --out some/dir
python run.py --board X.kicad_pcb --design D.yaml --rules DFM-PLC-003,DFM-STK-001 --checkers geometry,drc_rule
python coverage.py                                                     # 哪些可自动化规则还没接、为什么
python -m pytest ../../../../tests -q                                  # 静态测试；种子缺陷测试需要 KiCad 10 和参考板（见 tests/test_checkers_seeded.py）
```

`--design` 从 `design/template.yaml` 复制修改：板文件里没有的信息（哪些是电源网 / 快沿网、哪些 IC 引脚配哪颗去耦电容、天线禁布区、分流电阻焊盘角色）写在这里，每项注明出处。

输入板会被**拷贝**到 `checkers/_work/run-*/`（git 忽略；不用 /tmp），之后只对拷贝操作；KiCad 用私有的
`KICAD_CONFIG_HOME` / `KICAD_DOCUMENTS_HOME`。不会修改你的板文件，也不会碰 KiCad 正在打开的文件。目录里的规则由 `$EE_CATALOG_DIR` 或向上查找到的 `catalog/` 提供。

## 构成

| 文件 | 作用 |
|---|---|
| `drc_rule.py` + `bindings/drc.yaml` | 规则 ID → `.kicad_dru` 规则 → `kicad-cli pcb drc` → 按 `rule 'ID/子规则'` 反查违规 |
| `export_geometry.py` | **在 KiCad 自带 Python 3.9 里**把板导出成 `geometry.json`（焊盘多边形、courtyard、走线、过孔、铜区填充、板框、网络类）。所有 pcbnew 耦合都在这个文件和 `seed_defects.py` |
| `geom_lib.py` | 纯 Python/numpy：多边形距离、板框、**网络连通图**（走线 + 过孔 + 焊盘接触，求焊盘间铜路径长度/最窄线宽/过孔数/拐角） |
| `geometry.py` + `bindings/geometry.yaml` + `design/<board>.yaml` | 几何检查函数；板上的角色（电源网、快沿网、去耦引脚、ESD 通道、天线禁布区、分流电阻）写在设计文件里，每项注明出处 |
| `common.py` | 目录读取、阈值解析、KiCad 路径、结果对象 |
| `run.py` | 一条命令：拷贝 → 导出 → 两个检查器 → `results.json` + `results.md` |
| `seed_defects.py` | （KiCad Python）制造 12 种种子缺陷：挪元件、删封装、改网络、删走线、加过孔/走线…… |
| `../../../tests/bestpractices/` | 好板 pass、缺陷板 fail 的断言；金丝雀与“阈值来自目录”的测试 |

## 结果对象

每条规则一个：`rule_id, checker, method, automatable, severity, status(pass|fail|error|skipped), measured, threshold, evidence, tool, inputs, duration_s, note`。

* **阈值不写在代码里**。绑定只写目录 `parameters[].name`，`op/value/unit` 取自目录（`mil`/`inch` 换成 mm，`scale` 做显式乘数，如“过孔焊盘比孔大 0.1 mm”→ 环宽 0.05 mm）。
  目录写“项目设定 / 经验阈值”的数字（去耦电容距离 ≤ 3 mm、检流线长度失配 < 20 %……）放在 `design/*.yaml` 的 `project_thresholds`，
  结果里 `threshold.source` 标 `design_yaml` 并带出处文字；只出现在规则文字里的判据标 `rule_text`。
* `measured` 总给出余量：DRC 的 `observed_extreme`（探测所得最近/最差值）与 `margin`，几何检查的实测值。
* `status=error` 表示工具失败，**不是**判定：`.kicad_dru` 语法错误、金丝雀缺席、导出失败、设计文件缺角色。

## drc_rule 的几个做法

* 每条目录规则一个目录、一次 `kicad-cli`（线程池里并行起子进程）。一条规则内的子规则（如 DFM-STK-002 的钻孔 / 孔环 / 孔间距）写进同一个 `.kicad_dru`，
  同类约束的条件互斥，避免 KiCad “靠后的规则吃掉靠前的”。规则名 = `<规则ID>/<子规则key>`。
* **金丝雀**：每个规则文件开头有一条对每个封装触发一次的 assertion。语法错误会让 KiCad 静默丢掉整个文件、退出码 0；金丝雀缺席就判 `error` 并逐条子规则二分定位。
* **探测运行**：判定运行（真实阈值）之后再跑一次把阈值放宽的运行，读出最近/最差的实测值（`actual` 只在描述字符串里）。
  `objects_in_probe_window = 0` 说明条件没匹配到对象（或都远在阈值之外）——不要把它当“检查过了”。
* `builtin:` 规则数 KiCad 自带检查（courtyards_overlap、missing_courtyard、shorting_items、unconnected_items），并在**拷贝的** `.kicad_pro` 里把默认忽略的检查打开。

## geometry 的几个做法

* 铜路径长度 = 走线长度 + 焊盘中心到走线端点的接触段，和 KiCad 的 `fromTo()` 对得上（测试：C4.1→U1.1 = 9.6631 mm）。只算走线和过孔，**不含铜皮**。
* 距离单位全是 mm、KiCad 板坐标（本板 = 规格坐标 + 50）。
* 看不到的东西写进结果的 `not evaluated`（丝印、元件高度、阻焊开窗、封装接地焊盘单独的回流距离），不会悄悄当作通过。

## 新增一条规则

1. DRC 形：在 `bindings/drc.yaml` 加 `<规则ID>: rules: [{key, constraint, bound, param, condition?, shape}]`，`param` 必须是该规则目录里存在的 `parameters[].name`。
   跑一次后看结果里的 `objects_in_probe_window`：为 0 说明条件没匹配到对象（拼错属性值也会这样，而且不会报错）。
2. 几何形：在 `geometry.py` 写一个 `@check` 函数 `(ctx, rule, P, out)`，用 `out.add(key, measured, threshold)` 记子检查；在 `bindings/geometry.yaml` 绑定参数。
3. 在 `tests/bestpractices/test_bestpractices_checkers.py` 的 `FLIPS` 里加一行（并在 `seed_defects.py` 加对应缺陷），保证它在好板上 pass、缺陷板上 fail。

## 已知局限

* 只接了 `verify.method = drc | geometry_script` 且 `automatable: full` 的规则里的一部分（见 `coverage.py` 生成的 `NOT_AUTOMATED.md`）。
* 去耦 / 电源路径等“角色”要靠 `design/*.yaml` 手写；还没有从原理图网表自动推导（§3.4 第 3 步）。
* 铜皮（GND 铺铜）不进连通图，所以 GND 网的路径 / 开尔文类检查只对走线网络有意义。
* pcbnew 的 SWIG 绑定有个坑：删除封装后同一进程里再 `LoadBoard` 会得到无类型指针，所以 `seed_defects.py` 一个缺陷一个进程。
