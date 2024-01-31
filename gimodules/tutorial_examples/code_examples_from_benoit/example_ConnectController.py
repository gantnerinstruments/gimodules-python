import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import ginsapy.giutility.connect.PyQStationConnectWin as Qstation

#### Input parameters
# Controller IP address
controller_IP = "192.168.178.43"  

# Channel number to be plotted. You can enter several indexes [1,2,3,4]. Index 0 is timestamp
channel_nb = [8]  

# Size of the plotting window
window_size = 4096  

# Enter the index of the buffer
buffer_index = 0  

# Initialization of a buffer connection
conn = Qstation.ConnectGIns()
conn.bufferindex = int(buffer_index)
conn.init_connection(str(controller_IP))

# Return some information of the controller
conn.read_controller_name()
conn.read_serial_number()
conn.read_sample_rate()
conn.read_channel_names()
conn.read_channel_count()
print(conn.read_index_name(0))

# Call function to store Controller buffer into the variable buffer
buffer = conn.yield_buffer()

# Function to initiate a pyqtgraph plot
def init_curve(graph, init_list):
    curve = []
    for i in range(len(init_list)):
        c = graph.plot()
        curve.append(c)
    return curve

# Visualisation of the measurements
# Output matrix initialization
signal_plot = np.zeros((window_size, len(channel_nb)))  

win = pg.GraphicsWindow(title="Basic plotting example")
win.resize(1000, 600)
win.setWindowTitle('Time Signal')

plot_1 = win.addPlot(title="Title: Time plot")
curves = init_curve(plot_1, channel_nb)

win.show()

# Function to update the graph in real time with the new data
def update():
    global curves, channel_nb, buffer, signal_plot, window_size, readbuffer
     # Get next buffer frames
    readbuffer = next(buffer)

    # Get channel columns out of readbuffer matrix 
    disp = readbuffer[:, channel_nb]  

    # Number of rows/dataframes
    dim = len(disp)  
    signal_plot = np.vstack((signal_plot[dim:window_size, :], disp))

    for i in range(0, len(channel_nb)):
        curves[i].setData(y=signal_plot[:, i])

timer = QtCore.QTimer()
timer.timeout.connect(update)

# Refresh interval in milliseconds
timer.start(100)  
pg.QtGui.QGuiApplication.exec_()
