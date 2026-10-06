# data_v02 第一阶段 55 题评测结果

## 测试口径

- 测试集：`data/data_v01/eval_questions_55.json`
- 数据：`data/data_v02/all_interfaces.json`
- 向量库：`vector_store/vector_store_v02/chroma`
- Collection：`fealpy_capabilities_v02`
- 模式：`rule`
- Top K：5
- 测试时间：2026-09-21

选择 `rule` 模式是为了只评估当前 v02 的 capability 检索和确定性模板，不让外部 Qwen 服务状态影响结果。当前模板直接选择检索 Top-1，因此答案准确率与 Recall@1 相同。

## 核心结果

| 指标 | data_v01 | data_v02 |
|---|---:|---:|
| Recall@1 | 34.55% | 83.64% |
| Recall@2 | 40.00% | 90.91% |
| Recall@3 | 43.64% | 92.73% |
| Recall@4 | 43.64% | 96.36% |
| Recall@5 | 43.64% | 98.18% |
| 答案准确率 | 34.55% | 83.64% |
| 正确答案数 | 19/55 | 46/55 |

v01 数字取自 `data/data_v01/eval_results/evaluation_report.json`。两轮均使用相同的 55 题基准和 Top K=5；v02 使用 rule 模式，适合评价当前“查找正确接口”的阶段目标。

## 分类结果

| 分类 | 数量 | Recall@5 | Top-1/答案准确率 |
|---|---:|---:|---:|
| creation | 11 | 100% | 72.73% |
| linalg | 15 | 100% | 100% |
| manipulation | 16 | 93.75% | 75% |
| other | 3 | 100% | 100% |
| reduction | 10 | 100% | 80% |

## 失败归因

- Top-5 检索未命中：1 题（B043，目标 `bm.sort`）。
- 正确接口已进入 Top-5，但未排到第一：8 题。
- pipeline error：0 题。

| ID | 目标接口 | 正确排名 | 当前 Top-1 |
|---|---|---:|---|
| B010 | `bm.linspace` | 2 | `bm.random.rand` |
| B011 | `bm.asarray` | 4 | `bm.tolist` |
| B012 | `bm.zeros_like` | 2 | `bm.zeros` |
| B021 | `bm.reshape` | 5 | `bm.bitwise_right_shift` |
| B029 | `bm.repeat` | 3 | `bm.unique` |
| B035 | `bm.std` | 2 | `bm.random.randn` |
| B037 | `bm.prod` | 2 | `bm.full` |
| B043 | `bm.sort` | 未进入 Top-5 | `bm.permute_dims` |
| B046 | `bm.broadcast_to` | 4 | `bm.full` |

## 结果文件

- `evaluation_report.json`：完整配置、汇总指标和 55 条逐题详情。
- `failures.jsonl`：9 条失败样例，便于逐条分析。
- `samples.csv`：适合表格查看和不同版本横向比较。

