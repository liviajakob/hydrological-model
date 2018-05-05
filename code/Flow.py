import numpy as np

from Points import Point2D
from Raster import Raster

class FlowNode(Point2D):
    """Class representing nodes (points) in a Flow Raster
    
    Inherits from Point2D class
    
    """
    
    def __init__(self,x,y, value, rainfall=None):
        """Constructor for FlowNode
        
        Input Parameter:
            x – x-position of node within grid
            y – y-position of node within grid
            value – value at the node position (e.g. elevation)
        
        """
        Point2D.__init__(self,x,y) #use constructor of super class
        self._downnode=None #is set with setDownnode()
        self._upnodes=[]
        self._pitflag=True #set to true as FlowNode doesn't have a downnode at the moment
        self._value=value
        self._rainfall=rainfall
        self._lakedepth=0
        
    def setDownnode(self, newDownNode):
        """Sets the downnode of a FlowNode object, sets itself as an upnode 
        Can also be used to change a previous downnode to a new downnode as it removes itself as an upnode
        
        Input Parameter:
            newDownNode – a FlowNode object representing the downnode
            
        """
        self._pitflag=(newDownNode==None) #sets pitflag to True if downnode exists, else to false
        
        if (self._downnode!=None): # change previous
            self._downnode._removeUpnode(self) #remove itself as upnode (from thre downnode)
            
        if (newDownNode!=None): # insert itself as new upnode
            newDownNode._addUpnode(self)
            
        self._downnode=newDownNode # set downnode
        
        
    def getDownnode(self):
        """
        Returns:
           self._downnode – a FlowNode class object 
        """
        return self._downnode 
    
    
    def setRainfall(self, rainfall):
        """Setter for self._rainfall, sets the rainfall at the node
        
        Input Parameter:
            rainfall – rain at FlowNode object in mm
        """
        self._rainfall = rainfall
        
        
    def getRainfall(self):
        """Getter for self._rainfall
        
        Returns:
            self._rainfall – rain at FlowNode object in mm
        """
        return self._rainfall
    
        
    def getUpnodes(self):
        """Getter for self._upnodes
        Returns:
           self._upnodes – a list of FlowNode class objects
        """
        return self._upnodes
    
    
    def _removeUpnode(self, nodeToRemove):
        """Removes an upnode
        
        Input Parameter:
            nodeToRemove – a FlowNode object
        """
        self._upnodes.remove(nodeToRemove)
    
    
    def _addUpnode(self, nodeToAdd):
        """Adds an upnode
        
        Input Parameter:
            nodeToAdd – a FlowNode object
        """
        self._upnodes.append(nodeToAdd)


    def numUpnodes(self):
        """
        Returns:
           number of Upnodes
        """
        return len(self._upnodes)
    
    
    def getPitFlag(self):
        """Getter for self._pitflag
        Returns:
           self._pitflag – True or False: 
                           True when it is a pitFlag(=no downnodes)
                           False when it is not (=has downnodes)
        """
        return self._pitflag
    
    
    def setLakeDepth(self, depth):
        """Sets the depth of a lake
        
        Input Parameter:
            depth – lake depth in meter, should be 0 when it is not a lake
        """
        self._lakedepth += depth
    
    
    def getLakeDepth(self):
        """Getter for depth of lake
        Returns:
            self._lakedepth – number, zero when node is not a pitfall
        """
        return self._lakedepth
    
    
    
    def getFlow(self, constRain=None):
        """recursively adds the flow of all upnodes and its upnodes etc.
        If constant rain input parameter is null, flow is calculated from 
        recorded rainfall per node using self._rainfall
        If both, constant and self._rainfall are None, it calculates with 0mm rain
        
        Input Parameter:
            constRain – constant rain per node in mm, if left out the rainfall per node value is used
        """
        flow=0 #set to zero
        if constRain is not None:
            flow=constRain #initial flow is set to constant rain
        elif self.getRainfall() is not None: #if no constant rain is given it checks if a rainfall at this node is recorded
            flow=self.getRainfall() #initial flow is set to rainfall on cell
        
        for upnode in self.getUpnodes(): #iterare through upnotes
            flow+=upnode.getFlow(constRain) #add up flow by calling the function recursively with next upnode
        
        return flow #return result
        
    
    def getElevation(self):
        """Getter for Elevation
        
        Returns:
            self._value – a number representing elevation in m at the FlowNode
        """
        return self._value
    
    
    def fill(self, elevation):
        """Fills the node with water up to a new elevation. Calculates the depth.
        
        Input Parameter:
            elevation – new elevation
        
        """
        assert elevation >= self.getElevation()
        self.setLakeDepth(elevation - self.getElevation()) #set new lake depth
        self._value = elevation
    
  
    def __str__(self):
        """String representation of FlowNode object
        
        """
        downnode= -999
        if self.getDownnode() is not None:
            downnode =self.getDownnode().getElevation()
        return "Flownode y={}, x={}, elevation={} downnode={}".format(self.get_y(), self.get_x(), self.getElevation(), downnode)
    
    
    def __repr__(self):
        """Representation of FlowNode object
        
        """
        return self.__str__()
    







