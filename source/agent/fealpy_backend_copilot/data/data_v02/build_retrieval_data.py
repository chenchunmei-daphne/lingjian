"""Build the v02 retrieval-MVP dataset from the audited v01 interface list.

The output intentionally contains only facts needed to route a natural-language
calculation request to a FEALPy ``bm.*`` interface. Parameter and backend usage
details belong to a later data version.
"""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
V01_FILE = HERE.parent / "data_v01" / "all_interfaces.json"
OUTPUT_FILE = HERE / "all_interfaces.json"


SEMANTICS = {
    # Backend management and conversion.
    "random.seed": "设置随机数生成器的种子，使随机结果可复现",
    "set_backend": "切换 FEALPy 当前使用的计算后端",
    "load_backend": "加载并返回指定名称的 FEALPy 计算后端",
    "get_current_backend": "获取 FEALPy 当前正在使用的计算后端",
    "is_tensor": "判断一个对象是否为当前后端支持的张量",
    "context": "获取张量的数据类型和设备等上下文信息",
    "set_default_device": "设置当前后端创建张量时使用的默认设备",
    "compile": "编译或优化一个可调用函数以便后续执行",
    "device_type": "获取张量所在设备的类型，例如 CPU 或 GPU",
    "device_index": "获取张量所在设备的编号",
    "get_device": "获取张量所在的计算设备",
    "device_put": "将张量放到指定计算设备上",
    "to_numpy": "将当前后端张量转换为 NumPy 数组",
    "from_numpy": "将 NumPy 数组转换为当前后端张量",
    "tolist": "将张量转换为 Python 列表",
    "astype": "将张量转换为指定数据类型",
    "can_cast": "判断一种数据类型能否安全转换为另一种数据类型",
    "finfo": "查询浮点数据类型的精度和取值范围",
    "iinfo": "查询整数数据类型的取值范围",
    "isdtype": "判断数据类型是否属于指定的数据类型类别",
    "result_type": "推断多个输入共同运算时应使用的数据类型",
    "signbit": "判断各元素的符号位是否为负",
    "take_along_axis": "沿指定维度按照索引张量取出元素",
    "concatenate": "沿已有维度连接多个张量",
    "transpose": "按照给定轴顺序转置张量",
    "unique_counts": "获取唯一元素及每个唯一值的出现次数",
    "unique_inverse": "获取唯一元素及可重建原输入的逆映射索引",
    "unique_values": "只获取张量中的唯一元素值",
    "setdiff1d": "获取只出现在第一个输入而未出现在第二个输入中的元素",
    "coo_spmm": "执行 COO 格式稀疏矩阵与稠密向量或矩阵的乘法",
    "csr_spmm": "执行 CSR 格式稀疏矩阵与稠密向量或矩阵的乘法",
    "csr_spspmm": "执行两个 CSR 格式稀疏矩阵的乘法",
    "coo_tocsr": "把 COO 格式的稀疏矩阵转换为 CSR 格式",

    # Creation and random.
    "random.rand": "创建服从零到一均匀分布的随机张量",
    "random.randint": "创建指定整数区间内的随机整数张量",
    "random.randn": "创建服从标准正态分布的随机张量",
    "arange": "按起点、终点和步长创建等间隔数值序列",
    "asarray": "把输入转换为数组，并尽可能避免不必要的复制",
    "array": "根据输入数据创建数组",
    "tensor": "根据输入数据创建当前后端的张量",
    "empty": "创建指定形状但不初始化元素值的张量",
    "empty_like": "创建与给定张量形状相同但不初始化元素值的张量",
    "eye": "创建二维单位矩阵或带指定对角线的矩阵",
    "full": "创建指定形状且所有元素为同一给定值的张量",
    "full_like": "创建与给定张量形状相同且填充指定值的张量",
    "linspace": "在起点和终点之间创建指定数量的等间隔数值",
    "meshgrid": "根据多个一维坐标序列生成坐标网格",
    "ones": "创建指定形状的全一张量",
    "ones_like": "创建与给定张量形状相同的全一张量",
    "zeros": "创建指定形状的全零张量",
    "zeros_like": "创建与给定张量形状相同的全零张量",

    # Manipulation, searching, sorting and indexed updates.
    "take": "按给定索引从张量中取出元素",
    "broadcast_arrays": "将多个张量广播成相互兼容的共同形状",
    "broadcast_to": "将张量广播到指定目标形状",
    "concat": "沿已有维度连接多个张量",
    "expand_dims": "在指定位置为张量增加一个长度为一的新维度",
    "flip": "沿指定维度反转张量中的元素顺序",
    "moveaxis": "把张量的一个或多个维度移动到新的位置",
    "permute_dims": "按照给定顺序重新排列张量的全部维度",
    "repeat": "逐元素重复张量中的值",
    "reshape": "在元素总数不变的情况下将张量变为指定形状",
    "roll": "沿指定维度循环移动张量元素",
    "squeeze": "删除张量中长度为一的维度",
    "stack": "沿新增加的维度堆叠多个张量",
    "tile": "按照各维度的重复次数平铺整个张量",
    "unstack": "沿指定维度把一个张量拆成多个张量",
    "insert": "在指定位置向数组插入元素",
    "split": "沿指定维度把张量切分成多个部分",
    "swapaxes": "交换张量的两个指定维度",
    "nonzero": "返回张量中所有非零元素的位置索引",
    "searchsorted": "在有序序列中查找插入值后仍保持有序的位置",
    "where": "根据布尔条件从两个输入中逐元素选择值",
    "bincount": "统计非负整数张量中每个取值出现的次数",
    "unique_all": "获取唯一元素以及索引、逆映射和计数等完整信息",
    "unique": "获取张量中的唯一元素并去除重复值",
    "argsort": "返回张量排序后各元素对应的原始索引",
    "sort": "返回沿指定维度排序后的元素值",
    "lexsort": "使用多个键对数据执行稳定的字典序排序",
    "copy": "复制张量并得到独立的新张量",
    "size": "获取张量的元素总数或指定维度的长度",
    "set_at": "在指定索引位置写入或替换张量元素",
    "add_at": "把给定值累加到张量的指定索引位置",
    "index_add": "沿指定维度按索引把源张量累加到目标张量",
    "scatter": "沿指定维度按索引把值写入目标张量",
    "scatter_add": "沿指定维度按索引把值累加到目标张量",

    # Reductions.
    "argmax": "返回张量最大元素所在的位置索引",
    "argmin": "返回张量最小元素所在的位置索引",
    "cumulative_sum": "沿指定维度计算包含初始值语义的累计和",
    "max": "计算张量全部元素或指定维度上的最大值",
    "mean": "计算张量全部元素或指定维度上的平均值",
    "min": "计算张量全部元素或指定维度上的最小值",
    "prod": "计算张量全部元素或指定维度上的乘积",
    "std": "计算张量全部元素或指定维度上的标准差",
    "sum": "计算张量全部元素或指定维度上的元素之和",
    "var": "计算张量全部元素或指定维度上的方差",
    "cumsum": "沿指定维度计算累计和并保留各位置的中间结果",
    "cumprod": "沿指定维度计算累计乘积并保留各位置的中间结果",
    "all": "判断张量全部元素或指定维度上的元素是否都为真",
    "any": "判断张量全部元素或指定维度上是否至少有一个元素为真",

    # Linear algebra (namespace is stripped when looking up these entries).
    "cholesky": "对对称正定矩阵进行 Cholesky 分解",
    "cross": "计算三维向量或向量数组的叉积",
    "det": "计算方阵的行列式",
    "diagonal": "提取矩阵或批量矩阵的对角线元素",
    "eigh": "计算实对称或复 Hermitian 矩阵的特征值和特征向量",
    "eigvalsh": "只计算实对称或复 Hermitian 矩阵的特征值",
    "inv": "计算可逆方阵的逆矩阵",
    "matmul": "执行矩阵乘法或批量矩阵乘法",
    "matrix_norm": "计算矩阵范数，例如 Frobenius 范数或核范数",
    "matrix_power": "计算方阵的整数次幂",
    "matrix_rank": "计算矩阵的秩",
    "matrix_transpose": "交换矩阵最后两个维度以得到矩阵转置",
    "outer": "计算两个向量的外积",
    "pinv": "计算矩阵的 Moore-Penrose 伪逆",
    "qr": "对矩阵进行 QR 分解",
    "slogdet": "计算行列式的符号和绝对值的自然对数",
    "solve": "求解线性方程组",
    "svd": "对矩阵进行奇异值分解并返回奇异向量和奇异值",
    "svdvals": "只计算矩阵的奇异值",
    "tensordot": "沿指定维度对两个张量执行缩并",
    "trace": "计算矩阵对角线元素之和",
    "vecdot": "沿指定维度计算两个向量的点积",
    "vector_norm": "计算向量范数，支持指定阶数和维度",
    "dot": "计算两个输入的点积或按相应规则执行乘积求和",
    "einsum": "使用爱因斯坦求和表达式描述张量运算",

    # Transformations, autodiff and FEALPy geometry helpers.
    "tril": "提取矩阵的下三角部分并将其余元素置零",
    "triu": "提取矩阵的上三角部分并将其余元素置零",
    "apply_along_axis": "沿数组指定维度对一维切片应用函数",
    "vmap": "把处理单个样本的函数向量化为批量函数",
    "grad": "构造计算标量函数梯度的函数",
    "jvp": "计算函数在给定切向量方向上的 Jacobian-向量积",
    "vjp": "计算给定余切向量与函数 Jacobian 的向量-Jacobian 积",
    "jacfwd": "使用前向模式自动微分计算函数的 Jacobian",
    "jacrev": "使用反向模式自动微分计算函数的 Jacobian",
    "hessian": "计算标量函数的 Hessian 矩阵",
    "query_point": "在周期盒及给定搜索半径下查询点的邻居",
    "multi_index_matrix": "生成给定次数和维数的多重指标矩阵",
    "edge_length": "根据节点坐标和边连接关系计算每条边的长度",
    "edge_normal": "计算二维网格边的法向量",
    "edge_tangent": "计算网格边的切向量",
    "tensorprod": "计算多个张量的一般化张量积",
    "bc_to_points": "利用重心坐标将网格实体上的点转换为物理坐标",
    "barycenter": "计算网格实体顶点的重心坐标位置",
    "simplex_measure": "计算单纯形网格实体的几何测度",
    "simplex_shape_function": "计算单纯形有限元形函数值",
    "simplex_grad_shape_function": "计算单纯形有限元形函数的梯度",
    "simplex_hess_shape_function": "计算单纯形有限元形函数的 Hessian",
    "tensor_measure": "计算由张量积结构表示的网格实体测度",
    "interval_grad_lambda": "计算区间单元重心坐标函数的梯度",
    "triangle_area_3d": "计算三维空间中三角形的面积",
    "triangle_grad_lambda_2d": "计算二维三角形重心坐标函数的梯度",
    "triangle_grad_lambda_3d": "计算三维空间三角形重心坐标函数的梯度",
    "quadrangle_grad_lambda_2d": "计算二维四边形参考坐标函数的梯度",
    "tetrahedron_grad_lambda_3d": "计算三维四面体重心坐标函数的梯度",
}


