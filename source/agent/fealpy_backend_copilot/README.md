# FEALPy 多后端接口助手

## 项目介绍

本项目是面向 FEALPy 新成员的多后端接口问答助手。用户可以用自然语言描述张量操作需求，例如“如何创建 GPU 全零张量”或“怎样求解线性方程组”，系统会返回合适的 `bm.*` 接口、参数用法、NumPy/PyTorch 原生接口映射和示例代码。

项目采用检索增强生成（RAG）架构，接口事实来自 FEALPy 源码提取结果，而不是依赖大模型记忆：

```text
FEALPy 源码
  → all_interfaces.json
  → BGE-M3 生成向量
  → Chroma 持久化知识库
  → 用户问题向量检索与规则重排
  → 通义千问根据检索证据回答
```

系统提供两种运行模式：

- 规则 MVP：不调用生成式大模型，由规则解析意图并使用固定模板回答。
- 通义千问模式：使用通义千问解析意图、生成自然回答；调用失败或输出校验失败时自动回退到规则和模板。

当前能力包括：

- 检索 FEALPy `bm.*` 公共接口。
- 返回 NumPy、PyTorch 原生接口映射。
- 识别 creation、linalg、reduction 等接口分类。
- 识别 NumPy/PyTorch、CUDA/GPU、shape、dtype、axis 等约束。
- 支持按 `session_id` 隔离的多轮追问。
- 校验大模型回答中的 FEALPy 接口和后端 API，阻止无依据的接口幻觉。
- 通义千问不可用时自动降级，保证基础检索仍然可用。

## 系统结构

```text
                        ┌──────────────────────┐
                        │ all_interfaces.json  │
                        └──────────┬───────────┘
                                   │ build_vector_kb.py
                                   ▼
                         ┌───────────────────┐
                         │ Chroma + BGE-M3   │
                         └─────────┬─────────┘
                                   │
用户问题 ──→ 意图解析 ──→ retriever.py ──→ 候选接口
   │                                      │
   │                                      ▼
   └── conversation.py ─────→ 答案生成与校验 ──→ 最终回答
```

规则模式依赖关系：

```text
cli.py
  └── agent.py
        ├── intent_parser.py
        ├── retriever.py
        └── answer_generator.py
```

通义千问模式依赖关系：

```text
llm_cli.py / example_llm_agent.py / example_multiturn.py
  └── hybrid_agent.py
        ├── conversation.py
        ├── llm_intent_parser.py
        │     ├── llm_client.py
        │     ├── intent_parser.py（失败回退）
        │     └── prompts/intent_prompt.txt
        ├── retriever.py
        └── llm_answer_generator.py
              ├── llm_client.py
              ├── output_validator.py
              ├── answer_generator.py（失败回退）
              └── prompts/answer_prompt.txt
```

## 项目目录

```text
fealpy_backend_copilot/
├── README.md
├── 01_origin.md
├── 02_data_extract_prompt.md
├── vector_kb.md
├── schemas.py
├── vector_kb.py
├── build_vector_kb.py
├── query_vector_kb.py
├── read_bge_m3_model.py
├── intent_parser.py
├── retriever.py
├── answer_generator.py
├── agent.py
├── cli.py
├── llm_client.py
├── llm_intent_parser.py
├── llm_answer_generator.py
├── output_validator.py
├── conversation.py
├── hybrid_agent.py
├── llm_cli.py
├── example_llm_agent.py
├── example_multiturn.py
├── requirements_vector_kb.txt
├── requirements_llm.txt
├── requirements_app.txt
├── .env.example
├── .gitignore
├── prompts/
│   ├── intent_prompt.txt
│   └── answer_prompt.txt
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   └── service.py
├── ui/
│   ├── __init__.py
│   └── gradio_app.py
├── data/
│   ├── all_interfaces.json
│   └── trial_creation.json
├── vector_store/
│   ├── manifest.json
│   └── chroma/
│       ├── chroma.sqlite3
│       └── <UUID>/
│           ├── data_level0.bin
│           ├── header.bin
│           ├── length.bin
│           └── link_lists.bin
└── tests/
    ├── test_api.py
    └── test_stage2.py
```

## 文件职责及关系

