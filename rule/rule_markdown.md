统一采用下面的 Markdown 规范：

* 不允许出现: ---
* 所有独立公式都写成一行
* 行内公式：`$u_t=Du_{xx}$`
* 独立公式：`$$...$$`,始终写成单行形式
* 不使用 `[]` 包裹公式
* 章节使用 `#`、`##`、`###`
* 重要说明使用 `> **注意*：*`
* 内容要紧凑
* 数学公式尽量单独成行，这样 Typora、Obsidian、GitHub Pages 等都能正确渲染。
* 专有名词的写作格式是: 第一次出现时用：专有名词中文(对应的英文)，后面出现统一用英文或者中文中的一种；
* 除非特殊情况说明，否则文档只有一个一级标题·


根据kb\projects\wireless_channel\gscm_implementation里面的GSCM算法流程文档：gscm_algorithm_workflow.md、GSCM 软件架构与开发任务设计（第一版）文档：gscm_software_architecture.md、第一周计划任务的文档\week_plan\week_1.md、38901-g10_V16.1.0.pdf文档，完成\week_plan\week_1.md里面第一天的任务：编写 `types.py`、`config.py`、`random_state.py`。
为了让整个过程可控制，采取分步骤进行，第一步在对应位置生成空白的脚本文件，第二步在\week_plan\week_1_day_1.md介绍 `types.py`、`config.py`、`random_state.py`脚本的作用，包括不限于包含哪些类及其作用，每个类包含的函数及其参数、返回值等，如何使用，类名可以使用大写字母和小写字母、函数名统一使用小写字母，变量和参数名尽量要使用小字母，特殊情况要进行说明，week_1_day_1.md中要分文档进行表述。

根据设计说明\week_plan\week_1_day_1.md与团队的开发要求D:\chen\repo\fealpy\docs\standards\coding_standards.md、D:\chen\repo\fealpy\docs\standards\documentation_style.md进行`types.py`、`config.py` 与 `random_state.py`，并在examples\gscm中写一个调用运行示例