UNARY_MATH = {
    "abs": "绝对值", "acos": "反余弦", "acosh": "反双曲余弦",
    "asin": "反正弦", "asinh": "反双曲正弦", "atan": "反正切",
    "atanh": "反双曲正切", "ceil": "向上取整", "conj": "复共轭",
    "cos": "余弦", "cosh": "双曲余弦", "exp": "自然指数",
    "expm1": "自然指数减一", "floor": "向下取整", "imag": "虚部",
    "log": "自然对数", "log1p": "一加输入值的自然对数", "log2": "以二为底的对数",
    "log10": "以十为底的对数", "negative": "相反数", "positive": "正值恒等变换",
    "real": "实部", "round": "舍入值", "sign": "符号值", "sin": "正弦",
    "sinh": "双曲正弦", "square": "平方", "sqrt": "平方根",
    "tan": "正切", "tanh": "双曲正切", "trunc": "向零截断后的整数部分",
    "arcsin": "反正弦", "arccos": "反余弦", "arctan": "反正切",
    "arcsinh": "反双曲正弦", "arccosh": "反双曲余弦", "arctanh": "反双曲正切",
    "bitwise_invert": "逐位取反结果",
}

BINARY_MATH = {
    "add": "逐元素相加", "atan2": "根据纵横坐标计算四象限反正切",
    "arctan2": "根据纵横坐标计算四象限反正切", "bitwise_and": "逐位与",
    "bitwise_left_shift": "逐位左移", "bitwise_or": "逐位或",
    "bitwise_right_shift": "逐位右移", "bitwise_xor": "逐位异或",
    "copysign": "把第二个输入的符号复制到第一个输入的绝对值上",
    "divide": "逐元素相除", "floor_divide": "逐元素整除", "hypot": "直角三角形斜边长度",
    "logaddexp": "两个输入指数和的对数", "maximum": "两个输入逐元素比较后的较大值",
    "minimum": "两个输入逐元素比较后的较小值", "multiply": "逐元素相乘",
    "pow": "逐元素幂", "power": "逐元素幂", "remainder": "逐元素除法的余数", "subtract": "逐元素相减",
    "clip": "把元素限制在给定的最小值和最大值之间",
}

