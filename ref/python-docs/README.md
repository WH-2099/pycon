# Python 官方文档快照

获取日期：2026-09-04。

原始 RST 使用 Pandoc 3.9 转成 GFM Markdown，方便本地检索和批注。
Sphinx 的交叉引用与指令不一定能完整呈现，因此正式引用仍应回到对应的在线官方页面。
转换稿禁用自动 Markdown 风格修复，以免继续改变官方源码结构。

## Python 3.15 RC2

以下文件来自 CPython 官方仓库的 `v3.15.0rc2` tag。
对应 commit 为 `435c9e5a798c99653e3ab64ce29baed0e4f3dfee`。

- [线程安全保证](threadsafety.md)：内建容器在自由线程构建中的分级保证与非原子复合操作。
- [自由线程 HOWTO](free-threading-python.md)：运行时 GIL 状态、C 扩展兼容和已知限制。
- [多解释器](concurrent.interpreters.md)：隔离、通信与可共享对象边界。
- [Future 与 Executor](concurrent.futures.md)：线程、进程和解释器执行器的当前行为。
- [共享内存](multiprocessing.shared_memory.md)：跨进程共享存储及生命周期规则。
- [asyncio Task](asyncio-task.md)：Task、TaskGroup、取消与异常传播。
- [abi3t 迁移指南](abi3t-migration.md)：自由线程 Stable ABI 的扩展迁移约束。

在线入口：[Python 3.15 documentation](https://docs.python.org/3.15/)。

Python 3.15 在获取日仍是 RC2，正式版计划于 2026-10-01 发布；演讲前应重新比较最终文档。

## Python 3.14.7

以下四份文件均已完整归档，固定于 CPython 官方仓库的 `v3.14.7` tag。
对应 commit 为 `823f0323ee6ec1402088b73bce1a38473cac36dc`。
它们用于第四章引用计数与 GC 深入页，核对已发布的自由线程实现；不要与上面的 3.15 RC2 快照混用。

| 本地快照 | 固定版本的官方来源 | 用途 |
| --- | --- | --- |
| [GC 设计](garbage-collector-3.14.7.md) | [InternalDocs/garbage_collector.md](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/garbage_collector.md) | 两种 GC 实现、堆遍历、两次暂停与终结顺序 |
| [自由线程 HOWTO](free-threading-python-3.14.7.md) | [Doc/howto/free-threading-python.rst](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-python.rst) | 永生化、偏置、延迟与分线程计数的适用对象和释放延迟 |
| [C 扩展自由线程指南](free-threading-extensions-3.14.7.md) | [Doc/howto/free-threading-extensions.rst](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-extensions.rst) | 强引用 API、分配域、线程状态与扩展声明 |
| [循环 GC 支持](gcsupport-3.14.7.md) | [Doc/c-api/gcsupport.rst](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/gcsupport.rst) | 扩展容器的遍历、清理、跟踪与分配责任 |

获取方式为 `git show v3.14.7:<官方仓库路径>`，复用已更新远端引用的本地 CPython 裸仓。
GC 设计原文已经是 Markdown，保留原文；其相对图片链接指向上表官方来源中的配套图片，本次未下载图片。
另外三份 RST 使用 `pandoc --from=rst --to=gfm --wrap=none` 转写。
每份文件开头都记录固定来源、版本、获取日期和转换方式。

在线入口：[Python 3.14 documentation](https://docs.python.org/3.14/)。
在线文档可能继续修订，实现细节应以本节固定 tag 和对应源码为准。