### 需求与说明文档

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `README.md` | 项目总览、架构、目录、配置和使用入口。 | 汇总整个项目的使用方式。 |
| `01_origin.md` | 记录项目原始需求、阶段目标和总体建设流程。 | 是知识提取、RAG 和智能体实现的需求来源。 |
| `02_data_extract_prompt.md` | 定义 FEALPy 接口提取规则、JSON 字段和后端映射要求。 | 指导生成 `data/all_interfaces.json`。 |
| `vector_kb.md` | 记录向量知识库、规则 MVP、通义千问和多轮对话的详细使用方法。 | 对 `build_vector_kb.py`、`query_vector_kb.py` 和智能体入口作补充说明。 |

### 数据与向量知识库

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `data/all_interfaces.json` | 全量 FEALPy 接口知识，是项目的唯一可信结构化数据源。 | 被 `vector_kb.py`、`build_vector_kb.py` 和 `retriever.py` 读取；修改后必须重建 Chroma。 |
| `data/trial_creation.json` | 早期 creation 分类试提取数据。 | 仅用于提取流程验证，不参与正式检索。 |
| `vector_kb.py` | 定义默认路径、读取并校验接口 JSON、拼接嵌入文档、生成 Chroma 元数据。 | 被 `build_vector_kb.py`、`query_vector_kb.py` 和 `retriever.py` 复用。 |
| `build_vector_kb.py` | 使用 BGE-M3 编码全部接口，并全量创建或重建 Chroma Collection。 | 输入为 `all_interfaces.json`，输出到 `vector_store/chroma`，同时更新 `manifest.json`。 |
| `query_vector_kb.py` | 直接查询 Chroma 的独立验证工具。 | 复用 `vector_kb.py` 的路径配置，读取 `vector_store/chroma`，不经过智能体回答生成。 |
| `read_bge_m3_model.py` | 最初的 BGE-M3 与 Chroma 内存模式演示。 | 是 `build_vector_kb.py` 和 `query_vector_kb.py` 的原型参考，不参与正式运行。 |
| `vector_store/manifest.json` | 保存 Collection 名称、记录数、向量维度、模型路径、源数据摘要和建库时间。 | 由 `build_vector_kb.py` 自动生成，用于确认索引与数据版本。 |
| `vector_store/chroma/chroma.sqlite3` | Chroma 的元数据和持久化数据库。 | 由 Chroma 自动管理，供 `retriever.py` 和 `query_vector_kb.py` 读取。 |
| `vector_store/chroma/<UUID>/*.bin` | Chroma/HNSW 的向量、索引头、长度和邻接表等二进制文件。 | 由 Chroma 自动生成和维护，不应手工修改。UUID 目录可能因重建而变化。 |

### 公共数据结构

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `schemas.py` | 定义 `QueryIntent`、`SearchResult`、`AgentAnswer` 和 `ConversationTurn`。 | 被意图解析、检索、答案生成、会话管理和智能体编排模块共同使用。 |

### 不依赖生成式大模型的规则 MVP

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `intent_parser.py` | 使用关键词和正则表达式识别操作、分类、后端、shape、dtype、axis 和 device。 | 被 `agent.py` 直接使用，也是 `llm_intent_parser.py` 的失败回退。 |
| `retriever.py` | 加载 BGE-M3 和 Chroma，执行向量召回、分类软加权、后端过滤和规则重排。category 不作为硬过滤条件，避免错误分类直接丢失正确接口。 | 被规则智能体和混合智能体共同使用；读取 `all_interfaces.json` 和 Chroma。 |
| `answer_generator.py` | 根据检索记录生成确定性的模板答案和示例代码。 | 被 `agent.py` 直接使用，也是 `llm_answer_generator.py` 的失败回退。 |
| `agent.py` | 编排规则意图解析、向量检索和模板回答。 | 由 `cli.py` 调用，不需要通义千问 API。 |
| `cli.py` | 规则 MVP 的命令行入口。 | 创建 `FealpyBackendAgent` 并输出模板答案。 |

