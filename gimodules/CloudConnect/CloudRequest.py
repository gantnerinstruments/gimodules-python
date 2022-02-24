# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 10:34:01 2020

@author: jouanb
Module to send simplified html requests to the Cloud
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import numpy as np
from datetime import datetime
#import pandas as pd
#import os


class CloudRequest():
    'Module to send simplified html request to the Cloud'

    def __init__(self):
        self.empty = 'empty'
        self.url = ''
        self.user = ''
        self.PW = ''

    def connect_gi_cloud(self):
        'connect to GI.Cloud'
        # We create the Form with entries and values
        login_form = {'username': self.user,
                      'password': self.PW, 'grant_type': 'password'}
        auth = HTTPBasicAuth('gibench', '')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        url_login = self.url+'/token'
        try:
            res = requests.post(url_login, data=login_form,
                                headers=headers, auth=auth)
            self.login_res = res.json()
            self.auth_token = self.login_res['access_token']
            self.token_timestamp = (datetime.now().strftime("%H:%M:%S"))
        except ConnectionRefusedError:
            print("connection failed")
            res = res
        return (res)

    def list_gi_cloud_sources(self):
        'list sources'
        url_list = self.url+'/kafka/structure/sources'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            response = requests.get(url_list, headers=header_list)
            self.sources_res = response.json()
        except:
            print("get list error")
            response = "error"
        return (response)

    def print_stream_ID(self):
        'format and print in a list the stream name and their ID'
        self.stream_list = []
        self.stream_ID = []
        for i in range(0, len(self.sources_res['Data'])):
            try:
                self.stream_list.append(self.sources_res['Data'][i]["Name"])
                self.stream_ID.append(self.sources_res['Data'][i]["Id"])
                print("Name: ", self.sources_res['Data'][i]["Name"],
                      "Id:", self.sources_res['Data'][i]["Id"])
            except:
                print("error")

    def variable_mapping(self, ID_stream):
        'variable mapping:  inspect how input variables are mapped'
        query = "{\n  variableMapping(sid: \""+ID_stream + \
            "\") {\n    sid\n    columns {\n      name\n      variables {\n        id\n        dataType\n        name\n        unit\n      }\n    }\n  }\n}"
        url_list = self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_map = requests.post(
                url_list, json={'query': query}, headers=header_list)
            self.request_map_res = request_map.json()
        except:
            print("error mapping")
            request_map = "error"
        return(request_map)

    def get_var_mapping(self, request_map_res):
        'return the variable name, unit, index and id. To be called after variable mapping'
        channel_name = []
        channel_unit = []
        channel_index = []
        channel_id = []
        for i in range(0, len(request_map_res['data']['variableMapping']['columns'])):
            try:
                channel_name.append(
                    request_map_res['data']['variableMapping']['columns'][i]['variables'][0]['name'])
                channel_unit.append(
                    request_map_res['data']['variableMapping']['columns'][i]['variables'][0]['unit'])
                channel_index.append(
                    request_map_res['data']['variableMapping']['columns'][i]['name'])
                channel_id.append(
                    request_map_res['data']['variableMapping']['columns'][i]['variables'][0]['id'])
            except:
                print("error variable mapping")
                channel_name.append("error")
                channel_unit.append("error")
                channel_index.append("error")
                channel_idx.append("error")
        return(channel_index, channel_name, channel_unit, channel_id)

    def get_measurement(self, SID, timestamp_start, timestamp_stop):
        'get measurement between time start and time stop'
        query_measurement = "{\n  measurementPeriods(sid: \""+SID+"\",from: "+str(timestamp_start)+",\n \
        to: "+str(timestamp_stop)+") \
        {\n    minTs\n    maxTs\n    mid\n    sampleRate\n  }\n}"
        url_list = self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_measurement = requests.post(
                url_list, json={'query': query_measurement}, headers=header_list)
            self.request_measurement_res = request_measurement.json()
        except:
            print("error get measurement")

    def get_measurement_limit(self, SID, limit):
        'get last measurements'
        query_measurement = "{\n  measurementPeriods(sid: \""+SID+"\",from: 0,\n    to: 9999999999999, limit: "+str(limit)+", sort: DESC) \
        {\n    minTs\n    maxTs\n    mid\n    sampleRate\n  }\n}"
        url_list = self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_measurement = requests.post(
                url_list, json={'query': query_measurement}, headers=header_list)
            self.request_measurement_res = request_measurement.json()
        except:
            print("error get measurement")

    def print_measurement(self, request_measurement_res):
        'format the measurement into a list'
        limit = len(request_measurement_res['data']['measurementPeriods'])
        measurement_list = np.zeros((int(limit), 2))
        for l in range(0, int(limit)):
            #print("start : ",request_measurement_res['data']['measurementPeriods'][l]['minTs'],"stop:",request_measurement_res['data']['measurementPeriods'][l]['maxTs'])
            measurement_list[l,
                             0] = request_measurement_res['data']['measurementPeriods'][l]['minTs']
            measurement_list[l,
                             1] = request_measurement_res['data']['measurementPeriods'][l]['maxTs']
        return(measurement_list)

    def get_data(self, ID_device, index_list, start_import, end_import):
        'old function to get raw data'
        if len(index_list) > 0:
            selected_index_string = ""
            for j in range(0, len(index_list)):
                selected_index_string = selected_index_string + \
                    "\""+index_list[j]+"\""+" ,"
        else:
            print("no variable selected")
        query_data = "{\n  Raw(columns: [\"ts\", \"nanos\","+selected_index_string+"], sid: \"" + \
            ID_device+"\", from: "+start_import+", to: " + \
            end_import+") {\n    data\n  }\n}\n"
        #query_data="{\n  Raw(columns: [\"ts\", \"nanos\", \"a0\", \"a1\"], sid: \""+ID_device+"\", from: "+start_import+", to: "+end_import+") {\n    data\n  }\n}\n"
        #query_data="{\n  Raw(columns: [\"ts\", \"nanos\", \"a1\", \"a0\",], sid: \""+ID_device+"\", from: "+start_import+", to: "+end_import+") {\n    data\n  }\n}\n"

        self.query_data_check = query_data
        url_list = self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_data = requests.post(
                url_list, json={'query': query_data}, headers=header_list)
            self.request_data_res = request_data.json()
            # req_matrix_slb=self.request_data_res['data']['Raw']['data']
        except:
            print("error get data")

    def get_data_interactive(self, ID_device, index_list, start_import, end_import, resolution='nanos'):
        'get data, the type between nanoand and resolution should be enter as a aparameter because they do not have the same structure'
        if resolution == 'nanos':
            if len(index_list) > 0:
                selected_index_string = ""
                for j in range(0, len(index_list)):
                    selected_index_string = selected_index_string + \
                        "\""+index_list[j]+"\""+" ,"
            else:
                print("no variable selected")
            if resolution == 'nanos':
                query_data = "{\n  Raw(columns: [\"ts\", \"nanos\","+selected_index_string+"], sid: \"" + \
                    ID_device+"\", from: "+start_import+", to: " + \
                    end_import+") {\n    data\n  }\n}\n"
        else:
            if len(index_list) > 0:
                selected_index_string = ""
                for j in range(0, len(index_list)):
                    selected_index_string = selected_index_string + \
                        index_list[j]+"{\n      avg\n}"
                # print(selected_index_string)
            else:
                print("no variable selected")

            # srcl# formatted to understand better. Why so many "\n"?
            query_data = "{\n  analytics(from: "+start_import+", \
                to: "+end_import+", \
                resolution: "+resolution+" \
                sid: \""+ID_device+"\") \
                {\n    ts\n    "+selected_index_string+"\n}\n}\n"

        self.query_data_check = query_data
        url_list = self.url+'/__api__/gql'
        header_list = {'Authorization': 'Bearer ' + self.auth_token}
        try:
            request_data = requests.post(
                url_list, json={'query': query_data}, headers=header_list)
            self.request_data_res = request_data.json()
            # req_matrix_slb=self.request_data_res['data']['Raw']['data']
        except:
            print("error get data")

    def filter_data(self, formated_data):
        'old filter obsolete'
        data_matrix = formated_data['data']['Raw']['data']
        # We add the request return into a numpy matrix
        import_data = np.array(data_matrix)
        import_data = import_data.astype(float)
        nonecheck = np.isnan(import_data[:, :])
        none_index = np.where(nonecheck == True)
        if len(none_index[0]) > 0:
            last_none = none_index[0][-1]
            import_data = import_data[last_none+1:-1, :]
        return(import_data)

    def filter_data_interactive(self, formated_data, selected_index, resolution='nanos'):
        'filter data in order to avoid NaN'
        if resolution == 'nanos':
            data_matrix = formated_data['data']['Raw']['data']
            # We add the request return into a numpy matrix
            import_data = np.array(data_matrix)
        else:
            import_data = np.zeros(
                (len(formated_data['data']['analytics']['ts']), len(selected_index)+1))
            import_data[:, 0] = formated_data['data']['analytics']['ts']
            for k in range(0, len(selected_index)):
                import_data[:, k+1] = formated_data['data']['analytics'][selected_index[k]]['avg']

        import_data = import_data.astype(float)
        nonecheck = np.isnan(import_data[:, :])
        none_index = np.where(nonecheck == True)
        if len(none_index[0]) > 0:
            last_none = none_index[0][-1]
            import_data = import_data[last_none+1:-1, :]
        return(import_data)

    def get_remaining_token(self):
        return self.auth_token

    #**************************************
    #           Second Stream
    # This code is hardcoded and the only purpose is the 210107t16 SRCL script,
    # in order to use variables of a second stream - revamp or delete
    #************************************** 