class FlowRaster(Raster):
    """A class containing a Raster with FlowNodes
    
    Inherits from Raster
    """

    def __init__(self,araster):
        """Constructor for FlowRaster
        
        Input Parameter:
            araster – a Raster class object
        
        """
        #create a new raster out of araster without data
        super().__init__(None,araster.getOrgs()[0],araster.getOrgs()[1],araster.getCellsize())#call init of raster class
        data = araster.getData() #get elevation of input raster
        nodes=[]
        #insert data
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                y=(i)*self.getCellsize()+self.getOrgs()[0] #x-position of node within grid
                x=(j)*self.getCellsize()+self.getOrgs()[1] #y-position of node within grid
                nodes.append(FlowNode(x,y, data[i,j]))#add node
            
        nodearray=np.array(nodes) #convert list to array
        nodearray.shape=data.shape #reshape 1d array to shape of the raster
        self._data = nodearray

        self.__neighbourIterator=np.array([1,-1,1,0,1,1,0,-1,0,1,-1,-1,-1,0,-1,1] ) #neighbours
        self.__neighbourIterator.shape=(8,2)        
        self.setDownnodes() #calculate downnodes
        self._lakes=[]
      
        
    def getPitflags(self):
        """Returns a list of pitflag nodes
        Pitflags are nodes without a downnode
        
        Returns:
            pitflags – a list of pitflag nodes
        """
        pitflags=[]
        for i in range(self._data.shape[0]):
            for j in range(self._data.shape[1]):
                if self._data[i,j].getPitFlag():
                    pitflags.append(self._data[i,j])
        return pitflags
    

    def calculateLakes(self):
        """Calculates lakes and creates Lake class objects
        
        Calculates lakes from pitflags, calculates depth for each lake node, 
        Readjusts elevation of lake nodes to lake surface (i.e. fills lakes) 
        and resets downnodes between the lake nodes using a gravity algorithm 
        towards the lake outflow
        
        The lakes are stored in self._lakes, a list with Lake objects
        
        """        
        for pitflag in self.getPitflags(): #iterate through pitflags
            i,j = int(pitflag.get_y()/self.getCellsize()), int(pitflag.get_x()/self.getCellsize())
            edgecase = i==0 or j==0 or i==(self._data.shape[0]-1) or j==(self._data.shape[1]-1)
            #check again if pitflag because it might have changed when two lakes grow together
            if pitflag.getPitFlag() and not(edgecase):
                self._lakes.append(self.createLake(i,j)) #create a lake object
        
        for lake in self._lakes:
            self.setLakeDownnodes(lake) #set new downnodes
            assert not(lake._outflow.getPitFlag())
            assert not(lake._nodes[-2].getPitFlag())
            
                        
            
    
    
    def createLake(self, i,j):
        """Creates a lake at position i,j
        Calculates its size and nodes, calculates depths for each lake node and
        readjusts elevation of lake nodes to lake surface
        
        Input Parameter:
            i – x position (int)
            j – y position (int)
            
        Returns:
            lake – a Lake class object
        """
        assert self._data[i,j].getPitFlag() ##assert that it's a pitflag
        lake=Lake(self._data[i,j]) #create new Lake object
        lake.addNeighbours(self.getNeighbours(i,j)) #add initial lake neighbours
        
        while(lake._outflow is None): #while lake has no outflow
            lowest=lake.lowestNeighbour()
            r,c=int(lowest.get_y()/self.getCellsize()), int(lowest.get_x()/self.getCellsize()) #row and col
            lake.addNode(lowest) #adds a new node to the lake, this also removes the node from neighbours
            lake.addNeighbours(self.getNeighbours(r,c)) #add new neighbours
            
            edgecase = r==0 or c==0 or r==(self._data.shape[0]-1) or c==(self._data.shape[1]-1)
            
            if lowest.getPitFlag() and edgecase: #yeah we arrived at an edge pitfall, no more searching is needed 
                lake.finalise() # finalise the lake
        return lake
    
    
    
    
    def setLakeDownnodes(self, lake):
        """Recalculates the downnodes for each lake node using a gravitation algorithm 
        towards the outflow. Recalculates the outflow downnode.
        
        Input Parameter:
            lake – a Lake object
        """
        checked=[] #stores checked nodes
        checknode=lake._outflow #stores the current node to be checked
        tocheck=[lake._outflow] #stores the future nodes to be checked

        while (len(tocheck)+len(checked))<(len(lake._nodes)): #while not every downnode is reset

            r,c=int(checknode.get_y()/self.getCellsize()), int(checknode.get_x()/self.getCellsize())
            neighbours = self.getNeighbours(r,c) #get new neighbours of checknode

            for n in neighbours:
                if lake.isLake(n) and n not in tocheck and n not in checked: #if downnode is not set yet
                    n.setDownnode(checknode) #set a downnode from neighbour to checknode
                    tocheck.append(n) #append the new neigbours
            
            tocheck.remove(checknode) #remove the checknode
            checked.append(checknode) #append the checked to checked

            nearest=self.getNearest(lake._outflow, tocheck) #nearest from outflow
            checknode=nearest
        
        #set lake downnode of outflow
        x=int(lake._outflow.get_x()/self.getCellsize())
        y=int(lake._outflow.get_y()/self.getCellsize())
        lake._outflow.setDownnode(self.lowestNeighbour(y,x)) #set outflows downnodes
     
    
    
    
    def getNearest(self, node, nodelist):
        """Returns nearest point from nodelist to node
        
        Input Parameter:
            node – origin node, a Flow node object
            nodelist – list with FlowNode object
        
        Returns:
            pNearest – the nearest point to a node, a FlowNode object
        """
        dNearest=None
        pNearest=None
        for n in nodelist:
            d = node.distance(n)
            if dNearest is None or d<dNearest:
                dNearest=d
                pNearest=n
        return pNearest
        
        


              
    def getNeighbours(self, r, c):
        """ Returns the eight neighbours of a cell
        
        Input Parameter:
            r – x-coordinate of the cell
            c – y-coordinate of the cell
        
        Returns:
            neighbours – a list of 8 neighbour FlowNode objects
        
        """  
        neighbours=[]
        for i in range(8):
            rr=r+self.__neighbourIterator[i,0]
            cc=c+self.__neighbourIterator[i,1]
            if (rr>-1 and rr<self.getRows() and cc>-1 and cc<self.getCols()):
                neighbours.append(self._data[rr,cc])
                
        return neighbours
    
    
    def lowestNeighbour(self,r,c):
        """Calculates the lowest neighbour, excluding itself
        
        Input Parameter:
            r – x-coordinate of the cell
            c – y-coordinate of the cell
        
        Returns:
            lownode - the node representing the lowest neighbour, a FlowNode object
        """
        lownode=None
        
        for neighbour in self.getNeighbours(r,c):
            if lownode==None or neighbour.getElevation() < lownode.getElevation():
                lownode=neighbour
        
        return lownode

    def setDownnodes(self):
        """Calculates Downnodes and sets them for each FlowNode object
        
        """
        for r in range(self.getRows()):
            for c in range(self.getCols()):
                lowestN = self.lowestNeighbour(r,c)
                if (lowestN.getElevation() < self._data[r,c].getElevation()):
                    self._data[r,c].setDownnode(lowestN) #set downnode, upnode is set within the FlowNode class

    
    def getMaximumFlow(self):
        """Calculates the maximum flow within the FlowRaster
        
        Returns:
            a tuple – (maxrate, maxnode)
                    maxrate: maximum flow rate, a float
                    maxnode: node with maximum flow rate, a Flownode object
        """
        flow=self.extractValues(FlowExtractor()) #get flow data
        maxrate=None
        maxnode=None
        for i in range(flow.shape[0]): #iterate through data
            for j in range(flow.shape[1]): #iterate through data
                if maxrate is None or flow[i,j]>maxrate:
                    maxrate=flow[i,j]
                    maxnode=(i,j)
        return (maxrate, self._data[maxnode[0],maxnode[1]])
    
    
    
    def getTotalRainfall(self):
        """Calculates the total rainfall over all cells
        
        Returns:
            total rainfall – a number
        """
        rainfall=self.extractValues(RainfallExtractor())
        total=0
        for i in range(rainfall.shape[0]): #iterate through data
            for j in range(rainfall.shape[1]): #iterate through data
                total+=rainfall[i,j] #add rainfall
        return total
        
    
    def getTotalFlow(self):
        """Calculates the total flow over all cells
        
        Returns:
            total flow – a number
        """
        flow=self.extractValues(FlowExtractor())
        total=0
        for i in range(flow.shape[0]): #iterate through data
            for j in range(flow.shape[1]): #iterate through data
                edgecase = i==0 or j==0 or i==(self._data.shape[0]-1) or j==(self._data.shape[1]-1)
                if self._data[i,j].getPitFlag() and edgecase:
                    total+=flow[i,j]
        return total
    
    
    def extractValues(self, extractor):
        """Extract values from FlowRaster object
        
        Input Parameter:
            extractor – A FlowExtractor class object
        """
        values=[]
        for i in range(self._data.shape[0]): #iterate through data
            for j in range(self._data.shape[1]): #iterate through data
                values.append(extractor.getValue(self._data[i,j]))
        valuesarray=np.array(values) #convert to numpy array
        valuesarray.shape=self._data.shape #reshape
        return valuesarray
    

    
    
    def addRainfall(self, rainfall):
        """Adds rainfall to the Raster by adding the rainfall value 
        to each FlowNode
        
        Input Parameter:
            rainfall – numpy.ndarray containing rainfall for each cell
                        expected to have the same size an shape as 
                        the raster data
        """
        assert rainfall.shape[0]==self._data.shape[0] #assert that same shape
        assert rainfall.shape[1]==self._data.shape[1] #assert that same shape
        
        for i in range(rainfall.shape[0]): #iterate through array
            for j in range(rainfall.shape[1]): #iterate through array
                self._data[i,j].setRainfall(rainfall[i,j]) #set cells rainfall



