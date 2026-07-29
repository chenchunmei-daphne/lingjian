# 扩张腔消声器声学分析的控制方程与边界条件

## 1. 求解区域

### 1.1 物理区域

**计算域**：轴对称圆柱管道

**几何参数**（来自表3-1）：

| 参数 | 符号 | 数值 |
|------|------|------|
| 入口管长度 | $L_{in}$ | 0.05 m |
| 扩张腔长度 | $L_e$ | 0.2 m |
| 出口管长度 | $L_{out}$ | 0.05 m |
| 入口管直径 | $D_{in}$ | 0.025 m |
| 扩张腔直径 | $D_e$ | 0.1 m |
| 出口管直径 | $D_{out}$ | 0.05 m |

**半径定义**：
$$R_{in} = \frac{D_{in}}{2} = 0.0125 \text{ m}, \quad R_e = \frac{D_e}{2} = 0.05 \text{ m}, \quad R_{out} = \frac{D_{out}}{2} = 0.025 \text{ m}$$

**z方向分段**：
$$0 \le z \le L_{in} + L_e + L_{out} = 0.30 \text{ m}$$

**分段断点**：
$$z_0 = 0, \quad z_1 = L_{in} = 0.05 \text{ m}, \quad z_2 = L_{in} + L_e = 0.25 \text{ m}, \quad z_3 = L_{in} + L_e + L_{out} = 0.30 \text{ m}$$

**径向范围**（分段函数）：
$$R(z) = 
\begin{cases}
R_{in}, & 0 \le z \le L_{in} \\
R_e, & L_{in} < z \le L_{in} + L_e \\
R_{out}, & L_{in} + L_e < z \le L_{in} + L_e + L_{out}
\end{cases}$$

**求解域**：
$$\Omega = \{(z, r) \mid 0 \le z \le L_{total}, \; 0 \le r \le R(z)\}$$

---

## 2. 控制方程

### 2.1 三维亥姆霍兹方程

$$\frac{\partial^2 p}{\partial x^2} + \frac{\partial^2 p}{\partial y^2} + \frac{\partial^2 p}{\partial z^2} + k^2 p = 0$$

### 2.2 轴对称简化

由于几何和边界条件关于 $z$ 轴旋转对称，声压 $p$ 不依赖于角度 $\theta$：
$$p(r, \theta, z) = p(r, z)$$

得到**轴对称亥姆霍兹方程**：

$$\frac{\partial^2 p}{\partial z^2} + \frac{\partial^2 p}{\partial r^2} + \frac{1}{r}\frac{\partial p}{\partial r} + k^2 p = 0, \quad (z, r) \in \Omega$$

其中：
- $p$ = 复声压（Pa）
- $k = \omega/c = 2\pi f/c$ = 波数（rad/m）
- $f$ = 频率（Hz）
- $c = 340$ m/s = 声速

---

## 3. 边界条件

### 3.1 入口边界（$z = 0, \; 0 \le r \le R_{in}$）

**Sommerfeld辐射边界条件 + 入射波激励**：

$$\left.\frac{\partial p}{\partial z}\right|_{z=0} + i k p = 2 i k \cdot p_{inc}$$

或用外法向形式（$\mathbf{n}$ 指向 $+z$ 方向）：

$$\left.\frac{\partial p}{\partial n}\right|_{inlet} = i k p - 2 i k p_{inc}$$

其中：
- $i = \sqrt{-1}$
- $p_{inc} = 1.0$ Pa = 入射声压幅值
- 第一项 $i k p$：允许反射波离开（非反射）
- 第二项 $-2 i k p_{inc}$：入射波驱动源

### 3.2 出口边界（$z = L_{total}, \; 0 \le r \le R_{out}$）

**Sommerfeld无反射边界条件**：

$$\left.\frac{\partial p}{\partial z}\right|_{z=L_{total}} - i k p = 0$$

或用外法向形式（$\mathbf{n}$ 指向 $+z$ 方向）：

$$\left.\frac{\partial p}{\partial n}\right|_{outlet} = i k p$$

允许声波完全透射出计算域，无反射波返回。

### 3.3 刚性壁面（$r = R(z), \; 0 < z < L_{total}$）

包括：
- 入口管壁面：$0 < z < L_{in}, \; r = R_{in}$
- 扩张腔壁面：$L_{in} < z < L_{in}+L_e, \; r = R_e$
- 出口管壁面：$L_{in}+L_e < z < L_{total}, \; r = R_{out}$
- 入口阶梯面：$z = L_{in}, \; R_{in} \le r \le R_e$
- 出口阶梯面：$z = L_{in}+L_e, \; R_{out} \le r \le R_e$

**Neumann边界条件**：

$$\left.\frac{\partial p}{\partial n}\right|_{wall} = 0$$

物理意义：声波不能穿透壁面，壁面处法向质点振速为零。

### 3.4 轴线条件（$r = 0, \; 0 \le z \le L_{total}$）

**轴对称条件**（由对称性导出）：

$$\left.\frac{\partial p}{\partial r}\right|_{r=0} = 0$$

---

## 4. 边界条件汇总表

| 编号 | 边界位置 | 区域 | 边界条件类型 | 数学表达式 |
|------|---------|------|-------------|-----------|
| 1 | **入口**：$z = 0$ | $0 \le r \le R_{in}$ | Sommerfeld + 激励 | $\frac{\partial p}{\partial n} = i k p - 2 i k p_{inc}$ |
| 2 | **出口**：$z = L_{total}$ | $0 \le r \le R_{out}$ | Sommerfeld 无反射 | $\frac{\partial p}{\partial n} = i k p$ |
| 3 | **刚性壁面**：$r = R(z)$ | $0 < z < L_{total}$ | 刚性壁（Neumann） | $\frac{\partial p}{\partial n} = 0$ |
| 4 | **轴线**：$r = 0$ | $0 \le z \le L_{total}$ | 轴对称条件 | $\frac{\partial p}{\partial r} = 0$ |

---

## 5. 图示：求解区域与边界

```
r
^
|   ════════════════════════════════════════════════════
|   ████████████                           ████████████  ← 入口边界 (z=0)
|   ████████████     扩张腔                ████████████  ← 出口边界 (z=L_total)
|   ████████████  (刚性壁面 r=R_e)        ████████████
|   ████████████                           ████████████
|   ████████████                           ████████████
|   ════════════════════════════════════════════════════
|   ← 刚性壁面 →  ← 刚性壁面 →  ← 刚性壁面 →
|   (r=R_in)       (r=R_e)       (r=R_out)
|   z:0~L_in       z:L_in~L_in+Le z:L_in+Le~L_total
|
|   ===== 轴线 r=0 (∂p/∂r = 0) =====
└────────────────────────────────────────────────────────→ z
   z=0           z=L_in      z=L_in+Le     z=L_total
```

---

## 6. 波数定义

对于给定频率 $f$：

$$k = \frac{2\pi f}{c}$$

其中 $c = 340$ m/s 为声速。

**频率范围**：$f \in [20, 3200]$ Hz