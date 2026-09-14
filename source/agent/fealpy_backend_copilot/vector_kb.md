# FEALPy 接口向量知识库

## 文件结构

```text
fealpy_backend_copilot/
├── data/
│   └── all_interfaces.json       # 唯一可信的结构化接口数据源
├── vector_store/                 # 运行建库脚本后生成
│   ├── manifest.json             # 模型、数据摘要和构建信息
│   └── chroma/                   # Chroma 持久化数据库
├── vector_kb.py                  # 文档拼接、元数据与路径配置
├── build_vector_kb.py            # 全量构建/重建向量库
├── query_vector_kb.py            # 命令行检索与验证
├── schemas.py                    # 意图、检索结果和答案结构
├── intent_parser.py              # 不依赖大模型的规则意图解析
├── retriever.py                  # 向量召回、后端过滤与规则重排
├── answer_generator.py           # 基于知识记录的模板答案生成
├── agent.py                      # 串联解析、检索和答案生成
├── cli.py                        # MVP 命令行入口
├── requirements-vector-kb.txt    # Python 依赖
└── read_bge_m3_model.py          # 原始演示脚本，可保留作参考
```

`all_interfaces.json` 是唯一需要人工维护的数据文件。`vector_store` 中的内容均由建库脚本生成；接口数据更新后，应重新运行建库脚本。

## 构建

当前可用环境：

```powershell
D:\mini\envs\cgraph_env\python.exe .\lingjian\source\agent\fealpy_backend_copilot\build_vector_kb.py
```

默认路径：

- 数据：`data/all_interfaces.json`
- 模型：仓库根目录下的 `download_model/bge-m3`
- 数据库：`vector_store/chroma`
- Collection：`fealpy_interfaces`

路径均可覆盖：

```powershell
python build_vector_kb.py --data DATA.json --model MODEL_DIR --db DB_DIR
```

## 查询

```powershell
D:\mini\envs\cgraph_env\python.exe .\lingjian\source\agent\fealpy_backend_copilot\query_vector_kb.py "如何创建正态分布随机张量" --top-k 5
```

按分类过滤：

```powershell
D:\mini\envs\cgraph_env\python.exe .\lingjian\source\agent\fealpy_backend_copilot\query_vector_kb.py "求解 Ax=b" --category linalg
```

每个接口对应一个向量文档，内容包括接口名、中文描述、别名、签名、参数、NumPy/PyTorch 映射、后端差异、关键词和源码位置。Chroma 元数据保留适合过滤和展示的标量字段。

## 接入通义千问

智能体通过阿里云百炼的 OpenAI 兼容端点调用通义千问。密钥只从环境变量读取，不应写入代码：

```powershell
$env:qianwen_openai_api = "你的 API Key"
$env:QIANWEN_MODEL = "qwen-turbo"
```

运行完整流程：

```powershell
D:\mini\envs\cgraph_env\python.exe .\lingjian\source\agent\fealpy_backend_copilot\llm_cli.py "PyTorch 后端如何在 GPU 上创建 3×4 的全零张量？" --top-k 3
```

处理链路：

```text
用户问题
  → 通义千问结构化意图解析
  → BGE-M3 + Chroma 检索
  → 分类、后端过滤和重排
  → 通义千问依据检索证据生成回答
```

当意图解析调用失败时，系统自动使用 `RuleBasedIntentParser`；当答案生成调用失败时，自动使用 `TemplateAnswerGenerator`。命令输出开头的 `intent=qwen` 和 `answer=qwen` 表示两个大模型步骤均成功。

### 多轮对话

同一个智能体实例和 `session_id` 会保留最近的对话，后续问题可以继承上一轮的操作、分类、后端和参数：

```python
from hybrid_agent import HybridFealpyBackendAgent

agent = HybridFealpyBackendAgent()

answer1 = agent.run(
    "怎样创建一个 3×4 的全零张量？",
    session_id="user-1",
)
answer2 = agent.run(
    "那放到 GPU 上呢？",
    session_id="user-1",
)

print(answer1.text)
print(answer2.text)

agent.clear_session("user-1")
```

完整示例见 `example_multiturn.py`。当前会话状态保存在进程内存中，服务重启后不会保留。

### 输出校验与回退

`GroundedAnswerValidator` 会检查大模型回答中的 `bm.*` 接口和 `numpy.*`、`torch.*` API 是否存在于本次检索证据中。如果回答引用未检索到的接口、编造后端 API 或没有引用任何候选接口，系统会丢弃该回答并返回模板答案，状态显示为 `answer=template_validation_fallback`。

运行自动化测试：

```powershell
D:\mini\envs\cgraph_env\python.exe -m unittest discover -s .\lingjian\source\agent\fealpy_backend_copilot\tests -v
```

相关文件：

- `llm_client.py`：通义千问兼容客户端、模型和超时配置。
- `llm_intent_parser.py`：结构化意图解析和规则回退。
- `llm_answer_generator.py`：基于检索证据生成答案和模板回退。
- `hybrid_agent.py`：编排完整链路。
- `llm_cli.py`：命令行入口。
- `prompts/intent_prompt.txt`：意图解析约束。
- `prompts/answer_prompt.txt`：知识库约束与回答格式。

## 规则驱动智能体 MVP

MVP 不调用生成式大模型。它依次执行规则意图解析、BGE-M3 向量召回、分类与后端过滤、关键词重排和模板答案生成。

```powershell
D:\mini\envs\cgraph_env\python.exe .\lingjian\source\agent\fealpy_backend_copilot\cli.py "PyTorch 后端如何在 GPU 上创建 3×4 的全零张量？" --top-k 3
```

程序会输出推荐的 FEALPy 接口、签名、参数、NumPy/PyTorch 映射、可执行示例、候选接口、源码位置和匹配分数。