COMPARISON = {
    "equal": "判断两个输入的对应元素是否相等",
    "greater": "判断第一个输入的对应元素是否大于第二个输入",
    "greater_equal": "判断第一个输入的对应元素是否大于或等于第二个输入",
    "isfinite": "判断各元素是否为有限数值",
    "isinf": "判断各元素是否为正无穷或负无穷",
    "isnan": "判断各元素是否为非数值 NaN",
    "less": "判断第一个输入的对应元素是否小于第二个输入",
    "less_equal": "判断第一个输入的对应元素是否小于或等于第二个输入",
    "logical_and": "对两个布尔输入逐元素执行逻辑与",
    "logical_not": "对布尔输入逐元素执行逻辑非",
    "logical_or": "对两个布尔输入逐元素执行逻辑或",
    "logical_xor": "对两个布尔输入逐元素执行逻辑异或",
    "not_equal": "判断两个输入的对应元素是否不相等",
    "isin": "判断输入中的每个元素是否出现在候选元素集合中",
    "allclose": "判断两个张量在给定容差内是否整体近似相等",
}


CONTRASTS = {
    "sum": [("bm.cumsum", "普通求和返回归约结果；累计和保留各位置的中间结果", "出现累计、前缀和时选择 bm.cumsum"),
            ("bm.add", "求和归约一个张量中的多个元素；add 对两个输入逐元素相加", "出现两个张量逐元素相加时选择 bm.add")],
    "cumsum": [("bm.sum", "累计和保留各位置的中间结果；普通求和返回归约结果", "只要求总和时选择 bm.sum")],
    "cumulative_sum": [("bm.cumsum", "两者都是累计和接口，但 cumulative_sum 遵循数组 API 的初始值语义", "一般兼容旧调用时优先确认是否需要 bm.cumsum")],
    "max": [("bm.argmax", "max 返回最大值；argmax 返回最大值所在索引", "问题询问位置或索引时选择 bm.argmax"),
            ("bm.maximum", "max 对单个张量做归约；maximum 对两个输入逐元素取较大值", "比较两个张量对应元素时选择 bm.maximum")],
    "argmax": [("bm.max", "argmax 返回最大值的位置；max 返回最大值本身", "问题只要求最大值时选择 bm.max")],
    "min": [("bm.argmin", "min 返回最小值；argmin 返回最小值所在索引", "问题询问位置或索引时选择 bm.argmin"),
            ("bm.minimum", "min 对单个张量做归约；minimum 对两个输入逐元素取较小值", "比较两个张量对应元素时选择 bm.minimum")],
    "argmin": [("bm.min", "argmin 返回最小值的位置；min 返回最小值本身", "问题只要求最小值时选择 bm.min")],
    "sort": [("bm.argsort", "sort 返回排序后的值；argsort 返回排序对应的原始索引", "问题要求索引或排列次序时选择 bm.argsort")],
    "argsort": [("bm.sort", "argsort 返回排序索引；sort 返回排序后的值", "问题要求排序值时选择 bm.sort")],
    "reshape": [("bm.permute_dims", "reshape 改变维度大小；permute_dims 只重新排列维度顺序", "只交换轴顺序时选择 bm.permute_dims"),
                ("bm.moveaxis", "reshape 指定新形状；moveaxis 把特定轴移动到新位置", "明确移动某一轴时选择 bm.moveaxis")],
    "permute_dims": [("bm.reshape", "permute_dims 重排轴顺序；reshape 改变维度大小", "给出目标 shape 时选择 bm.reshape")],
    "moveaxis": [("bm.permute_dims", "moveaxis 指定源轴和目标位置；permute_dims 给出全部轴的新顺序", "给出完整轴排列时选择 bm.permute_dims")],
    "repeat": [("bm.tile", "repeat 逐元素重复；tile 按维度平铺整个张量", "要求按各维度复制整个数组时选择 bm.tile")],
    "tile": [("bm.repeat", "tile 平铺整个张量；repeat 逐元素重复", "要求每个元素分别重复时选择 bm.repeat")],
    "concat": [("bm.stack", "concat 沿已有维度连接；stack 会新增一个维度", "要求新增维度时选择 bm.stack")],
    "concatenate": [("bm.stack", "concatenate 沿已有维度连接；stack 会新增一个维度", "要求新增维度时选择 bm.stack"),
                    ("bm.concat", "concatenate 与 concat 都表示沿已有维度连接，优先使用当前代码规范采用的名称", "项目明确使用 concat 名称时选择 bm.concat")],
    "stack": [("bm.concat", "stack 新增维度后堆叠；concat 沿已有维度连接", "不增加维度时选择 bm.concat")],
    "zeros": [("bm.zeros_like", "zeros 根据显式形状创建；zeros_like 复制已有张量的形状", "以现有张量为模板时选择 bm.zeros_like")],
    "zeros_like": [("bm.zeros", "zeros_like 使用已有张量的形状；zeros 使用显式目标形状", "直接给出 shape 时选择 bm.zeros")],
    "ones": [("bm.ones_like", "ones 根据显式形状创建；ones_like 复制已有张量的形状", "以现有张量为模板时选择 bm.ones_like")],
    "ones_like": [("bm.ones", "ones_like 使用已有张量的形状；ones 使用显式目标形状", "直接给出 shape 时选择 bm.ones")],
    "full": [("bm.full_like", "full 根据显式形状填充值；full_like 复制已有张量的形状", "以现有张量为模板时选择 bm.full_like")],
    "full_like": [("bm.full", "full_like 使用已有张量的形状；full 使用显式目标形状", "直接给出 shape 时选择 bm.full")],
    "empty": [("bm.empty_like", "empty 根据显式形状创建；empty_like 复制已有张量的形状", "以现有张量为模板时选择 bm.empty_like")],
    "empty_like": [("bm.empty", "empty_like 使用已有张量的形状；empty 使用显式目标形状", "直接给出 shape 时选择 bm.empty")],
    "where": [("bm.nonzero", "where 在两个输入中选择值；nonzero 返回非零元素的位置", "只需要非零位置时选择 bm.nonzero")],
    "nonzero": [("bm.where", "nonzero 返回位置索引；where 根据条件选择结果值", "需要在两个值之间选择时使用 bm.where")],
    "vector_norm": [("bm.linalg.matrix_norm", "vector_norm 计算向量范数；matrix_norm 按矩阵语义计算范数", "明确要求 Frobenius 范数或核范数时选择 bm.linalg.matrix_norm")],
    "matrix_norm": [("bm.linalg.vector_norm", "matrix_norm 按矩阵语义计算范数；vector_norm 按向量或指定轴计算范数", "输入按向量处理时选择 bm.linalg.vector_norm")],
    "svd": [("bm.linalg.svdvals", "svd 返回奇异向量和奇异值；svdvals 只返回奇异值", "只需要奇异值时选择 bm.linalg.svdvals")],
    "svdvals": [("bm.linalg.svd", "svdvals 只返回奇异值；svd 还返回奇异向量", "需要完整分解时选择 bm.linalg.svd")],
    "eigh": [("bm.linalg.eigvalsh", "eigh 返回特征值和特征向量；eigvalsh 只返回特征值", "只需要特征值时选择 bm.linalg.eigvalsh")],
    "eigvalsh": [("bm.linalg.eigh", "eigvalsh 只返回特征值；eigh 还返回特征向量", "需要特征向量时选择 bm.linalg.eigh")],
    "det": [("bm.linalg.slogdet", "det 直接返回行列式；slogdet 返回符号和绝对值对数", "需要数值更稳定的对数形式时选择 bm.linalg.slogdet")],
    "array": [("bm.asarray", "array 强调创建数组；asarray 强调转换并尽量避免复制", "希望复用已有存储时选择 bm.asarray"),
              ("bm.tensor", "array 使用数组命名；tensor 强调创建当前后端张量", "以统一张量概念表达时选择 bm.tensor")],
    "asarray": [("bm.array", "asarray 尽量避免复制；array 强调创建数组", "明确需要新数组时选择 bm.array")],
}


