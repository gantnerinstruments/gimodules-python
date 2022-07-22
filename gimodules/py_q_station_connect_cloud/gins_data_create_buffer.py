# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 16:47:07 2020

@author: jouanb
"""
from ctypes import*
import ctypes
import os


#//////////////////////////////////////////////////////////////////////////////////////////
#/*------------- PostProcess buffer server handling -------------------------------------*/
#/*																						*/
#/*	Description:																		*/
#/*																						*/
#/*		Following functions allow creation of PostProcess buffers / data stream			*/
#/*		Depending on environmental settings, different data backends are supported   	*/
#/*																						*/
#//////////////////////////////////////////////////////////////////////////////////////////
#/**
# * @brief Create new PostProcess buffer / SystemStream
# *
# * @param sourceID			source UUID (SID) of this buffer
# * @param sourceName		name of this buffer
# * @param measurementID		measurement UUID (MID) of the actual mesurement
# * @param measurementName	name of the actual measurement
# * @param sampleRateHz		the desired sample rate for this measurement
# * @param bufferSizeByte	the maximum size of this buffer in bytes
# * @param segmentSizeByte	the size of a buffer segment (if supported)
# * @param retentionTimeSec  data retention time of this buffer (if supported)
# *
# * @param bufferHandle		the result handle
# * @param errorMsg			buffer for error message text if not successful
# * @param errorMsgLen		length of the error message buffer
# *
# * @return General return codes
# */

#const char* -->c_char_p
#double      -->c_double
#double*      -->POINTER(c_double)
#uint64_t    -->? probably c_int
#int32_t      -->c_int
#int32_t*    -->POINTER(c_int)
#char*       -->c_char_p
#uint32_t    -->c_int


class PostProcessBufferServer():
    def __init__(self):

        try:
            #chemin=os.path.abspath(".\\Giutility\\giutility_x64.dll")
            chemin = "libGInsUtility.so"
            
            self.GINSDll = ctypes.cdll.LoadLibrary(chemin)
            
            
            print("64 bit DLL imported")
            print(chemin)
        except OSError as err:
            print("err: {}\ncan not imported libGInsUtility.so", format(err))

        #New v3.0
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Create.argtypes = [c_char_p,c_char_p,c_double,c_ulonglong,c_ulonglong,c_double,c_char_p,POINTER(c_int),c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AddVariableDefinition.argtypes = [c_int,c_char_p,c_char_p,c_char_p,c_int,c_int,c_int,c_int,c_double,c_double,c_char_p,c_int]        
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Initialize.argtypes =[c_int,c_int,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteDoubleToFrameBuffer.argtypes =[c_int,c_int,c_int,c_double,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteTimestampToFrameBuffer.argtypes =[c_int,c_int,c_ulonglong,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendFrameBuffer.argtypes =[c_int,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendDataBuffer.argtypes =[c_int,c_char_p,c_ulonglong,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Close.argtypes =[c_int,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_SleepMS.argtypes =[c_int]
        #self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_CreateUDBFFileBuffer.argtypes = [c_char_p,c_char_p,c_char_p,c_double,c_ulonglong, c_int16,POINTER(c_int32),c_char_p,c_int32]
        self.buffersize=50000000
        self.segmentsize=50000000
        self.bufferHandle=c_int(-1)
        self.errorlen=30
        self.frameBufferLength=10
        self.errorMsg=ctypes.create_string_buffer(30)
        

    def create_UDBF_file_buffer(self, file_path, stream_id, stream_name, sample_rate):
        self.max_length_in_sec = 3600 #the maximum length of a file in seconds
        self.options = 0 # bitset for future options- what does that mean???

        self.ID = stream_id.encode('UTF-8')
        self.BufferName = stream_name.encode('UTF-8')
        self.StreamSampleRate = sample_rate

        #TODO when udbf upload is rdy - add function here

    def create_buffer(self,ID,BufferName,StreamSampleRate):
        """create buffer"""
        self.ID= ID.encode('UTF-8')
        self.BufferName=BufferName.encode('UTF-8')
        self.StreamSampleRate=StreamSampleRate
        
        dataTypeIdent='raw'
        self.dataTypeIdent=dataTypeIdent.encode('UTF-8')
        #self._CD_eGateHighSpeedPort_PostProcessBufferServer_Create.argtypes = [c_char_p,c_char_p,c_double,c_int,c_int,c_double,c_char_p,POINTER(c_int),c_char_p,c_int]
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Create(self.ID, self.BufferName, self.StreamSampleRate, self.buffersize, self.segmentsize,0, self.dataTypeIdent, byref(self.bufferHandle),self.errorMsg, self.errorlen)
        if ret!=0:
            print("Error at create buffer!")

    def add_channel(self,variableID,variableName,Unit):
        """add channels"""
        self.variableID=variableID.encode('UTF-8')
        self.variableName=variableName.encode('UTF-8')
        self.Unit=Unit.encode('latin-1')
        self.DataTypeCode=8
        self.VariableKindCode=6
        self.Precision=4
        self.FieldLength=8
        self.RangeMin=-100
        self.RangeMax=100
        self.errorMsgLen=self.errorlen
        #self._CD_eGateHighSpeedPort_PostProcessBufferServer_Create.argtypes = [c_char_p,c_char_p,c_double,c_int,c_int,c_double,c_char_p,POINTER(c_int),c_char_p,c_int]
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AddVariableDefinition(self.bufferHandle, self.variableID, self.variableName, self.Unit,self.DataTypeCode,self.VariableKindCode,self.Precision,self.FieldLength,self.RangeMin,self.RangeMax,self.errorMsg,self.errorMsgLen)
        if ret!=0:
            print("Error adding channel")
            
    def init_buffer(self):
        """Init buffer"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Initialize(self.bufferHandle, self.frameBufferLength, self.errorMsg, self.errorMsgLen)
        if ret!=0:
            print("Error buffer initialized")
            self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Close(self.bufferHandle,self.errorMsg, self.errorMsgLen)
        else :
            print("success buffer ini",self.bufferHandle) 
    def write_timestamps(self,frameIndex,timestamp_ns):
        #self.frameIndex=frameIndex
        #self.valueInt=timestamp_ns
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteTimestampToFrameBuffer(self.bufferHandle,frameIndex,timestamp_ns,None, self.errorMsgLen)
        if ret!=0:
            print("error writing timestamps")
        return (ret)
        #else :
        #    print("success writing timestamps","buffer",self.bufferHandle,"frameindex",frameIndex,"ts",timestamp_ns,)
            
    def write_to_framebuffer(self,frameIndex,variableIndex,valueDouble):
        #self.frameIndex=frameIndex
        #self.variableIndex=variableIndex
        #self.valueDouble=valueDouble
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteDoubleToFrameBuffer(self.bufferHandle,frameIndex,variableIndex,valueDouble,self.errorMsg, self.errorMsgLen)
        if ret!=0:
            print("error filling frame")
        return (ret)
        #else :
        #    print("success filling fram ret",ret)
            #print("error message",self.errorMsg)

    def append_to_framebuffer(self):
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendFrameBuffer(self.bufferHandle,self.errorMsg,self.errorMsgLen)
        if ret!=0:
            print("error append to framebuffer - code:" + str(ret))
            print(self.errorMsg.value, "len:",self.errorMsgLen )
            
    def append_data_to_framebuffer(self,data,dataLength):
        self.data=data
        self.dataLength=dataLength
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendDataBuffer(self.bufferHandle,self.data,self.dataLength,self.errorMsg,self.errorMsgLen)
        if ret!=0:
            print("error append_data")

    def close_buffer(self,bufferHandle):
        self.bufferHandle=bufferHandle
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Close(self.bufferHandle,self.errorMsg, self.errorMsgLen)
        if ret!=0:
            print("error closing connection")
            
    def buffer_sleep(self,sleep_time):
        #self.sleep_time=sleep_time
        ret=self.GINSDll._CD_eGateHighSpeedPort_SleepMS(sleep_time)
        if ret!=0:
            print("error by sleeping")

