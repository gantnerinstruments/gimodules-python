# -*- coding: utf-8 -*-

"""
Created on July 37 14:00:19 2018
@author: BJ
Gantner Instruments to Python tutorials
Read Gantner UDBF File
"""
#module with communication functions to Gantner Q.Station under windows
import initExample ## Add path to library (just for examples; you do not need this)

import ginsapy.giutility.connect.PyQStationConnectWin as Qstation
#use PyQStationConnect_2_0_lin to work under linux

import numpy as np #module for scientific operations

import datetime #to return the date of the execution of the script

import os# to manipulate files

from matplotlib import pyplot as plt#graphical library
import matplotlib.dates as mpdt#to change the date format in the graph

#*********************************************************************************************************************
#**************** Define some file dependant variables
#*********************************************************************************************************************


#File to be imported
Raw_file="GinsDataloggerReadDatFiles.dat"#Name of udbf to be imported
path_dir = os.path.dirname(__file__)          
path_udbf = os.path.join(path_dir, Raw_file)# This return the absolute path of the file

#liste of channels to be imported
index_channels_temperature=[1,6,7,8,9]

#index of the timestamp allways 0
index_timestamp=0
first_temperature_index=1

#*********************************************************************************************************************
#**************** Import the communication function between pythin and Q.Station
#*********************************************************************************************************************

print("we enter the Gantner Instrument initialisation")
#Initialisation of a file connection
conn=Qstation.ConnectGIns()
conn.init_file(path_udbf)



print('plot in the python windows the index and name of channels')
conn.read_channel_names()#Return some information of the logged file


print('We print some information on the loaded file')
max_channel=conn.read_channel_count()#number of channels
f_samples=conn.read_sample_rate() #sampling rate

print('You can write in variables the channels name and units')
index_name_time=conn.read_index_name(index_timestamp)
index_unit_time=conn.read_index_unit(index_timestamp)
print(index_name_time,index_unit_time)

#if you have some encoding problems on your distribution you can try following:
index_name_temp=conn.read_index_name(first_temperature_index)
index_unit_temp=conn.read_index_unit(first_temperature_index)



#*********************************************************************************************************************
#**************** Import the dat file in a matrix
#*********************************************************************************************************************
try:
    dat_file=Qstation.read_gins_dat(conn)
    print('file was imported in a numpy matrix: dat_file[row,column]')
except:
    print('file could not be imported')

#*********************************************************************************************************************
#**************** Basic operation on the matrix:
#*********************************************************************************************************************

print('Number of rows',len(dat_file[:,0]))
print('Number of columns',len(dat_file[0,:]))
print('see the timestamp column:',dat_file[:,0])

init_time=dat_file[0,index_timestamp]
init_temp=dat_file[0,first_temperature_index]


print('At init time:',init_time,'for channel:',index_name_temp,'the temperature is:',init_temp,index_unit_temp)

#*********************************************************************************************************************
#**************** Search for min/max values
#*********************************************************************************************************************

min_temp=np.min(dat_file[:,first_temperature_index])
print('the minimum temperature is:',min_temp,index_unit_temp)

max_temp=np.max(dat_file[:,first_temperature_index])
print('the maximum temperature is:',max_temp,index_unit_temp)


#*********************************************************************************************************************
#**************** Write results in a text file
#*********************************************************************************************************************

now=datetime.datetime.now()
now=now.strftime("%d.%m.%Y %H:%M")

if not os.path.exists('results'):
    os.makedirs('results')

if not os.path.isfile('./results/resu.txt'):
    with open ("./results/resu.txt", "w") as log_file:
        log_file.write('journal created on: '+now+'\n')

with open ("./results/resu.txt", "a") as log_file:
    log_file.write('**********************')
    log_file.write('\n')
    log_file.write("1;Journal update;"+now+"\n")

    try:
        log_file.write("2;Minimum temperature;"+str(min_temp)+"; ["+index_unit_temp.encode('UTF-8')+"] \n")
        log_file.write("3;Maximum temperature;"+str(max_temp)+"; ["+index_unit_temp.encode('UTF-8')+"] \n")
    except:        
        log_file.write("2;Minimum temperature;"+str(min_temp)+"; ["+index_unit_temp+"] \n")
        log_file.write("3;Maximum temperature;"+str(max_temp)+"; ["+index_unit_temp+"] \n")



#*********************************************************************************************************************
#**************** We now plot the first temperature channel in a graph
#*********************************************************************************************************************

#we define an help function to transform the time into human readable format

def ole2datetime(oledt):
    '''Convert OLE To DATE-TIME'''
    OLE_TIME_ZERO = datetime.datetime(1899, 12, 30, 0, 0, 0)
    return OLE_TIME_ZERO + datetime.timedelta(days=float(oledt))

#we transform the file time sample into date_strings and date_num-->unix time
date_strings=[ole2datetime(oledt) for oledt in dat_file[:,index_timestamp]]
date_num=mpdt.date2num(date_strings)


#we prepare the axis
figAxis,axAxis=plt.subplots()
axAxis.xaxis_date()
axAxis.fmt_xdata=mpdt.DateFormatter('%d-%m% %H:%M:%S')
figAxis.autofmt_xdate()
try:
    axAxis.set_ylabel(("Y: Temp[°C]"), fontsize=10)
except:
    axAxis.set_ylabel((u'Y: Temp[°C]'), fontsize=10)

#we plot the channel in the graph
try:
    axAxis.plot(date_num,dat_file[:,first_temperature_index],color='green',linewidth=1,label="T1 [°C]")
except:
    axAxis.plot(date_num,dat_file[:,first_temperature_index],color='green',linewidth=1,label=u'T1 [°C]')

#we add the legend
axAxis.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,prop={'size':5})

#we will save the graph in png
name_graph_axis="Temperature"
figAxis.savefig((('./results/{}.png').format(name_graph_axis)),format='png',dpi=500)


#*********************************************************************************************************************
#**************** Close connection
#*********************************************************************************************************************

# we close the connection
conn.close_connection()