# v01 was extracted before several public mappings and sparse helpers were
# audited. These entries are present in the current NumPy/PyTorch backend
# implementation and are added explicitly instead of silently inheriting the
# old omission. Constants and dtype attributes are not callable interfaces and
# remain outside this retrieval dataset.
EXTRA_INTERFACES = [
    ("bm.signbit", "signbit", "math", "fealpy/backend/base.py:L167"),
    ("bm.power", "power", "math", "fealpy/backend/base.py:L172"),
    ("bm.take_along_axis", "take_along_axis", "manipulation", "fealpy/backend/base.py:L176"),
    ("bm.concatenate", "concatenate", "manipulation", "fealpy/backend/base.py:L206"),
    ("bm.transpose", "transpose", "manipulation", "fealpy/backend/base.py:L207"),
    ("bm.unique_counts", "unique_counts", "manipulation", "fealpy/backend/base.py:L218"),
    ("bm.unique_inverse", "unique_inverse", "manipulation", "fealpy/backend/base.py:L218"),
    ("bm.unique_values", "unique_values", "manipulation", "fealpy/backend/base.py:L218"),
    ("bm.setdiff1d", "setdiff1d", "manipulation", "fealpy/backend/base.py:L221"),
    ("bm.coo_spmm", "coo_spmm", "linalg", "fealpy/backend/numpy_backend.py:L157"),
    ("bm.csr_spmm", "csr_spmm", "linalg", "fealpy/backend/numpy_backend.py:L181"),
    ("bm.csr_spspmm", "csr_spspmm", "linalg", "fealpy/backend/numpy_backend.py:L202"),
    ("bm.coo_tocsr", "coo_tocsr", "manipulation", "fealpy/backend/numpy_backend.py:L210"),
]


