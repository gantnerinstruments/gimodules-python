# -*- coding: utf-8 -*-

"""
Created on Tue Jun  2 12:39:28 2020
@author: BJ
Gantner Instruments to Python tutorials
Connect to GINS Controller
"""


import initExample ## Add path to library (just for examples; you do not need this)

import ginsapy.giutility.connect.PyQStationConnectWin as Qstation #module with communication functions to Gantner Q.Station under windows environment

import numpy as np #module for scientific operations
import pyqtgraph as pg # Scientific Graphics and GUI Library for Python. Use for fast display
from pyqtgraph.Qt import QtCore



#****************************************************
# Input parameters
#*****************************************************

controller_IP="192.168.178.43"#Controller IP
channel_nb=[8]#channel number to be ploted you can enter several indexes[1,2,3,4]. Index 0 is timestamp
window_size=4096# Size of the ploting window
buffer_index=0#Enter the index of the buffer
#****************************************************


#Initialisation of a buffer connection
conn=Qstation.ConnectGIns()
conn.bufferindex=int(buffer_index)
conn.init_connection(str(controller_IP))

#Return some information of the controller
conn.read_controller_name()
conn.read_serial_number()
conn.read_sample_rate()
conn.read_channel_names()
conn.read_channel_count()
print(conn.read_index_name(0))


#Call function to store Controller buffer into the variable buffer
buffer=conn.yield_buffer()


#function to initiate a pyqtgraph plot
def init_curve(graph,init_list):
    curve=[]
    for i in range(len(init_list)):
        c = graph.plot()
        curve.append(c)
    return(curve)


#*************
#Visualisation of the measurements
#*************



signal_plot=np.zeros((window_size,len(channel_nb)))#output matrix initialisation


win = pg.GraphicsWindow(title="Basic plotting example")
win.resize(1000,600)
win.setWindowTitle('Time Signal')

plot_1 = win.addPlot(title="Title: Time plot")
curves=init_curve(plot_1,channel_nb)

win.show()

#Function to update graph
def update():
    global curves,channel_nb,buffer,signal_plot,window_size,readbuffer
    readbuffer=next(buffer)          #get next buffer frames
    disp = readbuffer[:,channel_nb]  #get channel columns out of readbuffer matrix
    dim=len(disp)                    #number of rows/dataframes
    signal_plot=np.vstack((signal_plot[dim:window_size,:],disp))

    for i in range(0,len(channel_nb)):
        curves[i].setData(y=signal_plot[:,i])



timer=QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)#refreshms
pg.QtGui.QGuiApplication.exec_()



