# -*- coding: utf-8 -*-
"""
Created on Mon Nov 05 00:46:36 2012

@author: nrjh
"""

import math

class Point2D(object):
    '''A class to represent 2-D points'''

    def __init__(self,x,y):
        """Constructor for Point2D
        
        Input Parameter:
            x – x-coordinate, an integer or float
            y – y–coordinate, an integer or float
        
        """

        self._x=x*1. #ensure points are always floats
        self._y=y*1.
        
       
    def clone(self):
        """returns a clone of self (another identical Point2D object) 
        """
        return Point2D(self._x,self._y)

 
    def get_x(self):
        """returns x coordinate"""
        return self._x
        
         
    def get_y(self):
        """returns y coordinate"""
        return self._y
        
    def get_coord(self,arg):
        """return x coord if arg=0, else y coord"""
        if arg==0:
            return self._x
        else:
            return self._y
        
      
    def get_xys(self):
        """returns x,y tupel"""
        return (self.x,self._y)        
    
    
    def move(self,x_move,y_move):
        """moves points by specified x-y vector"""
        self._x = self._x + x_move
        self._y = self._y + y_move
        
  
    def distance(self, other_point):
        """calculates and return distance"""
        xd=self._x-other_point._x
        yd=self._y-other_point._y
        return math.sqrt((xd*xd)+(yd*yd))
       
     
    def samePoint(self,point):
        if point==self:
             return True

    def sameCoords(self,point,absolute=True,tol=1e-12):
        if absolute:
            return (point.get_x()==self._x and point.get_y()==self._y)
        else:
            xequiv=math.abs((self.get_x()/point.get_x())-1.)<tol
            yequiv=math.abs((self.get_y()/point.get_y())-1.)<tol
            return xequiv and yequiv
            
    
#End of class Point 2D
#********************************************************


class PointField(object):
    '''A class to represent a field (collection) of points'''
    
    def __init__(self,PointsList=None):
        self._allPoints = []
        if isinstance(PointsList, list):
            self._allPoints = []
            for point in PointsList:
                if isinstance(point, Point2D):
                    self._allPoints.append(point.clone())
  
    def getPoints(self):
        return self._allPoints
        
    def size(self):
        return len(self._allPoints)
    
    def move(self,x_move,y_move):
        for p in self._allPoints:
            p.move(x_move,y_move)
    
    def append(self,p):
        self._allPoints.append(p.clone())

#method nearestPoint
    def nearestPoint(self,p,exclude=False):
        """A simple method to find the nearest Point to the passed Point2D
        object, p.  Exclude is a boolean we can use at some point to
        deal with what happens if p is in the point set of this object, i.e
        we can choose to ignore calculation of the nearest point if it is in 
        the same set"""
 
#check we're been passed a point   
        if isinstance(p,Point2D):
 
#set first point to be the initial nearest distance           
            nearest_p=self._allPoints[0]           
            nearest_d=p.distance(nearest_p)

# now itereate through all the other points in the PointField
# testing for each point, i.e start at index 1
            for testp in self._allPoints[1:]:

# calculate the distance to each point (as a test point)
                d=p.distance(testp)

# if the test point is closer than the existing closest, update
# the closest point and closest distance
                if d<nearest_d:
                    nearest_p=testp
                    nearest_d=d

# return the nearest point                    
            return nearest_p

#else not a Point passed, return nothing       
        else:
            return None
            
        

    def sortPoints(self):
           """ A method to sort points in x using raw position sort """
           self._allPoints.sort(pointSorterOnX)
        
        
   
class Point3D (Point2D):

    def __init__(self, x, y, z):
        print ('I am a Point3D object')
        Point2D.__init__(self, x, y)
        self._z = z
        print ('My z coordinate is ' + str(self._z))
        print ('My x coordinate is ' + str(self._x))
        print ('My x coordinate is ' + str(self._y))

    def clone(self):
        return Point3D(self._x, self._y, self._z)
        
    def get_z(self):
        return self._z
    
    def move(self, x_move, y_move, z_move):
        Point2D.move(self,x_move, y_move)
        self._z = self._z + z_move
    
    def distance(self, other_point):
        zd=self._z-other_point.get_z()
#        xd=self._x-other_point.get_x()
#        yd=self._y-other_point.get_y()
        d2=Point2D.distance(self,other_point)
        d3=math.sqrt((d2*d2)+(zd*zd))
        return d3
        

    
def pointSorterOnX(p1,p2):
    x1=p1.get_x()
    x2=p2.get_x()
    if (x1<x2): return -1
    elif (x1==x2): return 0
    else: return 1

def pointSorterOnY(p1,p2):
    y1=p1.get_y()
    y2=p2.get_y()
    if (y1<y2): return -1
    elif (y1==y2): return 0
    else: return 1

        