# Multiple public names can express exactly the same operation. They share one
# capability so equivalent names do not compete as separate semantic results.
# The mapping value is the preferred interface returned by the retrieval MVP.
EQUIVALENT_PRIMARY = {
    "bm.linalg.cross": "bm.cross",
    "bm.linalg.matmul": "bm.matmul",
    "bm.linalg.matrix_transpose": "bm.matrix_transpose",
    "bm.linalg.tensordot": "bm.tensordot",
    "bm.linalg.trace": "bm.trace",
    "bm.linalg.vecdot": "bm.vecdot",
    "bm.arccos": "bm.acos",
    "bm.arccosh": "bm.acosh",
    "bm.arcsin": "bm.asin",
    "bm.arcsinh": "bm.asinh",
    "bm.arctan": "bm.atan",
    "bm.arctan2": "bm.atan2",
    "bm.arctanh": "bm.atanh",
    "bm.power": "bm.pow",
    "bm.concatenate": "bm.concat",
}


SYNONYMS = {
    "sum": "求总和", "mean": "求平均值", "std": "求标准差", "var": "求方差",
    "prod": "求元素乘积", "reshape": "重设张量形状", "squeeze": "去掉单维度",
    "expand_dims": "增加新维度", "concat": "连接多个张量", "stack": "堆叠多个张量",
    "argsort": "获取排序索引", "sort": "对元素排序", "nonzero": "查找非零位置",
    "inv": "求逆矩阵", "det": "求行列式", "solve": "解线性方程组",
    "matrix_rank": "求矩阵秩", "vector_norm": "求向量范数", "matrix_norm": "求矩阵范数",
    "zeros": "创建全零张量", "ones": "创建全一张量", "full": "创建常数填充张量",
    "random.rand": "生成均匀随机数", "random.randn": "生成标准正态随机数",
    "random.randint": "生成随机整数", "random.seed": "固定随机种子",
}


