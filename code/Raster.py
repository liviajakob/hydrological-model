# -*- coding: utf-8 -*-
"""

"""
import numpy as np

class Raster(object):
    
    '''A class to represent 2-D Rasters'''

    def __init__(self,data,xorg,yorg,cellsize,nodata=-999.999):
        """Constructor of a Raster, sets all the object variables
        
        Origin: xorg=0 and yorg=0 is left down corner of a cell
        
        Input Parameter:
            data
            xorg – An Integer describing x-origin
            yorg – An Integer describing y-origin
            cellsize – A Number describing cellsize (e.g. 1)
            nodata – No data representation
            
        """
        self._data=np.array(data)
        self._orgs=(xorg,yorg)
        self._cellsize=cellsize
        self._nodata=nodata
        
    def getData(self):
        return self._data
    
           
    def getShape(self):
        """return the shape of the data array"""
        return self._data.shape    
    
    def getRows(self):
        return self._data.shape[0]
        
    def getCols(self):
        return self._data.shape[1]
        
    def getOrgs(self):
        """Returns raster origin
        
        Returns:
            self._orgs – a tuple of (xorg, yorg)
        """
        return self._orgs
        
    def getCellsize(self):
        return self._cellsize
    
    def getNoData(self):
        return self._nodata
    

    def createWithIncreasedCellsize(self, factor):
        """returns a new Raster with cell size larger by a factor (which must be an integer)
        
        Input Parameter:
            factor – factor of increased cellsize
        Returns:
            resampled Raster, a Raster object
        """
        if factor== 1: #doesnt do anything
            return self
        else:
            return self.resample(factor)


    def resample(self, factor):
        """Resamples the raster
        
        Input Parameter:
            factor – factor of cellsize
        
        Returns:
            resampled Raster, a Raster object
        """
        nrows=self.getRows() // factor #floor division, calcucate new number of rows
        ncols=self.getCols() // factor #floor division, calcucate new number of cols
        newdata=np.zeros([nrows, ncols]) #create empty array
        
        for i in range(nrows): #iterate
            for j in range(ncols): #iterate
                sumCellValue=0.0 #set sum to zero at the start
                for k in range(factor): #smaller box iterates through values in a (new) cell
                    for l in range(factor):
                        #"i*factor + k" calculates y position of data in original raster
                        sumCellValue += self._data[i*factor + k, j*factor +l] #add new value to sum
                newdata[i,j]=sumCellValue / factor / factor + 100 #dividing by number of cells
        return Raster(newdata, self.getOrgs()[0],self.getOrgs()[1], self._cellsize*factor) #return new raster
    
    


    def __repr__(self):
        """String representation
        """
        return str(self.getData())