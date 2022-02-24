# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 16:47:07 2020
DRAFT
@author: jouanb
"""
from ctypes import*
import ctypes
import os


class GetProcessBufferServer():
    def __init__(self):
        try:
            # chemin=os.path.abspath(".\\Giutility\\giutility_x64.dll")
            chemin = "libGInsUtility.so"
            #gins_lib = "/home/gins/data/libGInsUtility.so"
            self.GINSDll = ctypes.cdll.LoadLibrary(chemin)
            print("64 bit DLL imported")
            print(chemin)
        except OSError:
            print("can not imported libGInsUtility.so")

        self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo.argtypes = [
            c_int, c_char_p, c_size_t, c_char_p, c_size_t]
        self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer.argtypes = [
            c_char_p, POINTER(c_int), POINTER(c_int)]
        self.bufferID = ctypes.create_string_buffer(50)
        self.bufferName = ctypes.create_string_buffer(50)
        self.HCLIENT = c_int(-1)
        self.HCONNECTION = c_int(-1)

    def get_buffer_count(self):
        """create buffer"""
        self.count = self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferCount()
        return(self.count)

    def get_buffer_info(self, bufferIndex):
        ret = self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo(
            bufferIndex, self.bufferID, len(self.bufferID), self.bufferName, len(self.bufferName))
        if ret != 0:
            print("error get_buffer_info")
        else:
            print("buffer index:", bufferIndex, "buffer name:", self.bufferName.value.decode(
                'UTF-8'), "buffer ID:", self.bufferID.value.decode('UTF-8'))
        return(self.bufferName.value.decode('UTF-8'), self.bufferID.value.decode('UTF-8'))

    def init_buffer_conn(self, sbufferID):
        self.sbufferID = sbufferID.encode('UTF-8')
        ret = self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer(
            self.sbufferID, byref(self.HCLIENT), byref(self.HCONNECTION))
        if(ret != 0):
            print("Init Connection Failed - ret:", ret)