class Lake():
    """A class representing lakes
    Helper for the calculation of lakes
    
    """
    
    def __init__(self, startNode):
        """Contructor for Lake class
        
        Input Parameter:
            startNode – pitflag to start calculating the lake
        
        """
        assert startNode.getPitFlag()
        self._neighbours = []
        self._nodes = []
        self.addNode(startNode)
        self._outflow=None

        

    def addNeighbours(self, neighbours):
        """Adds new neighbours to self._neighbours
        ¨¨
        Input Parameter:
            neighbours – a list of neighbour nodes
        """
        for node in neighbours:
            #check if already in lake or already in neighbours
            if node not in self._neighbours and node not in self._nodes:
                self._neighbours.append(node)

        
        
    def removeNeighbour(self, node):
        """Removes neighbours from self._neighbours
        
        Input Parameter:
            node – a FlowNode object which should be removed
        """
        if node in self._neighbours:
            self._neighbours.remove(node)

            
    def lowestNeighbour(self):
        """Calculates the lowest neighbour of the lake
        
        Returns:
            lownode - the node representing the lowest neighbour, a FlowNode object
        """
        lownode=None
        
        for neighbour in self._neighbours:
            if lownode==None or neighbour.getElevation() < lownode.getElevation():
                lownode=neighbour
        
        return lownode
    
        
        
    def addNode(self, node):
        """adds a new node to the lake, removes the node from self._neighbours
        
        Input Parameter:
            node – to be added, a FlowNode object
        """
        assert node not in self._nodes
        self.removeNeighbour(node)
        self._nodes.append(node)
        
        for node in self._nodes:
            assert node not in self._neighbours
        
    
    def isLake(self, node):
        """Returns true if the input node is in the Lake
        
        Input Parameter:
            node – a FlowNode object
        """
        return node in self._nodes
    

                
    def finalise(self):
        """Finalises a lake. Calculates the lake outflow (highest point) and removes
        nodes within self._nodes visited after the outflow.
        
        The lake path must have arrived at an edge pitflag to call this method
        """
        assert self._nodes[-1].getPitFlag() #must arrive at a pitflag
        highest = self.getHighestPosition()

        self._outflow=self._nodes[highest]
        self._nodes=self._nodes[:highest+1]
        
        for node in self._nodes:
            node.fill(self._outflow.getElevation())
    

        
    def getHighestPosition(self):
        """Calculates highest position of a lake pathe
        
        Returns:
            an index of the position of the highest point within self._node list
        """
        highest=None
        index=None
        
        for i, node in enumerate(self._nodes):
            if highest==None or node.getElevation() >= highest.getElevation(): #>= because it should replace when equal
                highest=node
                index=i
        
        return index
        
        

    
    
class FlowExtractor():
    """A class responsible for extracting flow values
    
    """
    
    def __init__(self, rain=None):
        """Constructor of FlowExtractor
        if a constant rain parameter is given the flow will be calculated with the constant rain.

        Input Parameter:
            rain – an optional constant rain parameter (per cell) in mm
        """
        self._constantRain=rain
    
    def getValue(self, node):
        """extracts the flow value of a node
        
        Input Parameter:
            node – A FlowNode class object
        """
        return node.getFlow(self._constantRain)
    
    
class LakeDepthExtractor():
    """A class responsible for extracting lake depth values
    
    """
   
    
    def getValue(self, node):
        """extracts the flow value of a node
        
        Input Parameter:
            node – A FlowNode class object
        """
        return node.getLakeDepth()
    
    
class ElevationExtractor():
    """A class responsible for extracting elevation values
    
    """

    def getValue(self, node):
        """extracts the flow value of a node
        
        Input Parameter:
            node – A FlowNode class object
        """
        return node.getElevation()
    
    
class RainfallExtractor():
    """A class responsible for extracting rainfall values
    
    """
    
    def getValue(self, node):
        """extracts the flow value of a node
        
        Input Parameter:
            node – A FlowNode class object
        """
        return node.getRainfall()