### 通义千问混合智能体

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `llm_client.py` | 通过 OpenAI 兼容客户端调用通义千问，管理模型、端点、超时和重试。 | 被 `llm_intent_parser.py` 与 `llm_answer_generator.py` 共用；从环境变量读取密钥。 |
| `llm_intent_parser.py` | 调用通义千问生成结构化意图，并清洗分类、后端、参数和接口提示。 | 读取 `intent_prompt.txt`；失败时调用 `RuleBasedIntentParser`；支持继承上一轮意图。 |
| `llm_answer_generator.py` | 将用户问题、历史、解析意图和检索证据交给通义千问生成自然回答。 | 读取 `answer_prompt.txt`，调用 `output_validator.py`；失败或校验不通过时使用模板答案。 |
| `output_validator.py` | 检查回答中的 `bm.*` 和 `numpy.*`、`torch.*` 是否来自检索证据。 | 被 `llm_answer_generator.py` 调用，阻止无依据的接口和后端 API。 |
| `conversation.py` | 按 `session_id` 保存有限轮次的内存会话，提供历史和上一轮意图。 | 被 `hybrid_agent.py` 使用，并向两个 LLM 阶段提供历史。 |
| `hybrid_agent.py` | 编排通义千问意图解析、向量检索、答案生成、校验、回退和会话状态。 | 是通义千问模式的核心入口，由 `llm_cli.py` 和示例文件调用。 |
| `llm_cli.py` | 通义千问模式的命令行入口，支持单轮和交互式多轮运行。 | 创建 `HybridFealpyBackendAgent`，输出意图来源和答案来源。 |

### 提示词

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `prompts/intent_prompt.txt` | 约束通义千问只输出结构化意图 JSON，并结合历史理解追问。 | 由 `llm_intent_parser.py` 加载。 |
| `prompts/answer_prompt.txt` | 约束通义千问使用自然对话风格，并且只能依据检索证据回答。 | 由 `llm_answer_generator.py` 加载。 |

### 示例、测试与配置

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `example_llm_agent.py` | 单轮或多个独立问题的通义千问调用示例。 | 直接创建并调用 `HybridFealpyBackendAgent`。 |
| `example_multiturn.py` | 使用同一个 `session_id` 连续追问的多轮示例。 | 调用 `hybrid_agent.py`，展示历史继承与会话清理。 |
| `tests/test_stage2.py` | 测试多轮继承、意图清洗、输出校验和失败回退。 | 使用伪客户端，不访问真实通义千问 API，也不依赖实际网络。 |
| `requirements_vector_kb.txt` | BGE-M3 与 Chroma 建库、检索所需依赖。 | 用于运行建库、查询和检索模块。 |
| `requirements_llm.txt` | 通义千问 OpenAI 兼容调用所需依赖。 | 用于运行 LLM 客户端和混合智能体。 |
| `requirements_app.txt` | FastAPI、Uvicorn、Gradio、HTTP 客户端及数据模型依赖。 | 用于运行阶段三 API 服务和 Web 界面。 |
| `.env.example` | 环境变量名称和默认配置示例，不包含真实密钥。 | 对应 `llm_client.py` 读取的配置。 |
| `.gitignore` | 防止真实 `.env` 和密钥配置被提交。 | 与 `.env.example` 配合使用。 |

### FastAPI 服务与 Gradio 界面

| 文件 | 作用 | 与其他文件的关系 |
|---|---|---|
| `api/__init__.py` | 声明 HTTP API Python 包。 | 使 `api.app`、`api.routes` 等模块可被 Uvicorn 导入。 |
| `api/models.py` | 定义聊天、搜索、匹配和健康检查的 Pydantic 请求响应模型。 | 被 `api/routes.py` 用于输入校验和 OpenAPI 文档生成。 |
| `api/service.py` | 管理应用级智能体单例、线程安全调用、日志、接口查询和健康状态。 | 初始化 `HybridFealpyBackendAgent`，供所有 API 路由共享。 |
| `api/routes.py` | 定义 `/health`、`/api/chat`、`/api/search`、接口详情和会话清理路由。 | 从 `app.state` 获取 `AgentService`，通过线程池调用同步模型代码。 |
| `api/app.py` | 创建 FastAPI 应用，并在 lifespan 启动阶段只加载一次模型和向量库。 | 挂载 `api/routes.py`，向 Uvicorn 暴露 `app`。 |
| `ui/__init__.py` | 声明用户界面 Python 包。 | 支持界面代码模块化。 |
| `ui/gradio_app.py` | 单进程启动入口，将 Gradio 对话界面挂载到 FastAPI，并为每个浏览器会话生成独立 ID。 | 直接复用 `AgentService`，一次启动即可同时提供对话页面、API 和会话清理。 |
| `tests/test_api.py` | 验证 API 健康检查、聊天、参数校验、接口详情和会话清理契约。 | 使用假服务，不加载模型、不调用外部 API。 |

