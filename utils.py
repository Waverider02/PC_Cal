import json
import matplotlib.pyplot as plt
import numpy as np
import logging
import os

# 设置绘图样式
def set_style(fontfamily="Arial",titlesize=10,labelsize=10,ticksize=10,legendsize=10,linewidth=1.5,markersize=4,autolayout=True):
    plt.rcParams["axes.unicode_minus"] = False #解决负号显示为方块的问题
    plt.rcParams["font.sans-serif"] = fontfamily #设置字体
    # plt.rcParams["lines.linestyle"]  #线条样式
    plt.rcParams["lines.linewidth"] = linewidth
    plt.rcParams["lines.markersize"] = markersize #图形标记大小
    plt.rcParams["lines.markeredgewidth"] = 0.5 #标记附近线宽
    plt.rcParams["xtick.labelsize"] = ticksize #横轴字体大小
    plt.rcParams["ytick.labelsize"] = ticksize #纵轴字体大小
    plt.rcParams['legend.fontsize'] = legendsize #图例字体大小
    # plt.rcParams["xtick.major.size"] #x轴最大刻度
    # plt.rcParams["ytick.major.size"] #y轴最大刻度
    plt.rcParams["axes.titlesize"] = titlesize #子图的标题大小
    plt.rcParams["axes.labelsize"] = labelsize #子图的标签大小
    plt.rcParams["figure.dpi"] = 300 #图像分辨率
    # plt.rcParams["figure.figsize"] #图像显示大小
    plt.rcParams["savefig.dpi"] = 600 #图片像素
    plt.rcParams["mathtext.fontset"] = "custom"
    plt.rcParams["mathtext.rm"] = fontfamily  # 用于正常数学文本
    plt.rcParams["mathtext.it"] = fontfamily+":italic"  # 用于斜体数学文本
    plt.rcParams['svg.fonttype'] = 'none' # 导出svg可用AI编辑
    plt.rcParams['svg.hashsalt'] = 'hello' # svg编码种子
    plt.rcParams['figure.autolayout'] = autolayout # 自动调整图像间距

# 配置日志
def logging_config():
    logging.basicConfig(
        level=logging.INFO, #level over INFO
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="./log/LOGGING.log",
        encoding="utf-8"
    )

# info
def logging_info(_string):
    logging.info(_string)

# warning
def logging_warning(_string):
    logging.warning(_string)

# 将数据结构保存到文件
def save_data(data,file_path,file_name):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path+file_name,'w') as file:
        json.dump(data, file)

# 从文件中加载数据结构
def load_data(file_name):
    with open(file_name,'r') as file:
        data = json.load(file)
    return data

# 生成遍历路径 all
def space_rg_all(la=300e-9,num=11):
    kx_rg = np.linspace(0,0.5,num) #[2*pi/a]
    ky_rg = np.linspace(0,0.5,num) #[2*pi/a]
    _len_max = len(kx_rg)*len(ky_rg)
    _space = dict()
    _space['a'] = la
    _space['kx'] = np.zeros(_len_max)
    _space['ky'] = np.zeros(_len_max)
    for lp1 in range(0,len(kx_rg)):
        for lp2 in range(0,len(ky_rg)):
            lp_all = len(ky_rg)*lp1+lp2
            _space['kx'][lp_all],_space['ky'][lp_all] = kx_rg[lp1],ky_rg[lp2]
    return _space,_len_max

# 生成遍历路径 GXMG
def space_rg_GXMG(la=300e-9,num=121):
    lp_rg = np.linspace(0,3,num)
    _len_max = num
    _space = dict()
    _space['a'] = la
    _space['kx'] = np.zeros(_len_max)
    _space['ky'] = np.zeros(_len_max)
    for _lp in range(0, _len_max):
        lp_k = lp_rg[_lp]
        if lp_k<1:
            _space['kx'][_lp],_space['ky'][_lp] = lp_k*0.5,0
        elif lp_k<2:
            _space['kx'][_lp],_space['ky'][_lp] = 0.5,(lp_k-1)*0.5
        elif lp_k<3:
            _space['kx'][_lp],_space['ky'][_lp] = (3-lp_k)*0.5,(3-lp_k)*0.5
    return _space,_len_max

def to_mesh(x0,y0,z0,val0,num=[11,11,11]):
    x0,y0,z0,val0 = np.array(x0).ravel(),np.array(y0).ravel(),np.array(z0).ravel(),np.array(val0).ravel()
    x = np.linspace(np.min(x0),np.max(x0),num[0])
    y = np.linspace(np.min(y0),np.max(y0),num[1])
    z = np.linspace(np.min(z0),np.max(z0),num[2])
    x,y,z = np.meshgrid(x,y,z)
    val = np.zeros(np.shape(z))
    for lpx in range(num[0]):
        for lpy in range(num[1]):
            for lpz in range(num[2]):
                dis = (x0-x[lpy,lpx,lpz])**2+(y0-y[lpy,lpx,lpz])**2+(z0-z[lpy,lpx,lpz])**2
                idx1,idx2 = np.argpartition(dis, 1)[:2]  # 最小两个值的索引
                dis1,dis2 = dis[idx1],dis[idx2]
                val1,val2 = val0[idx1],val0[idx2]
                val[lpy,lpx,lpz]= (dis1*val2+dis2*val1)/(dis1+dis2) # 插值
    return x,y,z,val

def norm(array):
    return (array-np.min(array))/(np.max(array)-np.min(array))