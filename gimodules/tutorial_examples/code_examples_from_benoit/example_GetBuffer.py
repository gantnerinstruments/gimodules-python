import initExample ## Add path to library (just for examples; you do not need this)

import ginsapy.giutility.connect.PyQStationConnectWin as Qstation #module with communication functions to Gantner Q.Station under windows environment
import ginsapy.giutility.buffer.GInsDataGetBuffer as QStream #This is an extra library with buffer methods



conn_get_stream=QStream.GetProcessBufferServer()#we initiate the class
count_buffer=conn_get_stream.get_buffer_count()#we check the number of streams
print("count buffer:",count_buffer)
if count_buffer>0:
    for buffer_index in range(0,count_buffer):
        buffer_name,buffer_ID=conn_get_stream.get_buffer_info(int(buffer_index))
else:
    print("no buffer found. check in GI.bench your active buffer")


#****************************************************
# Input parameters
#*****************************************************

enter_buffer="ff1fbdd4-7b23-11ea-bd6d-005056c00001"#Enter the buffer ID to be access
plot_data=True

#*****************************************************
#*****************************************************


conn=Qstation.ConnectGIns()#We create a new connection
conn.init_buffer_conn(enter_buffer)#We initialise the connection

#Return some information on the stream
conn.read_sample_rate()
conn.read_channel_names()
conn.read_channel_count()



#****************************************************
# Plot date : plot_data=True
#*****************************************************

if plot_data==True:
    # all this block if for representation only
    import numpy as np
    import datetime
    import time
    from numpy import vstack
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtGui, QtCore
    
    
    #Parameters
    List_plots=[1]#[1,2]#Index of channels to be plotted
    Window=4096# Size of the ploting window
    
    #Call function to store buffer into the variable buffer
    buffer=conn.yield_buffer()#This is a generator we wait the next call to yield to read the next part of the buffer
        
    #function to initiate a plot
    def init_curve(graph,init_list):
        curve=[]
        for i in range(len(init_list)):
            c = graph.plot()
            curve.append(c)
        return(curve)
    
    
    #*************
    #Visualisation of the measurements
    #*************
    
  
    
    Signal=np.zeros((Window,len(List_plots)))#output matrix initialisation
        
    win = pg.GraphicsWindow(title="Basic plotting example")
    win.resize(1000,600)
    win.setWindowTitle('Time Signal')
    
    plot_1 = win.addPlot(title="Title: Time plot")
    curves=init_curve(plot_1,List_plots)
        
    win.show()
        
    def update():
        global curves,List_plots,buffer,Signal,Window,readbuffer
        readbuffer=next(buffer)          #get next buffer frames
        disp = readbuffer[:,List_plots]  #get channel columns out of readbuffer matrix
        dim=len(disp)                    #number of rows/dataframes
        Signal=np.vstack((Signal[dim:Window,:],disp))
    
        for i in range(0,len(List_plots)):
            curves[i].setData(y=Signal[:,i])
        
    
    timer=QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)#1000=1s call
    
    ## Start Qt event loop unless running in interactive mode or using pyside.
    if __name__ == '__main__':
        import sys
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
    
