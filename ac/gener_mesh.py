import matplotlib.pyplot as plt
from fealpy.mesher import ExpansionChamberMesher

# L_in, L_e, L_out = 0.05, 0.2, 0.05
# r_in, r_e, r_out = 0.025, 0.1, 0.05
L_in = 0.05        # 入口管长度 m
L_e = 0.2          # 扩张腔长度 m
L_out = 0.05       # 出口管长度 m
L_total = L_in + L_e + L_out

D_in = 0.025       # 入口管直径 m
D_e = 0.1          # 扩张腔直径 m
D_out = 0.025       # 出口管直径 m

r = max(D_in, D_e, D_out)

mesh_ = ExpansionChamberMesher()
mesh = mesh_.init_mesh(nx=20,ny=10)
fig = plt.figure()
axes = fig.gca()
mesh.add_plot(axes)
mesh.find_node(axes, showindex=False)
mesh.find_cell(axes, showindex=False)
plt.show()