## 环境准备

当前项目使用的 Python 环境为：

```text
D:\mini\envs\cgraph_env\python.exe
```

安装依赖：

```powershell
D:\mini\envs\cgraph_env\python.exe -m pip install -r requirements_vector_kb.txt
D:\mini\envs\cgraph_env\python.exe -m pip install -r requirements_llm.txt
D:\mini\envs\cgraph_env\python.exe -m pip install -r requirements_app.txt
```

BGE-M3 默认路径：

```text
D:\chen\repo\download_model\bge-m3
```

## 通义千问配置

项目沿用 `lingjian/source/llm_app_development/daphne/api/openai_api.py` 的调用方式，使用阿里云百炼 OpenAI 兼容端点。真实密钥只能保存在环境变量中：

```powershell
$env:qianwen_openai_api = "你的 API Key"
$env:QIANWEN_MODEL = "qwen-turbo"
```

可选变量见 `.env.example`：

| 变量 | 作用 | 默认值 |
|---|---|---|
| `qianwen_openai_api` | 百炼 API Key，必填。 | 无 |
| `QIANWEN_BASE_URL` | OpenAI 兼容端点。 | 示例代码中的百炼端点 |
| `QIANWEN_MODEL` | 通义千问模型名。 | `qwen-turbo` |
| `QIANWEN_TIMEOUT` | 单次请求超时秒数。 | `60` |
| `QIANWEN_MAX_RETRIES` | 客户端最大重试次数。 | `2` |

## 构建向量知识库

当 `all_interfaces.json` 更新或更换嵌入模型后，运行：

```powershell
D:\mini\envs\cgraph_env\python.exe build_vector_kb.py
```

脚本会全量重建 `fealpy_interfaces` Collection。当前知识库包含 220 条接口、1024 维归一化向量，并使用余弦距离。

## Python 使用示例

### 规则模式

```python
from agent import FealpyBackendAgent

agent = FealpyBackendAgent()
answer = agent.run("怎样创建一个全零张量？", top_k=3)
print(answer.text)
```

### 通义千问模式

```python
from hybrid_agent import HybridFealpyBackendAgent

agent = HybridFealpyBackendAgent()
answer = agent.run(
    "PyTorch 后端如何在 GPU 上创建 3×4 的全零张量？",
    top_k=3,
    session_id="user-1",
)

print(answer.text)
print(answer.intent_source)
print(answer.answer_source)
print(answer.validation_errors)
```

### 多轮追问

```python
from hybrid_agent import HybridFealpyBackendAgent

agent = HybridFealpyBackendAgent()
session_id = "user-1"

print(agent.run(
    "怎样创建一个 3×4 的全零张量？",
    session_id=session_id,
).text)

print(agent.run(
    "那放到 GPU 上呢？",
    session_id=session_id,
).text)

print(agent.run(
    "如果改成 float64 呢？",
    session_id=session_id,
).text)

agent.clear_session(session_id)
```

同一个进程中的同一 `HybridFealpyBackendAgent` 实例和相同 `session_id` 才会共享历史。当前会话只保存在内存中，重启程序后不会保留。

## 回退状态

`AgentAnswer` 中的状态用于判断实际采用的处理路径：

| 状态 | 含义 |
|---|---|
| `intent_source="qwen"` | 通义千问成功解析意图。 |
| `intent_source="rule_fallback"` | LLM 解析失败，已使用规则解析。 |
| `answer_source="qwen"` | 通义千问回答通过事实校验。 |
| `answer_source="template_fallback"` | LLM 调用失败，已使用模板答案。 |
| `answer_source="template_validation_fallback"` | LLM 回答包含无依据的接口或 API，已被校验器拒绝。 |

