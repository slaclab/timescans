
import os
import h5py
import numpy


# new functions from TJ for happier, simplier times
def calib_path(env, detector_type, detector_src, start, end='end', create_dir=True):
    fn = "%s-%s.h5" % (start, end)
    base = os.path.join(env.calibDir(), detector_type, detector_src)
    if create_dir and not os.path.exists(base):
        os.system('mkdir -p %s' % base)
    return os.path.join(base, fn)


def find_calib_file(env, detector_type, detector_src, run):
    """
    logic: choose calib with starting range closest to desired run, being
           sure the range for that calib includes this run
    """

    basepath = os.path.join(env.calibDir(), detector_type, detector_src)

    nearest = '0-end.data'
    s_and_e = lambda s : s.split('.')[0].split('-')

    for fn in os.listdir(basepath):
        start, end = s_and_e(fn)
        start = int(start)
        end = 999999 if (end == 'end') else int(end)
        if (start <= run) and (run <= end):
            if start > int(s_and_e(nearest)[0]):
                nearest = fn
        else:
            raise IOError('No valid calib file found for run: %d' % run)

    return os.path.join(basepath, nearest)


class ConstantsStore(object):
    def __init__(self,obj,file):
        self.f = h5py.File(file,'w')
        self.cwd = ''
        for k in obj.keys():
            subobj = obj[k]
            self.dispatch(subobj,str(k))
        self.f.close()
    def pushdir(self,dir):
        '''move down a level and keep track of what hdf directory level we are in'''    
        
        self.cwd += '/'+dir
       
    def popdir(self):
        '''move up a level and keep track of what hdf directory level we are in'''
        self.cwd = self.cwd[:self.cwd.rfind('/')]
    def typeok(self,obj,name):
        '''check if we support serializing this type to hdf'''
        allowed = [dict,int,float,str,numpy.ndarray]
        return type(obj) in allowed
    def storevalue(self,v,name):
        '''persist one of the supported types to the hdf file'''
        self.f[self.cwd+'/'+name] = v
    def dict(self,d,name):
        '''called for every dictionary level to create a new hdf group name.
        it then looks into the dictionary to see if other groups need to
        be created'''
        if self.cwd is '':
            self.f.create_group(name)
        self.pushdir(name)
        for k in d.keys():
            self.dispatch(d[k],str(k))
        self.popdir()
    def dispatch(self,obj,name):
        '''either persist a supported object, or look into a dictionary
        to see what objects need to be persisted'''
        if type(obj) is dict:
            self.dict(obj,name)
        else:
            if self.typeok(obj,name):
                self.storevalue(obj,name)
            else:
                print('Constants.py: variable "'+name+'" of type "'+type(obj).__name__+'" not supported')

class ConstantsLoad(object):
    def __init__(self,file):
        self.obj = {}
        self.f = h5py.File(file,'r')
        self.f.visititems(self.loadCallBack)
        self.f.close()
    def setval(self,name,obj):
        '''see if this hdfname has a / in it.  if so, create the dictionary
        object.  if not, set our attribute value.  call ourselves
        recursively to see if other dictionary levels exist.'''
        if '/' in name:
            dictname=name[:name.find('/')]
            remainder=name[name.find('/')+1:]

            if not dictname in obj:
                obj[dictname]={}
               
            self.setval(remainder,obj[dictname])
        else:
            obj[name]=self.f[self.fullname].value

    def loadCallBack(self,name,obj):
        '''called back by h5py routine visititems for each
        item (group/dataset) in the h5 file'''
        if isinstance(obj,h5py._hl.group.Group):
            return
        self.fullname = name
        self.setval(name,self.obj)

def load(file):
    '''takes a string filename, and returns a constants object.'''
    c = ConstantsLoad(file)
    return c.obj

def save(file,obj):
    '''store a constants object in an hdf5 file.  the object
    can be a hierarchy (defined by python dictionaries) and
    hdf5 supported types (int, float, numpy.ndarray, string).
    the hierarchy can be created by having one value of
    a dictionary itself be a dictionary.'''
    
    c = ConstantsStore(obj,file)


if __name__ == '__main__': 
    from psana import *
    import psconst

    detector_type = 'timetool'
    detector_src = 'cxitt_1'

    ds = DataSource('exp=cxij8816:run=3')
    fout = psconst.calib_path(ds.env(), detector_type, detector_src, 20, end='end')

    subdict={'hello2':3,'junk2':'apple'}
    writedict={'hello':1,'junk':'banana','dict2':subdict}
    psconst.save(fout, writedict)

    fin = psconst.find_calib_file(ds.env(), detector_type, detector_src, 30)
    readdict = psconst.load(fin)
    print 'write:', writedict, '-->', fout
    print 'read:', fin, '-->', readdict
