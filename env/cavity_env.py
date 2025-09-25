import numpy as np
import mph
import os
import utils

class CavityQfactor():
    def __init__(self):
        super(CavityQfactor,self).__init__()
        self.a = 300e-9  # PcSel晶格常数
        self.r = 0.3*self.a
        self.tk = 100e-9
        self._kx = 0
        self._ky = 0
        self.center_freq = 0.45
        self.band_num:int = 4
        self.export_common_args = ('ewfd.Qfactor','ewfd.freq',)
        self.export_field_args = ('x','y','z','ewfd.Hz',)

        # Initialize the simulator environment
        if not os.path.isfile('./model/ComsolModel.mph'):
            utils.logging_warning("The available comsol model is not found, we will re-establish")
            self.create_new_model()
            utils.logging_warning("Re-establish completed!")
        client = mph.start()
        utils.logging_info("Load the comsol model")
        self.pymodel = client.load('./model/ComsolModel.mph')
        utils.logging_info("Load completed!")

    def get_result(self):
        model = self.pymodel.java
        model.param().set("kx",str(self._kx*2*np.pi/self.a))
        model.param().set("ky",str(self._ky*2*np.pi/self.a))
        model.study("std1").feature("eig").set("neigsactive",True)
        model.study("std1").feature("eig").set("neigs",str(self.band_num))
        model.study("std1").feature("eig").set("shift","c_const/a*"+str(self.center_freq))
        model.study('std1').run()
        export_data = dict()
        res_total = self.pymodel.evaluate(self.export_common_args,dataset=self.pymodel.datasets()[0])
        export_data['common'] = self.export(self.export_common_args,res_total)
        res_total = self.pymodel.evaluate(self.export_field_args,dataset=self.pymodel.datasets()[0])
        export_data['field'] = self.export(self.export_field_args,res_total)
        return export_data

    def export(self,export_args,res_total):
        export_data = dict()
        export_data['kx'],export_data['ky'] = self._kx,self._ky
        res_total = np.array(res_total)
        if res_total.ndim == 1:
            res_total = np.stack([res_total],0)
        elif res_total.ndim == 2:
            res_total = np.transpose(res_total)
        for export_arg,res in zip(export_args,res_total):
            if np.any(np.iscomplex(res)):
                export_data[export_arg+'_real'],export_data[export_arg+'_imag']=np.real(res).tolist(),np.imag(res).tolist()
            else:
                export_data[export_arg] = np.real(res).tolist()
        return export_data

    def render(self, mode=None):
        if mode is not None:
            utils.logging_warning("We don't have a render!")

    def create_new_model(self):
        client = mph.start()
        pymodel = client.create('Model')
        model = pymodel.java

        model.component().create("comp1")
        model.component("comp1").geom().create("geom1",3)
        model.component("comp1").mesh().create("mesh1")
        model.component("comp1").physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1")

        model.study().create("std1")
        model.study("std1").create("eig", "Eigenfrequency")
        model.study("std1").feature("eig").set("conrad", "1")
        model.study("std1").feature("eig").set("solnum", "auto")
        model.study("std1").feature("eig").set("notsolnum", "auto")
        model.study("std1").feature("eig").set("errorexpr", "1")
        model.study("std1").feature("eig").setSolveFor("/physics/ewfd",True)

        model.param().set("a", float(self.a))
        model.param().set("r", float(self.r))
        model.param().set("tk", float(self.tk))
        model.param().set("kx", float(self._kx))
        model.param().set("ky", float(self._ky))
        model.param().set("n_air", "1")
        model.param().set("n_medium", "3.5")

        model.component("comp1").geom("geom1").create("blk1", "Block")
        model.component("comp1").geom("geom1").feature("blk1").set("size",["a","a","tk/2"]) # PC层-介质
        model.component("comp1").geom("geom1").create("cyl1", "Cylinder")
        model.component("comp1").geom("geom1").feature("cyl1").set("r","r")
        model.component("comp1").geom("geom1").feature("cyl1").set("h","tk/2") # PC层-孔洞
        model.component("comp1").geom("geom1").feature("cyl1").set("pos",["a/2","a/2",'0'])
        model.component("comp1").geom("geom1").create("blk2", "Block")
        model.component("comp1").geom("geom1").feature("blk2").set("size",["a","a","a"]) # 空气层
        model.component("comp1").geom("geom1").feature("blk2").set("pos",["0","0","tk/2"])
        model.component("comp1").geom("geom1").create("blk3", "Block")
        model.component("comp1").geom("geom1").feature("blk3").set("size",["a","a","a"]) # PML层
        model.component("comp1").geom("geom1").feature("blk3").set("pos",["0","0","tk/2+a"])
        model.component("comp1").geom("geom1").run()

        model.component("comp1").coordSystem().create("pml1","PML")
        model.component("comp1").coordSystem("pml1").selection().set(3)
        model.component("comp1").physics("ewfd").create("pc1","PeriodicCondition",2)
        model.component("comp1").physics("ewfd").feature("pc1").set("PeriodicType","Floquet")
        model.component("comp1").physics("ewfd").feature("pc1").set("kFloquet",["kx","ky","0"])
        model.component("comp1").physics("ewfd").feature().duplicate("pc2","pc1")
        model.component("comp1").physics("ewfd").create("pmc1","PerfectMagneticConductor",2)
        model.component("comp1").physics("ewfd").feature("pc1").selection().set(2,5,8,11,12,13)
        model.component("comp1").physics("ewfd").feature("pc2").selection().set(1,4,7,20,21,22)
        model.component("comp1").physics("ewfd").feature("pmc1").selection().set(3,10,16)

        model.component("comp1").material().create("mat1", "Common")
        model.component("comp1").material("mat1").label("air")
        model.component("comp1").material("mat1").propertyGroup().create("RefractiveIndex", "Refractive_index")
        model.component("comp1").material("mat1").propertyGroup("RefractiveIndex").set("n",["n_air"])
        model.component("comp1").material().create("mat2","Common")
        model.component("comp1").material("mat2").label("medium")
        model.component("comp1").material("mat2").propertyGroup().create("RefractiveIndex", "Refractive_index")
        model.component("comp1").material("mat2").propertyGroup("RefractiveIndex").set("n",["n_medium"])
        model.component("comp1").material("mat2").selection().set(1)
        model.component("comp1").material("mat1").selection().set(2,3,4)

        model.component("comp1").physics("ewfd").prop("MeshControl").set("SizeControlParameter", "UserDefined");
        model.component("comp1").physics("ewfd").prop("MeshControl").set("PhysicsControlledMeshMaximumElementSize", "a/4") # 设置最大网格大小

        pymodel.save('./model/ComsolModel.mph')
        client.remove(pymodel)

