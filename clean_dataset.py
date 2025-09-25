import numpy as np
import matplotlib.pyplot as plt
import utils

utils.set_style()
a = 295e-9 # 晶格常数
band_num = 20
k_num = 121

num,kx,ky,freq,Qfactor = np.array([]),np.array([]),np.array([]),np.array([]),np.array([])
for lp in range(0,k_num):
    data_common = utils.load_data(f'./data/common/{lp}.json')
    num = np.append(num,int(lp)*np.ones(band_num))
    kx = np.append(kx,np.array(data_common['kx'])*np.ones(band_num))
    ky = np.append(ky,np.array(data_common['ky'])*np.ones(band_num))
    freq = np.append(freq,np.array(data_common['ewfd.freq'][0:band_num])/(3e8/a))
    Qfactor = np.append(Qfactor,np.array(data_common['ewfd.Qfactor'][0:band_num]))

space,_ = utils.space_rg_GXMG(num=k_num)
light_cone = np.sqrt(space['kx']**2+space['ky']**2)

plt.figure(figsize=[3.6,3.1])
plt.plot(light_cone,linewidth=1,linestyle='--',color='k')
plt.scatter(num,freq,s=2,c=np.log10(Qfactor),cmap='RdBu_r')
plt.xlabel("Γ-X-M-Γ")
plt.ylabel("Frequency (c/a)")
plt.show()

light_cone_reshape = (np.ones([band_num,1])*light_cone).transpose(1,0).ravel()

## 筛选-需手动调整参数
mask = ~((freq<4e-4)*(light_cone_reshape>0.0001))
mask_hold = mask # 记录未筛选前数据
mask = mask*~((Qfactor<18)*(freq>light_cone_reshape)) #光锥线以上
mask = mask*~((Qfactor<50)*(freq>light_cone_reshape)*(freq<light_cone_reshape+0.02)*(freq>0.1)) #光锥线附近

# mask = mask*~((freq>0.439375)*(freq<0.4394)) # 手动筛选

# mask += mask_hold*((freq>0.41215)*(freq<0.41220)) # 手动添加
mask += mask_hold*((freq>4.27e-8)*(freq<4.274e-8)) # 手动添加
mask += mask_hold*((freq>0.4116)*(freq<0.4117)) # 手动添加

for lp in range(k_num):
    args = np.sort(freq[mask*(num==lp)])[5:] #取5条带
    for f in args:
        mask[freq==f] = 0

num,kx,ky,freq,Qfactor = num[mask],kx[mask],ky[mask],freq[mask],Qfactor[mask]
plt.figure(figsize=[3.6,3.1])
plt.plot(light_cone,linewidth=1,linestyle='--',color='k')
plt.scatter(num,freq,s=2,c=np.log10(Qfactor),cmap='jet')
plt.xlabel("Γ-X-M-Γ")
plt.ylabel("Frequency (c/a)")
plt.show()

utils.save_data(mask.tolist(),'./data/mask/','mask.json')