def semantic_key(record: dict) -> str:
    name = record["name"]
    if name.startswith("linalg."):
        return name.split(".", 1)[1]
    return name


def summary_for(record: dict) -> str:
    name = semantic_key(record)
    full_name = record["name"]
    if full_name in SEMANTICS:
        return SEMANTICS[full_name]
    if name in SEMANTICS:
        return SEMANTICS[name]
    if name in UNARY_MATH:
        return f"逐元素计算输入张量的{UNARY_MATH[name]}"
    if name in BINARY_MATH:
        return f"对输入张量{BINARY_MATH[name]}"
    if name in COMPARISON:
        return COMPARISON[name]
    raise KeyError(f"No curated semantics for {record['id']}")


def capability_id(record: dict) -> str:
    # Interface-qualified IDs stay unique for top-level and linalg aliases.
    return "interface." + record["id"].removeprefix("bm.")


def expressions_for(record: dict, summary: str) -> list[str]:
    key = record["name"] if record["name"] in SYNONYMS else semantic_key(record)
    short = SYNONYMS.get(key)
    expressions = [
        summary,
        f"如何{summary}",
        f"我想{summary}",
        f"FEALPy 中用什么接口可以{summary}",
    ]
    if short:
        expressions.insert(1, short)
    # Stable de-duplication.
    return list(dict.fromkeys(expressions))