## 自动化测试

```powershell
D:\mini\envs\cgraph_env\python.exe -m unittest discover -s tests -v
```

测试不调用真实通义千问服务，覆盖会话、意图清洗、接口/API 校验和回退逻辑。

## Benchmark 定量评测

使用 55 条基准题分别运行独立检索和完整聊天链路：

```powershell
D:\mini\envs\cgraph_env\python.exe evaluate_benchmark.py --mode hybrid
```

`hybrid` 使用当前通义千问混合链路；未配置密钥时会按项目既有逻辑回退到规则解析和模板回答。若要显式评测纯规则基线，使用 `--mode rule`。可用 `--limit 3` 做快速冒烟测试。

默认结果写入 `data/eval_results/`：

- `evaluation_report.json`：汇总 Recall@1~5、Answer Accuracy、分类/难度切片和全部逐题证据。
- `samples.csv`：每题 Top1~5、正确 API 排名、最终首选 API 和失败类型，使用 Excel 兼容编码。
- `failures.jsonl`：仅导出失败样本；`retrieval_miss` 表示 Top-5 未召回，`answer_error_after_retrieval_hit` 表示已召回但回答错误，`pipeline_error` 表示运行异常。

Answer Accuracy 按最终回答中首个明确推荐的 `bm.*` API 与标注 API 精确匹配计算，不会因正确 API 仅出现在“其他候选”中而计为正确。每道题使用独立会话，避免多轮记忆污染结果。

进一步定位检索错误时运行：

```powershell
D:\mini\envs\cgraph_env\python.exe retrieval_diagnostics.py
```

该脚本批量执行原始 query、query 加 operation、query 加 category、完整增强 query、取消分类过滤和 Oracle category 六组消融，并分别记录向量原始排名与规则重排排名。结果位于 `data/eval_results/retrieval_diagnostics/`，包含 Recall@1/5/10/20/30、MRR、Mean Rank、知识库覆盖检查和逐题失败归因。

## 启动完整应用（推荐）

进入项目目录后，只需要启动一个文件：

```powershell
D:\mini\envs\cgraph_env\python.exe ui/gradio_app.py
```

这个进程会同时启动 FastAPI 后端和 Gradio 前端：

- 对话窗口：`http://127.0.0.1:8000/chat/`
- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

不需要再打开第二个终端，也不会再由 Gradio 请求一个尚未启动的独立 FastAPI 服务。

## 只启动 FastAPI 服务

从项目目录启动：

```powershell
D:\mini\envs\cgraph_env\python.exe -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

服务启动时只加载一次 BGE-M3、Chroma 和混合智能体。主要接口：

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/health` | 检查模型、向量库、记录数和通义千问配置。 |
| `POST` | `/api/chat` | 多轮问答，接收 `query`、`session_id` 和 `top_k`。 |
| `POST` | `/api/search` | 只执行检索，可指定后端和分类。 |
| `GET` | `/api/interfaces/{id}` | 返回一条完整接口记录。 |
| `DELETE` | `/api/sessions/{session_id}` | 清除指定会话历史。 |

交互式 API 文档位于 `http://127.0.0.1:8000/docs`。

即使没有配置通义千问密钥，服务也能启动；聊天请求会自动使用规则解析和模板回答。

如果不需要网页对话窗口，也可以只运行 `api.app:app`。这种方式仅提供 REST API 和 `/docs`，不挂载 `/chat/`。

完整应用的监听地址可以通过 `FEALPY_HOST` 和 `FEALPY_PORT` 修改。每个浏览器会话会生成独立 ID，并在状态释放时清理对应历史。

## 数据更新规则

1. FEALPy 后端接口发生变化时，更新 `data/all_interfaces.json`。
2. 执行 `build_vector_kb.py` 重建向量库。
3. 检查 `vector_store/manifest.json` 的源文件 SHA-256 和构建时间。
4. 运行 `query_vector_kb.py` 做基础召回验证。
5. 运行 `tests/test_stage2.py` 验证智能体逻辑。

不要手工编辑 `vector_store/chroma` 内的 SQLite 或二进制索引文件。
