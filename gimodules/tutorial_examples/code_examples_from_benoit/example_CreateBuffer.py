# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 16:47:07 2020
@author: BJ
Gantner Instruments to Python tutorials
Create a new Stream in GI.data
"""


import initExample ## Add path to library (just for examples; you do not need this)

import ginsapy.giutility.connect.PyQStationConnectWin as Qstation
import ginsapy.giutility.buffer.GInsDataCreateBuffer as NewStream#This is an extra library with buffer methods


import numpy as np #module forvectorial operations
import datetime#module for datetime manupulation
import time


# We import the Python class with giutilities function
conn_stream=NewStream.PostProcessBufferServer()

#****************************************************
# Input parameters
#*****************************************************

ID='ff1fbdd4-7b23-11ea-bd6d-005056c00001' #Enter GI.bench specific ID project or let the default one
BufferName='PythonBuffer'#Enter Buffer Name
StreamSampleRate=10#Enter the sampling rate in HZ
variableID='vv1fbdd4-7b23-11ea-bd6d-005056c00001'#Enter unique ID of the new variable
variableName='python_variable'#Variable name
Unit='V'#Variable unit


#****************************************************
# Initialisation of the buffer and channel
#*****************************************************
conn_stream.create_buffer(ID,BufferName,StreamSampleRate)#Create a new buffer

conn_stream.add_channel(variableID,variableName,Unit)#Add a new channel

conn_stream.init_buffer()#initialisation of the buffer



Timestamp_start_ns=np.uint64(round(time.time()-946684800)*1000000000)#start time point in nano seconds
sleep=int(conn_stream.frameBufferLength/StreamSampleRate*1000)# sleep time in ms
nsPerSample=int(1000000000/StreamSampleRate)
LS_write=0# Load step for information only
nanos=np.uint64((Timestamp_start_ns))# nanos is our counter time in nanoseconds DC system time


while True:
    for frameindex in range(0,int(conn_stream.frameBufferLength)):#We iterate ofer the frames
        conn_stream.write_timestamps(int(frameindex),nanos)#we write timestamp to each frame
        nanos=np.uint64(nanos+nsPerSample)
        #print("frame index",frameindex,"counter",nanos)
        value=np.multiply(np.random.random_sample(),100)#We generate a random value zwischen [0;100]
        conn_stream.write_to_framebuffer(int(frameindex),0,value)# we write value to frame
        LS_write=LS_write+1# we increase the load step -->for information only
    conn_stream.append_to_framebuffer()#We append the frames to the buffer
    conn_stream.buffer_sleep(sleep)#we sleep in order to generate data with defined StreamSample Rate and not CPU rate 
    

conn_stream.close_buffer(conn_stream.bufferHandle)#Closing the stream will delete the online values
        
