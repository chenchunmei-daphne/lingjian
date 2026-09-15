import os

# 1) 下载到 D 盘，不走默认 C 盘缓存，避免路径漂移
os.environ["HF_HOME"] = r"D:\chen\repo\download_model\hf_cache"

# 2) 国内网络建议开镜像（不用镜像可注释掉）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 3) 可选：加速下载（需先 pip install hf_transfer，不装也不影响）
# os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

from huggingface_hub import snapshot_download

MODEL_DIR = r"D:\chen\repo\download_model\bge-m3"

path = snapshot_download(
    repo_id="BAAI/bge-m3",
    local_dir=MODEL_DIR,          # 明确落到这个目录（实体文件，不建软链）
    max_workers=4,                # 并发下载
    resume_download=True,         # 断点续传
)
print("模型已下载到:", path)