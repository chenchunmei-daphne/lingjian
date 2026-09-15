import chromadb
from sentence_transformers import SentenceTransformer

# 1) 加载开源嵌入模型
MODEL_DIR = r"D:\chen\repo\download_model\bge-m3"
model = SentenceTransformer(MODEL_DIR)

# 试一下
# vec = model.encode(["创建随机张量"], normalize_embeddings=True)
# print(vec.shape)   # 期望输出: (1, 1024)


# 2) 准备"知识条目"（真实场景从 all_interfaces.json 读取）
docs = [
    {
        "id": "bm.random.rand",
        "text": "bm.random.rand 创建均匀分布的随机张量，别名：均匀随机张量。"
                "签名 random.rand(shape, dtype=None, device=None)。"
    },
    {
        "id": "bm.random.randn",
        "text": "bm.random.randn 创建标准正态分布的随机张量，别名：正态随机张量。"
                "签名 random.randn(shape, dtype=None, device=None)。"
    },
    {
        "id": "bm.random.randint",
        "text": "bm.random.randint 创建随机整数张量。"
                "签名 random.randint(low, high=None, shape=None)。"
    },
    {
        "id": "bm.linalg.solve",
        "text": "bm.linalg.solve 求解线性方程组 Ax=b，别名：求解线性方程。"
                "签名 linalg.solve(x1, x2)。"
    },
]

# 3) 构建向量库（Chroma 内存模式，便于演示）
client = chromadb.Client()
collection = client.create_collection(name="fealpy_api")

embeddings = model.encode([d["text"] for d in docs]).tolist()
collection.add(
    ids=[d["id"] for d in docs],
    documents=[d["text"] for d in docs],
    embeddings=embeddings,
)

# 4) 用户提问，做语义检索
queries = [
    "创建随机张量",              # 模糊，想找所有随机创建接口
    "生成高斯分布的数组",        # 用了"高斯""数组"，字面和接口都不同
    "解方程组 Ax=b",            # 数学表达，不是接口名
]

for q in queries:
    q_vec = model.encode([q]).tolist()
    res = collection.query(query_embeddings=q_vec, n_results=2)
    print(f"\n提问：{q}")
    for i, (doc_id, doc, dist) in enumerate(zip(
            res["ids"][0], res["documents"][0], res["distances"][0])):
        print(f"  Top{i+1}: {doc_id}  (距离={dist:.4f})")
        print(f"         {doc[:40]}...")