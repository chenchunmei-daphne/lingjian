# Python 3.6 环境安装 numpy 1.19 的问题与解决方法

## 背景

QuaDRiGa 的 Python 调用依赖 MATLAB Engine。由于本机 MATLAB 版本较老，只能使用 Python 3.6 环境：

```text
D:\mini\envs\quadriga_py36
```

该环境中 `matlab.engine` 已经可用，但缺少 `numpy`：

```powershell
D:\mini\envs\quadriga_py36\python.exe -c "import numpy"
```

报错：

```text
ModuleNotFoundError: No module named 'numpy'
```

## 没有安装成功的原因

主要原因有三个。

### 1. Python 3.6 对 numpy 版本有限制

Python 3.6 不能安装较新的 numpy。适合 Python 3.6 的 numpy 最后版本是 `1.19.5`。

因此不能直接安装最新版：

```powershell
python -m pip install numpy
```

应该指定版本：

```powershell
python -m pip install numpy==1.19.5
```

### 2. 当前 pip 被配置为不访问包索引

当时环境变量里存在：

```text
PIP_NO_INDEX=1
```

这会导致 pip 不去 PyPI 查询包，所以 pip 会提示找不到版本：

```text
ERROR: Could not find a version that satisfies the requirement numpy==1.19.5
ERROR: No matching distribution found for numpy==1.19.5
```

这个错误容易误判为版本不存在，但实际是 pip 被禁止访问索引。

### 3. 系统代理配置不可用

当时环境中还存在不可用代理：

```text
HTTP_PROXY=http://127.0.0.1:9
HTTPS_PROXY=http://127.0.0.1:9
ALL_PROXY=http://127.0.0.1:9
```

这些代理指向本地不可用端口，导致 pip 访问 PyPI 时触发 TLS/代理相关异常：

```text
ValueError: check_hostname requires server_hostname
```

即使临时清理部分环境变量，pip 仍可能从系统或用户配置读取代理，因此继续失败。

### 4. conda defaults 中的 numpy 1.19.5 不适配当前 Python 3.6 解算

尝试使用 conda 安装：

```powershell
D:\mini\Scripts\conda.exe --no-plugins install -n quadriga_py36 numpy=1.19.5 -y
```

conda 返回依赖冲突，提示该构建需要 Python 3.7/3.8/3.9：

```text
numpy=1.19.5 -> python[version='>=3.7,<3.8.0a0|>=3.8,<3.9.0a0|>=3.9,<3.10.0a0']
Your python: python=3.6
```

所以 conda 也没有直接安装成功。

## 最终解决方法

绕过 pip 的索引解析和代理配置，直接下载与 Python 3.6、Windows 64 位匹配的 wheel 文件，然后从本地 wheel 安装。

### 1. 下载 wheel

下载文件：

```text
numpy-1.19.5-cp36-cp36m-win_amd64.whl
```

使用命令：

```powershell
curl.exe -L --noproxy "*" -o D:\chen\repo\xuantong\numpy-1.19.5-cp36-cp36m-win_amd64.whl https://files.pythonhosted.org/packages/ea/bc/da526221bc111857c7ef39c3af670bbcf5e69c247b0d22e51986f6d0c5c2/numpy-1.19.5-cp36-cp36m-win_amd64.whl
```

其中：

```text
cp36-cp36m
```

表示该 wheel 适用于 Python 3.6。

```text
win_amd64
```

表示该 wheel 适用于 Windows 64 位。

### 2. 从本地 wheel 安装

```powershell
D:\mini\envs\quadriga_py36\python.exe -m pip install --no-index D:\chen\repo\xuantong\numpy-1.19.5-cp36-cp36m-win_amd64.whl
```

安装成功输出：

```text
Successfully installed numpy-1.19.5
```

### 3. 验证安装

```powershell
D:\mini\envs\quadriga_py36\python.exe -c "import numpy, matlab.engine; print('numpy', numpy.__version__); print('matlab.engine ok')"
```

期望输出：

```text
numpy 1.19.5
matlab.engine ok
```

## 建议

以后在这个环境中安装老版本包时，优先确认四件事：

1. 包版本是否支持 Python 3.6。
2. wheel 文件名是否匹配 `cp36` 和 `win_amd64`。
3. 当前 shell 是否设置了 `PIP_NO_INDEX=1`。
4. 当前 shell 或系统是否设置了不可用代理。

如果 pip 索引安装反复失败，可以直接下载匹配的 wheel，再用 `--no-index` 本地安装。