def tags_for(record: dict, summary: str) -> list[str]:
    name = semantic_key(record)
    tags = [name, record["name"], record["category"]]
    if name in SYNONYMS:
        tags.append(SYNONYMS[name])
    # Add a few discriminative phrases instead of tokenizing every common word.
    for term in ("索引", "形状", "维度", "随机", "矩阵", "向量", "梯度", "网格", "坐标", "排序", "累计", "设备", "类型"):
        if term in summary:
            tags.append(term)
    return list(dict.fromkeys(tags))


def build() -> dict:
    old_records = json.loads(V01_FILE.read_text(encoding="utf-8"))
    old_ids = {record["id"] for record in old_records}
    old_records.extend(
        {
            "id": interface_id,
            "name": name,
            "category": category,
            "source": source,
        }
        for interface_id, name, category, source in EXTRA_INTERFACES
        if interface_id not in old_ids
    )
    interfaces = []
    capabilities = []
    all_ids = {record["id"] for record in old_records}

    records_by_id = {record["id"]: record for record in old_records}

    for record in old_records:
        summary = summary_for(record)
        interfaces.append({
            "id": record["id"],
            "name": record["name"],
            "summary": summary,
            "category": record["category"],
            "source": record["source"],
        })

    alternatives_by_primary: dict[str, list[str]] = {}
    for alternative, primary in EQUIVALENT_PRIMARY.items():
        if alternative in records_by_id and primary in records_by_id:
            alternatives_by_primary.setdefault(primary, []).append(alternative)

    for record in old_records:
        if record["id"] in EQUIVALENT_PRIMARY:
            continue
        summary = summary_for(record)
        contrast_items = []
        for interface_id, difference, cue in CONTRASTS.get(semantic_key(record), []):
            if interface_id in all_ids and interface_id != record["id"]:
                contrast_items.append({
                    "interface_id": interface_id,
                    "difference": difference,
                    "selection_cue": cue,
                })

        target_interfaces = [{
            "id": record["id"],
            "role": "primary",
            "reason": summary,
        }]
        target_interfaces.extend(
            {
                "id": alternative,
                "role": "alternative",
                "reason": f"与 {record['id']} 表示相同计算能力的兼容入口",
            }
            for alternative in alternatives_by_primary.get(record["id"], [])
        )

        capabilities.append({
            "id": capability_id(record),
            "intent": summary,
            "expressions": expressions_for(record, summary),
            "target_interfaces": target_interfaces,
            "contrasts": contrast_items,
            "tags": tags_for(record, summary),
        })

    return {
        "schema_version": "2.0.0-retrieval-mvp",
        "dataset_version": "data_v02",
        "scope": "根据用户描述的计算功能检索正确的 FEALPy bm.* 接口",
        "interfaces": interfaces,
        "capabilities": capabilities,
    }


def validate(data: dict) -> None:
    interface_ids = [item["id"] for item in data["interfaces"]]
    capability_ids = [item["id"] for item in data["capabilities"]]
    assert len(interface_ids) == len(set(interface_ids)), "duplicate interface ID"
    assert len(capability_ids) == len(set(capability_ids)), "duplicate capability ID"
    known = set(interface_ids)
    for capability in data["capabilities"]:
        assert capability["intent"].strip()
        assert len(capability["expressions"]) >= 4
        assert capability["target_interfaces"]
        assert all(item["id"] in known for item in capability["target_interfaces"])
        assert all(item["interface_id"] in known for item in capability["contrasts"])


def main() -> None:
    data = build()
    validate(data)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(data['interfaces'])} interfaces and "
          f"{len(data['capabilities'])} capabilities to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
