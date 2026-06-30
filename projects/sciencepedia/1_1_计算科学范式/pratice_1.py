from fealpy.backend import bm
from fealpy.backend import TensorLike

def step_correct(u: TensorLike, alpha: float) -> TensorLike:
    """
    Performs one time step of the 1D heat equation with periodic boundary condition
    """
    if u.size == 0:
        return bm.array([])

    # The discrete Laplacian with periodic boundaries is implemented via circular shifts
    laplacian = bm.roll(u, 1) - 2 * u + bm.roll(u, -1)
    return u + alpha * laplacian


def step_buggy(u: TensorLike, alpha: float) -> TensorLike:
    """
    Performs one time step of the 1D heat equation with buggy zero boundary condition
    """
    n = u.size
    if n == 0:
        return bm.array([])

    u_new = bm.copy(u)

    # Interior points update
    if n > 2:
        u_left = bm.zeros_like(u_new)
        u_right = bm.zeros_like(u_new)
        u_left[1:]  = u[:-1]
        u_right[:-1] = u[1:]
        u_new += alpha * (u_right - 2 * u + u_left )

    elif n == 1:
        # Special case for N=1, both neighbors are 0
        laplacian_0 = 0 - 2 * u[0] + 0
        u_new[0] += alpha * laplacian_0

    return u_new

def solve_one_case(test_case: tuple, epsilon: float = 1e-10):
    n, alpha, t, seed, mode, include_zero = test_case
    step_func = step_correct if mode == 'correct' else step_buggy
    rng = bm.random.default_rng(seed)
    states = [rng.uniform(0, 1, size=n) for _ in range(t)]
    if include_zero:
        states.append(bm.zeros(n))

    con_v, sym_v, mon_v = 0, 0, 0
    for u_old in states:
        u_new = step_func(u_old, alpha)

        # 1. 质量守恒
        if bm.abs(bm.sum(u_old) - bm.sum(u_new)) > epsilon:
            con_v += 1

        # 2.空间反射下的对称等变性
        u_old_r = u_old[::-1]  # u_old 的翻转
        u_new_r = step_func(u_old_r, alpha)

        if bm.max(bm.abs(u_new_r - u_new[::-1])) > epsilon:
            sym_v += 1

        # 3.值域的单调性
        if u_old.size > 1:
            range_old = bm.max(u_old) - bm.min(u_old)
            range_new = bm.max(u_new) - bm.min(u_new)
            if range_new - range_old > epsilon:
                mon_v += 1
    total_test = len(states)

    return con_v / total_test, sym_v / total_test, mon_v / total_test


test_cases = [
        (64, 0.2, 100, 101, "correct", True),
        (64, 0.49, 200, 102, "correct", True),
        (64, 0.0, 200, 103, "correct", False),
        (64, 0.2, 200, 104, "buggy", True),
        (1, 0.2, 50, 105, "correct", True),
        (32, 0.2, 200, 106, "buggy", False),
        (32, 0.6, 200, 106, "buggy", False),]

for case in test_cases:
    case_result = solve_one_case(case)
    print(f"运行示例 {case} 违反3个属性测试的3个结果为: {case_result[0]:.1%}   {case_result[1]:.1%}   {case_result[2]:.1%}")

