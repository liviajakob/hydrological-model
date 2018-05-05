from RasterHandler import createRanRasterSlope
import matplotlib.pyplot as mp
import Flow as Flow
from RasterHandler import readRaster


"""This is the driver - Livia Jakob S1790173"""



def plotstreams(flownode,colour):
    """Recursively plots upnodes in given colour
    
    Input Parameter:
        flownode – a FlowNode object
        colour – a colour, e.g. "red"
    """
    for node in flownode.getUpnodes():
        x1=flownode.get_x()
        y1=flownode.get_y()
        x2=node.get_x()
        y2=node.get_y()
        mp.plot([x1,x2],[y1,y2],color=colour)
        if (node.numUpnodes()>0):
            plotstreams(node,colour)

def plotFlowNetwork(originalRaster, flowRaster, title="", plotLakes=True):
    """Plots a flow network
    
    Input Parameter:
        originalRaster – a Raster object
        flowRaster – a FlowRaster object
        title – plot title, a string
        plotLake – binary variable stating if lakes should be plotted
                    True if lakes should be plotted
                    False if lakes should be ignored
    """
    print ("\n\n{}".format(title))
    mp.imshow(originalRaster.extractValues(Flow.ElevationExtractor()))
    mp.colorbar()
    colouri=-1
    colours=["black","red","magenta","yellow","green","cyan","white","orange","grey","brown"]

    for i in range(flowRaster.getRows()):
        for j in range(flowRaster.getCols()):
            node = flowRaster._data[i,j]
            
            if (node.getPitFlag()): # dealing with a pit
                mp.scatter(node.get_x(),node.get_y(), color="red")
                colouri+=1
                plotstreams(node, colours[colouri%len(colours)])
                
            if (plotLakes and node.getLakeDepth() > 0): #if lakedepth is zero, it is not a lake
                mp.scatter(node.get_x(),node.get_y(), color="blue")

    mp.show()

def plotExtractedData(flowRaster, extractor, title=""):
    """Plots extracted data
    
    Input Parameter:
        flowRaster – FlowRaster class object
        extractor – FlowExtractor class object, or LakedepthExtractor object
        title – String of chart title
    """
    print ("\n\n{}".format(title))
    mp.imshow(flowRaster.extractValues(extractor))
    mp.colorbar()
    mp.show()

def plotRaster(araster, title=""):
    """Plots a raster
    
    Input Parameter:
        araster – Raster class object
        title – plot title, a string
    """
    print ("\n\n{}, shape is  {}".format(title, araster.shape))
    mp.imshow(araster)
    mp.colorbar()
    mp.show()


def calculateFlowsAndPlot(elevation, rain, resampleF):
    """Calculates all the flows and plots them
    
    Input Parameter:
        elevation – a Raster class object containing elevation
        rain – a Raster class object containing rainfall
        resampleF – an Integer
    
    """
    
    # plot input rasters
    plotRaster(elevation.getData(), "Original elevation (m)") #plot elevation
    plotRaster(rain.getData(), "Rainfall") #plot rainfall

    resampledElevations = elevation.createWithIncreasedCellsize(resampleF)

    
    
    
    ################# step 1 find and plot the intial network #######
    fr=Flow.FlowRaster(resampledElevations) #create FlowRaster
    plotFlowNetwork(fr, fr, "Task 1: Network structure - before lakes", plotLakes=False) #plot flow raster
    

    ################Step 2 ######################################
    plotExtractedData(fr, Flow.FlowExtractor(1), "Task 2: River flow rates - constant rain")
    
    
    
    ################# step 3 #######################################
    #handle variable rainfall
    fr.addRainfall(rain.getData())
    plotExtractedData(fr, Flow.FlowExtractor(), "Task 3: River flow rates - variable rainfall")
    
    ############# step 4 and step 5 #######################################
    # handle lakes
    
    fr.calculateLakes()

    plotFlowNetwork(fr, fr, "Task 4: Network structure (i.e. watersheds) - with lakes")
    plotExtractedData(fr, Flow.LakeDepthExtractor(), "Task 4: Lake depth")
    plotExtractedData(fr, Flow.FlowExtractor(), "Parallel Flows")
    
    #TESTING
    #this line tests if total raster outflow is equal to total rainfall on the raster
    assert round(fr.getTotalFlow(), 2) == round(fr.getTotalRainfall(),2)
    
    
    ############# step 5 #######################################
    maxflow=fr.getMaximumFlow()
    print("Task 5: Maximum Flow: {} mm, at FlowNode object: {}".format(round(maxflow[0], 3), maxflow[1]))

    

############# step 1 to 4 #######################################
# Create Random Raster
rows=40
cols=40
xorg=0.
yorg=0.
xp=5
yp=5
nodata=-999.999
cellsize=1.
levels=4
datahi=100.
datalow=0
randpercent=0.1
    
resampleFactorA = 1
elevationRasterA=createRanRasterSlope(rows,cols,cellsize,xorg,yorg,nodata,levels,datahi,datalow,xp,yp,randpercent)   
rainrasterA=createRanRasterSlope(rows//resampleFactorA,cols//resampleFactorA,cellsize*resampleFactorA,xorg,yorg,nodata,levels,4000,1,36,4,.1)   

##random raster
calculateFlowsAndPlot(elevationRasterA, rainrasterA, resampleFactorA)

############# step 5 #######################################

#calculateFlowsAndPlot(readRaster('ascifiles/dem_hack.txt'), readRaster('ascifiles/rain_small_hack.txt'), 10)

