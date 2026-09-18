# FEALPy Backend Copilot 数据 v02：元数据结构讨论稿

## 1. 本版本要解决的问题

v01 以 FEALPy 接口为唯一记录单元，适合保存签名和源码映射，但大量可检索文本只是“函数名 + 通用分类”的模板化描述。用户通常不会先说接口名，而是描述计算目标，例如“删除长度为 1 的维度”“返回排序后的索引”。因此 v02 将数据拆成两个相互引用的实体：

1. `interfaces`：接口事实层，回答“这个接口是什么、参数是什么、各后端怎么实现”。
2. `capabilities`：计算能力层，回答“用户想完成什么、应该选择哪个接口、为什么不是相似接口”。

核心关系为多对多：一个能力可以需要多个接口；一个接口也可以服务多个参数化能力。

```text
用户问题
   -> capability 检索与判别
   -> interface_refs
   -> interface 事实补全
   -> 答案生成与校验
```

v02 不把接口事实直接改写成自然语言知识，也不把所有问法塞进接口记录。两类数据有不同的更新来源和质量标准。

## 2. 建议的物理文件

定稿后建议生成：

```text
data_v02/
├── README.md                 # 本设计说明
├── metadata.schema.json      # 可执行的 JSON Schema
├── metadata.example.json     # 小规模完整示例
├── manifest.json             # 数据版本、来源和统计信息
├── interfaces.json           # 接口事实数组
├── capabilities.json         # 计算能力数组，主要检索对象
├── eval_dev.json             # 可用于调试的开发集
└── eval_test.json            # 不进入知识库的盲测集
```

当前讨论稿先提供前三个文件，不生成伪造的全量数据。

## 3. 顶层版本信息

`manifest` 用于判断索引与数据是否匹配，建议包含：

| 字段 | 类型 | 含义 |
|---|---|---|
| `schema_version` | string | 元数据协议版本，如 `2.0.0-draft.1` |
| `dataset_version` | string | 数据版本，如 `data_v02` |
| `language` | string | 主要自然语言，当前为 `zh-CN` |
| `source_revision` | string/null | FEALPy commit、tag 或快照标识 |
| `created_at` | string/null | ISO 8601 时间；未知时为 null，不编造 |
| `counts` | object | 接口数、能力数及质量统计 |
| `generation` | object | 提取器、人工审核状态和生成说明 |

`manifest` 是版本元数据，不参与语义检索。

## 4. interfaces：接口事实层

### 4.1 身份和分类

| 字段 | 必填 | 说明 |
|---|---:|---|
| `id` | 是 | 稳定 ID，如 `bm.sum` |
| `full_name` | 是 | 用户实际调用名 |
| `namespace` | 是 | 如 `bm`、`bm.linalg`、`bm.random` |
| `name` | 是 | 末级名称，如 `sum` |
| `category` | 是 | 粗粒度浏览标签，不作为默认硬过滤条件 |
| `summary` | 是 | 精确的一句话接口事实，不使用“执行某类操作”模板 |
| `signature` | 是 | FEALPy 公共签名 |
| `status` | 是 | `active`、`deprecated` 或 `experimental` |

`category` 只是导航属性。检索阶段最多软加权，除非分类器置信度达到经过评测确定的阈值，否则不得用它排除候选。

### 4.2 参数和返回值

参数除名称、类型和默认值外，还需要语义信息：

```json
{
  "name": "axis",
  "kind": "keyword_only",
  "type": "Optional[int | tuple[int, ...]]",
  "required": false,
  "default": null,
  "semantic_role": "reduction_axes",
  "description": "指定执行归约的维度；为 null 时归约所有维度",
  "constraints": [],
  "backend_names": {"numpy": "axis", "pytorch": "dim"}
}
```

`semantic_role` 使用稳定的机器可读值，例如 `input_tensor`、`target_shape`、`reduction_axes`、`output_dtype`、`device`。它用于参数匹配，不能由检索器从长文本中临时猜测。

返回值应记录：

- 返回类型；
- 自然语言含义；
- shape 规则；
- dtype 规则；
- 单值、张量还是 tuple；
- 已确认时才填写 view/copy、原地性和可微性。

无法从源码或测试确认的信息填 `null`，而不是使用通用句子补齐。

### 4.3 后端实现

