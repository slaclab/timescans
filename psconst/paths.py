from psana import *
from PSCalib.CalibFileFinder import CalibFileFinder

class CalibrationPaths:
    def __init__(self,env,src,calibdir=''):
        self.env = env
        self.calibgroup = 'TimeTool::CalibV1'
        self.src  = src
        if len(calibdir)==0:
            self.cdir = self.env.calibDir()
        else:
            self.cdir = calibdir

    def findCalFileName(self,type,rnum):
        """
        Returns calibration file name, given run number and type
        """              
        cff = CalibFileFinder(self.cdir, self.calibgroup, pbits=0)
        fname = cff.findCalibFile(self.src, type, rnum)
        return fname

    def newCalFileName(self,type,runBegin,runEnd='end'):
        """
        Returns calibration file name, given run number and type (e.g. "pedestals")
        """
        
        path=os.path.join(self.cdir)
        if not os.path.exists(path): 
            os.mkdir(path)
        path=os.path.join(self.cdir,self.calibgroup)
        if not os.path.exists(path): 
            os.mkdir(path)
        path=os.path.join(self.cdir,self.calibgroup,self.src)
        if not os.path.exists(path): 
            os.mkdir(path)
        path=os.path.join(self.cdir,self.calibgroup,self.src,type)
        if not os.path.exists(path): 
            os.mkdir(path)
        return path+'/'+str(runBegin)+'-'+str(runEnd)+'.data'