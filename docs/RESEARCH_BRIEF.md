# 调研方法与质量要求（给所有调研者）

目标：建一个**有出处、机器可读**的电路设计最佳实践库，后续用来驱动自动验证（KiCad ERC / DRC、自定义 pcbnew 几何脚本、SPICE、电磁 / 信号完整性 / 电源完整性 / 热仿真）。所以每条规则必须**原子、来源给了数字就量化、可检查**。

格式见 `SCHEMA.md`，校验用 `tools/validate.py`。输出文字用中文，术语、器件名、标准号保留英文。

## 调研方法

1. 用搜索找、用抓取工具（WebFetch 或浏览器）打开并**读原文**；PDF 抓回来是二进制时先 `pdftotext -layout` 再 grep 数字，图片型扫描件看渲染页。只在搜索摘要里见过的来源，`confidence` 不得标 `high`。
2. 来源优先级：标准（IPC、IEC、JEDEC）和厂商应用笔记 / 数据手册 / 官方布局指南（TI、ADI、Infineon、ST、Microchip、NXP、Renesas、onsemi、Espressif、Nordic、Silicon Labs、Würth、Murata、TDK、Vishay、Coilcraft）> 教科书和经典文献（Henry Ott《Electromagnetic Compatibility Engineering》、Howard Johnson《High-Speed Digital Design》、Eric Bogatin、Bruce Archambeault、Horowitz & Hill、Walt Jung / Hank Zumbahlen、Douglas Self）> EDA 厂商指南（KiCad、Altium、Cadence、Siemens）> 板厂文档（JLCPCB、PCBWay）> 博客论坛。
3. 数字阈值（距离、宽度、电容值、倍数）只在你**读到原文**时才写进 `parameters`，并在 `sources` 里指向那一处。凭经验估的值写进 `note`，`confidence` 降到 `medium` / `low`。
4. 不同来源冲突时（例如保险丝与 TVS 的先后、20H 规则、地平面是否分割、AGND/DGND 单点还是单平面），不要二选一糊弄：写 `conflicts`，说明各方观点和你的取舍依据。
5. 去伪存真：流传很广但站不住的说法（如"90° 拐角一定有害"）要么不收，要么收成 `consider` 并写明条件和反例。

## 硬性要求

* **不要编造 URL、章节号、数值。** 没读到原文就不要标 `high`。教科书 / 付费标准没有 URL 就写 `ref`。
* 每条规则尽量带 ≥ 1 个真实 URL 来源；`must` 级别尽量有 2 个独立来源或 1 个标准 / 厂商原文。
* 不要大段复制原文；用自己的话概括。
* `verify` 要具体到别人能照着实现：量什么、从哪到哪、通过判据是什么。只有真正机械的检查才标 `automatable: full`。尽量让一条规则同时给出"设计时检查"和"仿真 / 实测检查"两种验证方式（如果都存在）。
* 一条规则只讲一件事。一般性规则放 `general`，本领域特有的约束放本领域（带本领域的量化参数）。不要在你负责以外的领域写规则，不要和别的领域重复。
* 宁可少而准：总数目标见各自任务，但没有出处支撑的规则不要凑数。
* 覆盖面：你负责的每个环节（stage）都要有规则；某个环节确实没有领域特有内容就跳过，在最终报告里说明。
* 与示例板 [fxp/cat-feeder](https://github.com/fxp/cat-feeder)（ESP32-C3 模块、2 层板、N-MOSFET 电机驱动、INA199 分流检测、AMS1117 LDO、HX711 模块、JLC SMT 贴片）相关的规则加 `tags: [cat-feeder]`。

## 边界

* 只创建 / 修改你被指派的输出文件。临时文件放 `work/<你的名字>/`（已在 .gitignore 里；不要用 /tmp，会消失），结束前删干净。
* 不要改仓库里其他文件，不要 git commit，不要安装系统软件，不要碰别人 KiCad 可能正开着的板文件。
* 写完后：
  1. `python tools/validate.py <你的文件>` 直到 0 errors（警告尽量清掉）。
  2. `python tools/validate.py <你的文件> --check-urls`，处理不可达的 URL：确认你确实打开过的（403 / 429 多半是机器人拦截）可以保留，其余修正或删掉。

## 最终报告（≤ 200 字，不要贴 YAML）

* 每个 stage 的规则条数；
* 发现的重要来源冲突（一两句）；
* 你没能查到出处、因此没收录的重要主题（缺口）；
* 你认为最值得优先做自动验证的 3 条规则 ID。