每个后端记录不只保存 API 名，还要显式描述适配：

| 字段 | 说明 |
|---|---|
| `supported` | 是否支持该后端 |
| `native_api` | 原生 API；没有单一映射时为 null |
| `native_signature` | 已验证的原生签名 |
| `mapping_type` | `direct`、`renamed_params`、`wrapper`、`composed`、`custom`、`unsupported` |
| `parameter_map` | FEALPy 参数到原生参数及转换规则 |
| `return_adaptation` | FEALPy 是否改变原生返回结构 |
| `behavior_notes` | 具体行为差异；禁止“以实际后端为准”式占位文本 |
| `source` | 该后端实现的源码证据 |

跨后端差异放入结构化 `semantic_differences`：

```json
{
  "aspect": "parameter_name",
  "fealpy": "axis",
  "numpy": "axis",
  "pytorch": "dim",
  "impact": "FEALPy 对外统一使用 axis",
  "evidence": ["source:pytorch_backend.py:L..."],
  "confidence": "verified"
}
```

差异维度建议限定为：`parameter_name`、`parameter_form`、`default`、`dtype`、`device`、`shape`、`return_type`、`copy_view`、`autograd`、`error_behavior`、`unsupported` 和 `other`。

### 4.4 来源与质量

每条 interface 和 capability 都包含 `provenance`：

- `sources`：源码、官方文档或测试位置；
- `extraction_method`：`ast`、`runtime_inspection`、`manual` 或 `llm_assisted`；
- `review_status`：`unreviewed`、`machine_checked`、`human_reviewed`；
- `confidence`：`verified`、`high`、`medium`、`low`；
- `issues`：尚未确认的问题。

质量信息必须描述整条记录是否可信，不再用 `complete/inferred/missing` 混合表达“文档是否存在”和“事实是否可靠”。字段级未知值仍使用 null。

## 5. capabilities：计算能力层

capability 是主要向量检索单元。每条记录表示一个可以被明确区分的用户目标，而不是一个宽泛类别。

### 5.1 身份和意图

| 字段 | 必填 | 说明 |
|---|---:|---|
| `id` | 是 | 稳定语义 ID，如 `reduction.sum.all_elements` |
| `canonical_intent` | 是 | 完整动宾短语，如“计算张量所有元素之和” |
| `task_family` | 是 | 粗粒度任务族，仅软过滤 |
| `summary` | 是 | 说明任务语义及适用条件 |
| `user_expressions` | 是 | 多样化且去重的用户表达 |
| `intent_slots` | 是 | shape、axis、dtype、device、order 等可抽取槽位 |
| `interface_refs` | 是 | 对应接口以及使用条件、参数绑定和调用示例 |

`user_expressions` 应覆盖不同表达来源，并为每条表达添加用途标签：

```json
{
  "text": "把张量所有元素加起来",
  "language": "zh-CN",
  "style": "colloquial",
  "source": "curated",
  "include_in_embedding": true
}
```

允许的 `style` 包括 `canonical`、`colloquial`、`mathematical`、`migration`、`parameterized`。测试集原句不得复制进该字段。

### 5.2 接口引用及参数化能力

同一接口的不同参数语义可以拆为不同 capability。例如：

- `norm.vector.l1` -> `bm.linalg.vector_norm(ord=1)`
- `norm.vector.l2` -> `bm.linalg.vector_norm(ord=2)`
- `norm.matrix.frobenius` -> `bm.linalg.matrix_norm(ord="fro")`

`interface_refs` 记录：

- `interface_id`；
- `role`：`primary`、`alternative` 或 `supporting`；
- `when`：适用条件；
- `argument_bindings`：固定参数或从 intent slot 到参数的绑定；
- `call_template`：用于展示和校验的调用模板；
- `priority`：同一能力下确定性的选择顺序。

不要把 `call_template` 当作可执行代码直接运行，它只是答案生成模板。

### 5.3 易混淆能力

`contrasts` 显式记录近邻能力，主要供重排和答案解释使用：

```json
{
  "capability_id": "reduction.cumulative_sum",
  "distinction": "累计和保留逐位置的中间结果；普通求和返回归约结果",
  "selection_cue": "问题包含累计、前缀和或 cumulative 时选择累计和"
}
```

需要优先覆盖以下混淆组：

