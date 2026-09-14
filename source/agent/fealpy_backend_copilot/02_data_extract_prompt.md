# FEALPy 接口提取提示词

## 一、背景

FEALPy 是多后端数值计算库，通过 `fealpy.backend` 的 `bm` 对象统一管理后端：

- `numpy` → `numpy.xxx`
- `pytorch` → `torch.xxx`

```python
from fealpy.backend import bm
bm.set_backend("numpy")   # 或 "pytorch"
A = bm.tensor([1, 2, 3])
```

`bm` 上的每个公共方法是一个 FEALPy 接口，需为它提取信息，并记录对应的 NumPy / PyTorch 原始接口。

**源码位置**：`fealpy/fealpy/backend/`，只关注 numpy、pytorch 后端，跳过 paddle、taichi。

## 二、扫描范围

全量扫描：所有分类、所有公共接口。

- 提取：模块级函数、类方法、赋值别名（如 `tensor = array`）
- 跳过：以 `_` 开头的函数、内部辅助函数、测试代码
- 同一接口出现在多个文件时，以实现所在文件为准
- 同一接口在多个后端有实现时，`backends` 同时记录

## 三、字段规范

| 字段 | 说明 | 缺失处理 |
|------|------|----------|
| `id` | `bm.方法名` | 必填 |
| `name` | 接口调用名 | 必填 |
| `full_name` | 如 `bm.tensor` | 必填 |
| `module` | 如 `fealpy.backend` | 从路径推断 |
| `category` | 功能分类，见下表 | 推断 |
| `signature` | 完整函数签名 | 从源码提取 |
| `parameters` | 结构化参数列表 | 从签名提取 |
| `docstring` | 原始文档字符串 | 无则 `null` |
| `description` | 一句话中文描述 | 摘要或推断 |
| `returns` | 返回值说明 | 推断 |
| `source` | `文件路径:L行号` | 必填 |
| `backends` | 各后端映射，见规则 1 | 必填 |
| `is_backend_agnostic` | 后端行为是否一致，见规则 2 | 必填 |
| `backend_diff_notes` | 后端差异说明 | 无则空字符串 |
| `aliases` | 中文别名，至少 1 个 | 必填 |
| `keywords` | 检索关键词 | 必填 |
| `examples` | 使用示例，creation 类至少 1 个 | 必填 |
| `see_also` | 相关接口 id，2-4 个 | 必填 |
| `deprecated` | 是否废弃 | 默认 `false` |
| `doc_quality` | 文档质量，见规则 3 | 必填 |
| `doc_source` | 文档来源，见规则 3 | 必填 |

**分类表（`category`）：**

`creation`（创建）、`math`（数学）、`linalg`（线性代数）、`manipulation`（操作）、`reduction`（归约）、`comparison`（比较）、`dtype`（类型设备）、`other`（其他）。

## 四、判断规则

**规则 1：`backends`**

- 函数体 `return np.xxx(...)` → `backends.numpy.api = "numpy.xxx"`
- 函数体 `return torch.xxx(...)` → `backends.pytorch.api = "torch.xxx"`
- 分发逻辑或无法确定 → 填 `null`，标记 `doc_quality: "missing"`

**规则 2：`is_backend_agnostic`**

满足任一条件标 `true`：

- 命中白名单：`sin, cos, tan, arcsin, arccos, arctan, exp, log, log2, log10, sqrt, abs, sign, floor, ceil, round, isnan, isinf, add, subtract, multiply, divide, power`
- NumPy 与 PyTorch 签名一致且均为单行透传
- 纯 Python 逻辑，不涉及后端差异

否则标 `false`，并在 `backend_diff_notes` 说明差异。

**规则 3：`doc_quality` / `doc_source`**

| 情况 | doc_quality | doc_source |
|------|-------------|------------|
| 有完整 docstring | `complete` | `source_code` |
| 无 docstring，但是广为人知的数学函数 | `auto_filled` | `known_function` |
| 无 docstring，从函数体推断 | `inferred` | `code_inference` |
| 无 docstring，无法推断 | `missing` | `null` |

**规则 4：分类优先级**

多分类可选时按此优先级：`creation` > `linalg` > `reduction` > `math` > `manipulation` > `comparison` / `dtype` / `other`。

**规则 5：`source` 准确性**

- 填主要实现位置，格式 `文件路径:L行号`
- 多后端实现时填 NumPy 后端位置，PyTorch 位置写在 `backend_diff_notes`
- 行号是函数定义或赋值语句所在行，不是调用行

## 五、输出格式

**只输出 JSON 数组，保存到 `lingjian\source\agent\fealpy_backend_copilot\data`，不要输出解释文字或 Markdown 代码块标记。**

无接口时输出 `[]`。

**示例（单条）：**

```json
{
  "id": "bm.tensor",
  "name": "tensor",
  "full_name": "bm.tensor",
  "module": "fealpy.backend",
  "category": "creation",
  "signature": "tensor(data, dtype=None, device=None)",
  "parameters": [
    {"name": "data", "type": "array_like", "default": null, "required": true, "description": "输入数据"},
    {"name": "dtype", "type": "Optional[dtype]", "default": "None", "required": false, "description": "目标数据类型"},
    {"name": "device", "type": "Optional[device]", "default": "None", "required": false, "description": "目标设备"}
  ],
  "docstring": null,
  "description": "根据输入数据创建当前后端的张量",
  "returns": {"type": "Tensor", "description": "新创建的张量"},
  "source": "fealpy/backend/numpy_backend.py:L82",
  "backends": {
    "numpy": {"api": "numpy.array", "notes": "移除 device 参数"},
    "pytorch": {"api": "torch.tensor", "notes": "支持 device"}
  },
  "is_backend_agnostic": false,
  "backend_diff_notes": "NumPy 移除 device；PyTorch 支持 device。",
  "aliases": ["创建张量", "构造张量"],
  "keywords": ["张量", "创建", "tensor"],
  "examples": [
    {"description": "NumPy 后端", "code": "import fealpy.backend as bm\nbm.set_backend(\"numpy\")\nA = bm.tensor([1,2,3])"}
  ],
  "see_also": ["bm.array", "bm.asarray", "bm.zeros"],
  "deprecated": false,
  "doc_quality": "inferred",
  "doc_source": "code_inference"
}
```

## 六、约束

1. 不编造信息，无法推断填 `null` 或空值。
2. 签名完整，包含参数、默认值、类型注解。
3. 行号准确，指向函数定义或赋值语句所在行。
4. 分类拿不准填 `other`。
5. 一致性判断保守，拿不准标 `false`。
6. 输出必须是合法 JSON，无尾随逗号。
7. 只提取公共接口。
8. `description` 用中文，其他字段保持英文。
9. 全量提取，不跳过分类或接口。
10. 传入 paddle、taichi 文件时直接输出 `[]`。
11. `aliases` 至少 1 个，`examples` 中 creation 类至少 1 个，`see_also` 2-4 个。
