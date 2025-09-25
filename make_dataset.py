from multiprocessing import Pool
import env.cavity_env as cavity_env
import utils
import time

if __name__ != '__main__': # 子进程
    utils.logging_config() # 日志配置
    ComsolModel = cavity_env.CavityQfactor() # 仿真环境
    ComsolModel.band_num = 20 # 需要导出的能带数目
    ComsolModel.center_freq = 0.2 # 能带中心处频率
    ComsolModel.r = 0.3*295e-9  # 圆孔半径
    ComsolModel.tk = 100e-9 # PC厚度
    ComsolModel.export_common_args = ('ewfd.freq','ewfd.Qfactor') # 导出常规数据
    ComsolModel.export_field_args = ('x','y','z','ewfd.Hz') # 导出场数据(TE极化,若拓展TM极化,需要调整仿真模型配置)

def task(*para,**kwargs): # 并行计算任务
    ComsolModel.a,ComsolModel._kx,ComsolModel._ky = para
    jsdata = ComsolModel.get_result()
    utils.save_data(jsdata['common'],'./data/common/',f'{kwargs.get('lp')}.json')
    utils.save_data(jsdata['field'],'./data/field/',f'{kwargs.get('lp')}.json')
    utils.logging_info("Subprocess completed")

if __name__ == '__main__':
    utils.logging_config()
    processor_num = 12 # 设置进程数目,需要考虑内存大小
    ComsolModel = cavity_env.CavityQfactor()

    ### 参数空间 ### 3维
    a = 295e-9 # 晶格常数
    space,len_max = utils.space_rg_GXMG(a,121) # 获取参数空间
    utils.logging_info("Start")
    pl = Pool(processes=processor_num) # 进程池配置
    for lp in range(0,len_max): # 异步进程池
        pl.apply_async(func=task,args=(space['a'],space['kx'][lp],space['ky'][lp]),kwds={'lp':lp})
    pl.close()
    pl.join()
    time.sleep(1)
    utils.logging_info("Calculation completed")