- `sort` / `argsort`
- `max` / `argmax`，`min` / `argmin`
- `sum` / `cumsum`
- `reshape` / `permute_dims` / `moveaxis`
- `repeat` / `tile`
- `concat` / `stack`
- `array` / `asarray` / `tensor`
- `vector_norm` / `matrix_norm`
- `zeros` / `zeros_like`
- `where` / `nonzero`

### 5.4 预条件、结果和示例

capability 还需要记录：

- `preconditions`：输入 rank、shape、dtype 等要求；
- `result_semantics`：用户可理解的输出含义；
- `examples`：问题、FEALPy 调用及可选后端等价调用；
- `backend_considerations`：只有会影响用户选择的后端差异；
- `tags`：词法检索用的有限关键词。

示例必须展示该 capability 的区分性，不应只是把函数名换成代码。

## 6. 不进入源元数据的派生字段

以下内容应由构建索引时生成，不写回事实数据：

- 拼接后的 embedding 文本；
- tokenizer 结果和向量；
- category 预测值；
- 检索分数、排序分数；
- benchmark 命中次数；
- 根据测试问题自动追加的同义句。

建议索引构建器为每个 capability 生成多个检索文档：

1. 核心意图及用户表达；
2. 参数化场景；
3. NumPy/PyTorch 迁移表达；
4. 易混淆项及选择线索。

所有文档共享 `capability_id`，命中后按 capability 聚合，再读取 interface 事实。

## 7. 完整性和一致性规则

最低校验规则：

1. 所有 ID 在各自实体集合中唯一。
2. 每个 `interface_ref.interface_id` 必须存在。
3. 每个 `contrast.capability_id` 必须存在，且不能引用自身。
4. `primary` interface 至少一个；同一 capability 的 priority 不重复。
5. 参数绑定只能引用目标接口已声明的参数或 capability 已声明的 slot。
6. `mapping_type=unsupported` 时 `supported=false` 且 `native_api=null`。
7. `confidence=verified` 必须至少有一个可定位证据。
8. 占位描述、空泛差异和仅重复函数名的 alias 判为质量错误。
9. category/task_family 不作为默认硬过滤条件。
10. benchmark 测试问题不得直接进入 `user_expressions`。

## 8. v01 到 v02 的迁移策略

迁移分三步，避免一次性重写全部数据：

### 第一步：事实层机械迁移

从 v01 提取接口 ID、签名、参数、源码和后端映射。没有可靠证据的说明保留为 null，并登记到 `provenance.issues`。不复用通用模板 description 作为高质量 summary。

### 第二步：小规模 capability 试验

优先覆盖评测失败密集的 20 个左右接口：

`reshape`、`squeeze`、`expand_dims`、`permute_dims`、`moveaxis`、`repeat`、`tile`、`sort`、`argsort`、`unique`、`broadcast_to`、`sum`、`max`、`min`、`std`、`var`、`prod`、`argmax`、`argmin`、`cumsum`。

先验证 capability Recall@K 和 interface Recall@K，确认结构有效后再全量扩展。

### 第三步：扩展与人工审核

按混淆组而不是按单接口逐条扩展。每完成一个混淆组，同时增加开发集正例、反例和参数化问题。盲测集保持隔离。

## 9. 尚需通过试验决定的问题

以下内容不应在 schema 阶段凭感觉定死：

1. 一个 capability 最适合包含多少条 `user_expressions`。
2. capability 应拆到多细，例如“沿轴求和”和“全部元素求和”是否需要独立记录。
3. embedding 文档按字段拆分还是按表达逐条拆分。
4. dense、lexical、interface hint 三路召回的权重。
5. category 软加权幅度和允许硬过滤的置信度阈值。
6. contrasts 是进入向量文本，还是只供重排器使用。

这些问题使用开发集做消融实验决定，并记录每次实验的数据 SHA256、索引配置和代码版本。

## 10. 本讨论稿的定稿标准

进入全量数据生产前，应满足：

- `metadata.example.json` 能通过 `metadata.schema.json` 校验；
- 20 个失败密集接口已经建立 capability 原型；
- 开发集与盲测集完成隔离；
- capability -> interface -> backend 的答案链路可以追溯；
- 无 category 硬过滤的 v01 基线已固定；
- 新结构在同一开发集上至少分别报告 capability 与 interface 两级指标。

