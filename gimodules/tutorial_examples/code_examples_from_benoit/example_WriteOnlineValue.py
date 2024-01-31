# module with communication functions to Gantner Q.Station under windows
import initExample ## Add path to library (just for examples; you do not need this)
import time
import numpy as np #module for scientific operations
import ginsapy.giutility.connect.PyQStationConnectWin as Qstation


#****************************************************
# Input parameters
#*****************************************************

controller_IP="192.168.18.51"#Controller IP
index_to_write=133#channel index to write value. Take care enter the index of input/output channels not input
value_to_write=123#value to be written

#Initialisation of a buffer connection
conn=Qstation.ConnectGIns()
conn.init_online_connection(str(controller_IP))#Take care use online connection for initialisation to have overall index number

#Return some information of the controller
conn.read_controller_name()
conn.read_serial_number()
conn.read_channel_names()
    
name_index=conn.get_channel_info_name(index_to_write)
print("name of the channel where value will be written :",name_index)

if conn.ret !=0 :
    print('A Mistake occured during connecting to the Gantner Controller. Verifiy than you give right IP adress and controller is online')
else:    
    conn.write_online_value(index_to_write,value_to_write)
    print("we add value to the selected channel")
    time.sleep(10)#wait 10 seconds
    print("we reset")
    conn.write_online_value(index_to_write,0)#Write value 0 after 10s
    conn.close_connection()#close connection
