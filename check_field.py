import utils
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

mask = utils.load_data('./data/mask/mask.json')
k_lp = 0 # k点id 0-121 (Gamma-X-M-Gamma)
field = utils.load_data(f'./data/field/{k_lp}.json')
mask_mode = mask[k_lp*20:(k_lp+1)*20]

x,y,z,Hz_real,Hz_imag = field['x'],field['y'],field['z'],field['ewfd.Hz_real'],field['ewfd.Hz_imag']
x,y,z,Hz = np.array(x),np.array(y),np.array(z),np.array(Hz_real)**2+np.array(Hz_imag)**2

mode = 1 # 模式id 0-4
x,y,z,Hz = x[mask_mode][mode],y[mask_mode][mode],z[mask_mode][mode],Hz[mask_mode][mode]

X,Y,Z,F = utils.to_mesh(x,y,z,Hz,[51,51,11])
F = utils.norm(F) # 归一化

# 取一个切面，比如 z=0 平面
X_slice = F[:,25,:]
Y_slice = F[25,:,:]
Z_slice = F[:,:,0]

# 绘制 3D 切面图
fig = plt.figure(figsize=(8,6))
ax3d = fig.add_subplot(111, projection='3d')

# 用 plot_surface 画切面
ax3d.plot_surface(np.full_like(X[:,25,:],np.max(X)/2),Y[:,25,:],Z[:,25,:],facecolors=plt.cm.RdBu_r(X_slice),alpha=0.8)
ax3d.plot_surface(X[25,:,:],np.full_like(Y[25,:,:],np.max(Y)/2),Z[25,:,:],facecolors=plt.cm.RdBu_r(Y_slice),alpha=0.8)
ax3d.plot_surface(X[:,:,0],Y[:,:,0],np.full_like(Z[:,:,0],0),facecolors=plt.cm.RdBu_r(Z_slice),alpha=0.8)

norm = colors.Normalize(vmin=np.min([X_slice.min(),Y_slice.min(),Z_slice.min()]), vmax=np.max([X_slice.max(),Y_slice.max(),Z_slice.max()]))
cmap = plt.cm.RdBu_r
sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([]) # 关键：不需要数组
fig.colorbar(sm, ax=ax3d, orientation='vertical', shrink=0.6, label='normHz')

ax3d.set_xlabel("X")
ax3d.set_ylabel("Y")
ax3d.set_zlabel("Z")
plt.show()
