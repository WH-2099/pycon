# 章节时间线

核验与生成日期：2026-09-04。
2026-09-05 选定生图版本，移除六张 Mermaid slide。
6 个位置各保留一张生图，共 6 页；第五章包含总结与展望两页。
运行 `just present` 放映，或用 `just edit` 编辑对应单元格。

## 插入位置与资产

| 位置 | 主题 | 生图资产 | 尺寸 |
| --- | --- | --- | --- |
| 第一章末，EVA 页之后 | 全场历史坐标 | [01-timeline.png](../public/illustrations/01-timeline.png) | 1919 × 820 |
| 第二章开头，章节过渡之后 | 暂停、委托、调度、归属 | [02-timeline.png](../public/illustrations/02-timeline.png) | 1920 × 819 |
| 第三章开头，章节过渡之后 | 进程、解释器、自由线程三轨 | [03-timeline.png](../public/illustrations/03-timeline.png) | 1672 × 941 |
| 第四章开头，章节过渡之后 | 状态边界、共享、局部保护、不可变 | [04-timeline.png](../public/illustrations/04-timeline.png) | 1920 × 819 |
| 第五章开头，第 1 组 | 三个责任的历史总结 | [05-timeline-summary.png](../public/illustrations/05-timeline-summary.png) | 1920 × 819 |
| 第五章开头，第 2 组 | 发布背景与开放探索 | [05-timeline-outlook.png](../public/illustrations/05-timeline-outlook.png) | 1920 × 819 |

替代文本、讲者备注和逐图来源在 [timelines.toml](timelines.toml)。
生图均由内置 imagegen 生成和修改，完整实际提示词与来源记录在 [prompts.json](prompts.json)。
这些图是说明图，不是实测数据；年份表示特性随 Python 版本发布的年份，横向距离不表示时长。
三条执行路线以及不同的状态保护方式仍然共存。

## 事实边界

- `asyncio` 随 Python 3.4 发布，不能照抄 PEP 3156 头部的早期 3.3 目标。
  [Python 3.4 新特性](https://docs.python.org/3.4/whatsnew/3.4.html#whatsnew-asyncio)。
- PEP 654 定义 `ExceptionGroup` 和 `except*`；`TaskGroup` 是同版标准库能力，分开标注。
  [PEP 654](https://peps.python.org/pep-0654/)、[TaskGroup 文档](https://docs.python.org/3.11/library/asyncio-task.html#task-groups)。
- 自由线程在 3.13 为实验阶段，3.14 正式支持但仍可选，运行时还需要关闭 GIL。
  [PEP 703](https://peps.python.org/pep-0703/)、[PEP 779](https://peps.python.org/pep-0779/)。
- `shared_memory` 在 3.8 加入，无专属 PEP；共享字节仍需应用同步。
  [Python 3.8 文档](https://docs.python.org/3.8/library/multiprocessing.shared_memory.html)。
- 对象永生减少引用计数写入，不等于对象内容不可变。
  [PEP 683](https://peps.python.org/pep-0683/)。
- PEP 814 已 Final；3.15 截至核验日仍为 RC2，最终版计划 2026-10-01 发布；`frozendict` 仅浅层不可变。
  [PEP 814](https://peps.python.org/pep-0814/)、[PEP 790](https://peps.python.org/pep-0790/)。
- PEP 789、805 仍为 Draft；805 的 3.16 是目标，789 不标已经错过的 3.14 目标为落地版本。
  [PEP 789](https://peps.python.org/pep-0789/)、[PEP 805](https://peps.python.org/pep-0805/)。
- BOC / `bocpy` 为第三方探索，不是 CPython 已确定的统一路线，也没有标准库发布版本。
  [bocpy 项目](https://github.com/microsoft/bocpy)。

以上明确提及的 PEP 已在 [ref/peps](../ref/peps/) 归档，无需重复下载。

## 呈现与验证

6 张时间线均为独立图片页，未使用的 Mermaid 源码与历史截图已清理。
成品完成 4 轮页面审查，覆盖 1920 × 1080 与 1280 × 720 的实际放映。
图片以 `object-fit: contain` 完整显示，保留边缘版本与 PEP 标签。
这些图用于章节回顾和开场定位，具体机制由相邻正文页展开。
