# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 10:34:01 2020
@author: jouanb
Module to send simplified html request to the Cloud

change from 01.10.2021: new methods create import session
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import numpy as np
import pandas as pd
from pandas import json_normalize

#import pandas as pd
#import os

class CloudRequest():
    def __init__(self):
        self.empty='empty'
        self.url=''
        self.user=''
        self.PW=''
        self.ColumnSeparator= ";"
        self.DecimalSeparator= "."
        self.NameRowIndex= 0
        self.UnitRowIndex= 1
        self.ValuesStartRowIndex=2
        self.ValuesStartColumnIndex=3
        self.DateTimeFmtColumn1= "%d.%m.%Y"
        self.DateTimeFmtColumn2= ""
        self.DateTimeFmtColumn3=""

    def connect_gi_cloud(self):
        login_form={'username':self.user,'password':self.PW,'grant_type':'password'}#We create the Form with entries and values
        auth=HTTPBasicAuth('gibench', '')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        url_login = self.url+'/token'
        try:
            res = requests.post(url_login,data=login_form, headers=headers,auth=auth)
            self.login_res=res.json()
            self.auth_token=self.login_res['access_token']
        except Exception as e:
            print("connection failed")
            return e
        return (res)

    def create_import_session_udbf(self,stream_ID,stream_Name):
        '''method to import udbf file with http API'''
        url_list=self.url+'/history/data/import'
        param={"Type":"udbf","SourceID":stream_ID,"SourceName":stream_Name,"MeasID":"","SessionTimeoutSec":"300","AddTimeSeries":"false","SampleRate":"-1","AutoCreateMetaData":"true"}
        header_list = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.auth_token}
        try:
            response = requests.post(url_list,headers=header_list,json=param)
            self.import_session_res_udbf=response.json()
        except:
            print("create_import_session failed")
            response="error"
        return (response)


    def create_import_session_csv(self,stream_ID,stream_Name):
        '''method to import csv file with http API'''
        url_list=self.url+'/history/data/import'
        param={"Type":"csv","SourceID":stream_ID,"SourceName":stream_Name,"MeasID":"","SessionTimeoutSec":"300","AddTimeSeries":"false","SampleRate":"-1","AutoCreateMetaData":"true","CSVSettings": {"ColumnSeparator":self.ColumnSeparator,"DecimalSeparator": self.DecimalSeparator,"NameRowIndex": self.NameRowIndex,"UnitRowIndex": self.UnitRowIndex,"ValuesStartRowIndex":self.ValuesStartRowIndex,"ValuesStartColumnIndex":self.ValuesStartColumnIndex,"DateTimeFmtColumn1": self.DateTimeFmtColumn1,"DateTimeFmtColumn2": self.DateTimeFmtColumn2,"DateTimeFmtColumn3":self.DateTimeFmtColumn3}}
        header_list = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.auth_token}
        try:
            response = requests.post(url_list,headers=header_list,json=param)
            self.import_session_res_csv=response.json()
        except:
            print("create_import_session failed")
            response="error"
        return (response)

    
    def import_file_udbf(self,file):
        '''method to import udb file with http API'''
        self.session_ID=str(self.import_session_res_udbf['Data']['SessionID'])
        url_list=self.url+'/history/data/import/'+self.session_ID
        header_list = {'Content-Type':'application/octet-stream','Authorization': 'Bearer ' + self.auth_token}
        try:
            response_import=requests.post(url_list,headers=header_list,data=file)
        except:
            print("import  udbf failed")
            response="error"
        return (response_import)    

    def import_file_csv(self, file):
        '''method to import csv file with http API'''
        self.session_ID=str(self.import_session_res_csv['Data']['SessionID'])
        url_list=self.url+'/history/data/import/'+self.session_ID
        header_list = {'Content-Type':'text/csv','Authorization': 'Bearer ' + self.auth_token}
        try:
            response_import=requests.post(url_list,headers=header_list,data=file)

        except:
            print("import csv failed ,code:{}".format(response_import.status_code))
            response="error"
        return (response_import)


    def delete_import(self):
        '''method to delete session http API'''
        url_list=self.url+'/history/data/import/'+self.session_ID
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            response_delete=requests.delete(url_list,headers=header_list)
        except:
            print("delete failed")
            response="error"
        return (response_delete)    

    def list_gi_cloud_sources(self):
        url_list=self.url+'/kafka/structure/sources'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            response = requests.get(url_list,headers=header_list)
            self.sources_res=response.json()
        except:
            print("get list error")
            response="error"
        return (response)

    def print_stream_ID(self):
        self.stream_list=[]
        self.stream_ID=[]
        self.stream_last_ts=[]
        for i in range(0,len(self.sources_res['Data'])):
            try:
                self.stream_list.append(self.sources_res['Data'][i]["Name"])
                self.stream_ID.append(self.sources_res['Data'][i]["Id"])
                self.stream_last_ts.append(self.sources_res['Data'][i]["LastTimeStamp"])
                #print("Name: ",self.sources_res['Data'][i]["Name"],"Id:",self.sources_res['Data'][i]["Id"],\
                #      "last ts",self.sources_res['Data'][i]["LastTimeStamp"])
            except:
                print("error")
    def variable_mapping(self,ID_stream):
        query="{\n  variableMapping(sid: \""+ID_stream+"\") {\n    sid\n    columns {\n      name\n      variables {\n        id\n        dataType\n        name\n        unit\n      }\n    }\n  }\n}"
        url_list=self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_map = requests.post(url_list,json={'query':query},headers=header_list)
            self.request_map_res=request_map.json()
        except:
            print("error mapping")
            request_map="error"
        return(request_map)
    def print_var_mapping(self,request_map_res):
        channel_name=[]
        channel_unit=[]
        channel_index=[]
        channel_id=[]
        for i in range(0,len(request_map_res['data']['variableMapping']['columns'])):
            try:
                channel_name.append(request_map_res['data']['variableMapping']['columns'][i]['variables'][0]['name'])
                channel_unit.append(request_map_res['data']['variableMapping']['columns'][i]['variables'][0]['unit'])
                channel_index.append(request_map_res['data']['variableMapping']['columns'][i]['name'])
                channel_id.append(request_map_res['data']['variableMapping']['columns'][i]['variables'][0]['id'])
            except:
                print("error variable mapping")
                channel_name.append("error")
                channel_unit.append("error")
                channel_index.append("error")
                channel_idx.append("error")
        return(channel_index,channel_name,channel_unit,channel_id)
        
        
    def get_measurement(self,SID,timestamp_start,timestamp_stop):
        query_measurement="{\n  measurementPeriods(sid: \""+SID+"\",from: "+str(timestamp_start)+",\n \
        to: "+str(timestamp_stop)+") \
        {\n    minTs\n    maxTs\n    mid\n    sampleRate\n  }\n}"
        url_list=self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_measurement = requests.post(url_list,json={'query':query_measurement},headers=header_list)
            self.request_measurement_res=request_measurement.json()
        except:
            print("error get measurement")

    def get_measurement_limit(self,SID,limit):
        query_measurement="{\n  measurementPeriods(sid: \""+SID+"\",from: 0,\n    to: 9999999999999, limit: "+str(limit)+", sort: DESC) \
        {\n    minTs\n    maxTs\n    mid\n    sampleRate\n  }\n}"
        url_list=self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_measurement = requests.post(url_list,json={'query':query_measurement},headers=header_list)
            self.request_measurement_res=request_measurement.json()
        except:
            print("error get measurement")
            
            
            
    def print_measurement(self,request_measurement_res):
        limit=len(request_measurement_res['data']['measurementPeriods'])
        measurement_list=np.zeros((int(limit),2))
        for l in range(0,int(limit)):
    #print("start : ",request_measurement_res['data']['measurementPeriods'][l]['minTs'],"stop:",request_measurement_res['data']['measurementPeriods'][l]['maxTs'])
            measurement_list[l,0]=request_measurement_res['data']['measurementPeriods'][l]['minTs']
            measurement_list[l,1]=request_measurement_res['data']['measurementPeriods'][l]['maxTs']
        return(measurement_list)
        
    def get_data(self,ID_device,index_list,start_import,end_import):
        if len(index_list)>0:
            selected_index_string=""
            for j in range(0,len(index_list)):
                selected_index_string=selected_index_string+"\""+index_list[j]+"\""+" ,"
        else:
            print("no variable selected")
        query_data="{\n  Raw(columns: [\"ts\", \"nanos\","+selected_index_string+"], sid: \""+ID_device+"\", from: "+start_import+", to: "+end_import+") {\n    data\n  }\n}\n"            
        #query_data="{\n  Raw(columns: [\"ts\", \"nanos\", \"a0\", \"a1\"], sid: \""+ID_device+"\", from: "+start_import+", to: "+end_import+") {\n    data\n  }\n}\n"
        #query_data="{\n  Raw(columns: [\"ts\", \"nanos\", \"a1\", \"a0\",], sid: \""+ID_device+"\", from: "+start_import+", to: "+end_import+") {\n    data\n  }\n}\n"
        
        self.query_data_check=query_data
        url_list=self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_data= requests.post(url_list,json={'query':query_data},headers=header_list)
            self.request_data_res=request_data.json()
            #req_matrix_slb=self.request_data_res['data']['Raw']['data']
        except:
            print("error get data")

    def get_data_interactive(self,ID_device,index_list,start_import,end_import,resolution='nanos'):
        if resolution=='nanos':
            if len(index_list)>0:
                selected_index_string=""
                for j in range(0,len(index_list)):
                    selected_index_string=selected_index_string+"\""+index_list[j]+"\""+" ,"
            else:
                print("no variable selected")
            if resolution=='nanos':
                query_data="{\n  Raw(columns: [\"ts\", \"nanos\","+selected_index_string+"], sid: \""+ID_device+"\", from: "+start_import+", to: "+end_import+") {\n    data\n  }\n}\n"             
        else:            
            if len(index_list)>0:
                selected_index_string=""
                for j in range(0,len(index_list)):
                    selected_index_string=selected_index_string+index_list[j]+"{\n      avg\n}"
                #print(selected_index_string)
            else:
                print("no variable selected")

            #srcl# formatted to understand better. Why so many "\n"?
            query_data="{\n  analytics(from: "+start_import+", \
                to: "+end_import+", \
                resolution: "+resolution+" \
                sid: \""+ID_device+"\") \
                {\n    ts\n    "+selected_index_string+"\n}\n}\n"
                
        self.query_data_check=query_data
        url_list=self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_data= requests.post(url_list,json={'query':query_data},headers=header_list)
            self.request_data_res=request_data.json()
            #req_matrix_slb=self.request_data_res['data']['Raw']['data']
        except:
            print("error get data")
                      
            
    def filter_data(self,formated_data):
        data_matrix=formated_data['data']['Raw']['data']
        if len(data_matrix)>0:
            import_data=np.array(data_matrix)#We add the request return into a numpy matrix
            import_data=import_data.astype(float)
            nonecheck=np.isnan(import_data[:,:])
            none_index=np.where(nonecheck == True)
            import_data=import_data.astype(float)
            nonecheck=np.isnan(import_data[:,:])
            none_index=np.where(nonecheck == True)
            none_index_unique=np.unique(none_index[0][:])#we delete multi elements

            index_list_comple=np.linspace(0,len(import_data)-1,len(import_data))#we create a list with index same size than original data

            check_is_in=np.isin(index_list_comple,none_index_unique)#we check if nan index are in the element list
            excluded_nan=np.where(check_is_in == False)# we just take vales that are a number
            if len (excluded_nan[0])>0:#none number can be at the begining or at the end.
                first_valid_value=excluded_nan[0][0]
                last_valid_value=excluded_nan[0][-1]
                import_data=import_data[first_valid_value:last_valid_value,:]
                status=1
        else:
            import_data=[]#no corresponding values in the array between start and stop
            status=-1
        return(import_data,status)

    def filter_data_interactive(self,formated_data,selected_index,resolution='nanos'):
        '''this method is called to filter and format the values returned by from request'''
        if resolution=='nanos':
            data_matrix=formated_data['data']['Raw']['data']
            import_data=np.array(data_matrix)#We add the request return into a numpy matrix
        else:
            import_data=np.zeros((len(formated_data['data']['analytics']['ts']),len(selected_index)+1))
            import_data[:,0]=formated_data['data']['analytics']['ts']
            for k in range(0,len(selected_index)):
                import_data[:,k+1]=formated_data['data']['analytics'][selected_index[k]]['avg']
        
        import_data=import_data.astype(float)
        nonecheck=np.isnan(import_data[:,:])
        none_index=np.where(nonecheck == True)
        if len (none_index[0])>0:#none number can be at the begining or at the end.
            first_none=none_index[0][0]
            last_none=none_index[0][-1]
            if last_none==len(import_data)-1:
                import_data=import_data[0:first_none-1,:]
            else:    
                import_data=import_data[last_none+1:-1,:]
        return(import_data)

    def fetch_data_as_df(self, ID_stream, tenant, channels, begin, end):
        
        header_list = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.auth_token}
        
        convert= lambda dt: str(int(pd.to_datetime(dt).timestamp())*1000)
        data_query="{\nanalytics(from:" + convert(begin) + ",\
        to:" + convert(end) + ",resolution:QUARTER_HOUR,\
        sid:\"" + ID_stream + "\"){\nts\n"
        for i in channels:
            data_query += ""+str(i)+"{\navg\n}\n"
        data_query += "\n}\n}"
        request_data_res = requests.post(tenant + '/__api__/gql',json={'query':data_query},headers=header_list).json()
        df=json_normalize(request_data_res['data']['analytics']).apply(lambda x: x.explode())
        df=df.set_index(pd.to_datetime(df.ts*1e6)).drop(columns='ts')
        return df
    