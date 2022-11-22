
"""
@author: aljo, 
Module to send simplified http request to the Cloud
"""

import csv
from io import BytesIO
import requests
import datetime as dt
import numpy as np
import pandas as pd
import json 
import re
import uuid
import time 
import logging

from dataclasses import dataclass
from typing import Type, List, Dict, Tuple, Optional, Union, Any
from requests.auth import HTTPBasicAuth 
from enum import Enum
from dateutil import tz

from gimodules.cloudconnect import utils

# Set output level to INFO because default is WARNNG
logging.getLogger().setLevel(logging.INFO)

@dataclass
class CsvConfig:
    '''Object for tracking parameters for csv import'''
    # csv config - initialised with default values
    ColumnSeparator: str = ";"
    DecimalSeparator: str= ","
    NameRowIndex: int = 0
    UnitRowIndex: int = 0
    ValuesStartRowIndex: int = 1
    ValuesStartColumnIndex: int = 1
    ## Column 1: Date and Time -> specified in Gantner http docs
    ## Comment one out: if python formatter differs from C++ formatter
    ## e.g. "%d.%m.%Y %H:%M:%S.%F" on backend -> "%d.%m.%Y %H:%M:%S.%f" for python
    DateTimeFmtColumn1: str = "%d.%m.%Y %H:%M:%S.%F"
    DateTimeFmtColumn2: str = ""
    DateTimeFmtColumn3: str = ""
    
    def get_config(self):
        """returns config as dict"""
        return {
            "ColumnSeparator": self.ColumnSeparator,
            "DecimalSeparator": self.DecimalSeparator,
            "NameRowIndex": self.NameRowIndex,
            "UnitRowIndex": self.UnitRowIndex,
            "ValuesStartRowIndex": self.ValuesStartRowIndex,
            "ValuesStartColumnIndex": self.ValuesStartColumnIndex,
            "DateTimeFmtColumn1": self.DateTimeFmtColumn1,
            "DateTimeFmtColumn2": self.DateTimeFmtColumn2,
            "DateTimeFmtColumn3": self.DateTimeFmtColumn3
        }

@dataclass()
class GIStreamVariable: 
    '''Object for tracking available variables'''
    id: str
    name: str
    index: str
    unit: str
    data_type: str
    sid: str
        
class CloudRequest():
    
    def __init__ (self):
        self.url = ""
        self.user = ""
        self.pw = ""
        self.login_token = None
        self.refresh_token = None
        self.streams = None
        self.stream_variabels = None
        self.query = ""
        self.request_measurement_res = None

        # enums 
        self.resolutions = Resolution 
        self.units = None

        # importer data
        self.import_session_res_udbf = None
        self.import_session_res_csv = None
        self.import_session_csv_current = None
        self.session_ID = None
        self.csv_config = CsvConfig()


    def login(self, url:str, user:str, password:str):

        self.url = url 
        self.user = user 
        self.pw = password

        # prepare request
        login_form = { 'username': self.user, 'password': self.pw, 'grant_type': 'password' }
        auth = HTTPBasicAuth('gibench', '')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        login_url = self.url + '/token'

        # send request
        try:
            res = requests.post(login_url, data = login_form, headers = headers, auth = auth)
            if res.status_code == 200:
                self.login_token = res.json()
                self.refresh_token = self.login_token['refresh_token']
                logging.info("Login successful")
                self.get_all_stream_metadata()
                self.print_streams()
                self.get_all_var_metadata()
            else: 
                logging.error(f"Login failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as e:
            logging.warning(e)
    
    def refresh_access_token(self): 
        """
        Refresh the access token with a refresh token. 
        The refresh token is valid for 14 days. 
        """
        # prepare request
        refresh_form = json.dumps({ 'ClientID': 'gibench', 'RefreshToken': self.refresh_token })
        headers = {'Content-Type': 'application/json'}
        refresh_url = self.url + '/rpc/AdminAPI.RefreshToken'
        
        # send request
        try: 
            res = requests.post(refresh_url, data = refresh_form, headers= headers)
            if res.status_code == 200:
                res = res.json()
                res['access_token'] = res.pop('AccessToken')
                self.login_token = res
                logging.info("Access Token refreshed")
            else: 
                logging.error(f"Could not fetch access token with refresh token\nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as e:
            logging.warning(e)
            
        
    def get_all_stream_metadata(self): 
        """Loads the available meta information from all available streams. 
        The data is stored in data classes (GIStream) and is accessible via the .streams attribute. 
        """
        # check that auth_token exist
        if self.login_token is not None: 
            # prepare request
            url_list = self.url + '/kafka/structure/sources'
            headers = {'Authorization': 'Bearer ' + self.login_token['access_token']}
            # send request
            try: 
                res = requests.get(url_list, headers=headers)
                if res.status_code == 200: 
                    res = res.json()
                    self.streams = {} # reset memory 
                    for i in range(0, len(res['Data'])):
                        name = res['Data'][i]["Name"]
                        id = res['Data'][i]["Id"]
                        sample_rate_hz = res['Data'][i]["SampleRateHz"]
                        first_ts = res['Data'][i]["AbsoluteStart"]
                        last_ts = res['Data'][i]["LastTimeStamp"]
                        index = res['Data'][i]["Index"]
                        # store data in dict with dataclass
                        self.streams[name] = GIStream(name, id, sample_rate_hz, first_ts, last_ts, index)
                elif res.status_code == 401 or res.status_code == 403: 
                    self.refresh_access_token()
                    self.get_all_stream_metadata()
                else: 
                    logging.error(f"failed! \nResponse Code: {res.status_code} \nReason: {res.reason}")
            except Exception as e:
                logging.warning(e)
        else: 
            logging.error("You have no valid access token! \nPlease login first.")

    def print_streams(self):
        if self.streams is not None:
            for s in self.streams: 
                logging.info(f"{'Streamname:':<20}{self.streams[s].name} \
                        \n{'Streamid:':<20}{self.streams[s].id} \
                        \n{'first ts:':<20}{self.streams[s].first_ts} {dt.datetime.utcfromtimestamp(float(self.streams[s].first_ts)/1000).strftime('%Y-%m-%d %H:%M:%S')} \
                        \n{'last ts:':<20}{self.streams[s].last_ts} {dt.datetime.utcfromtimestamp(float(self.streams[s].last_ts)/1000).strftime('%Y-%m-%d %H:%M:%S')} \
                        \n{'Samplerate:':<20}{self.streams[s].sample_rate_hz}\n")
        else: 
            logging.info("You have no loaded Streams")

    def get_all_var_metadata(self):
        """Loads the available meta information from all available variable. The data is stored in data classes and is accessible via the .stream_variabels attribute. 
        """

        if self.streams is not None: 
            url_list=self.url+'/__api__/gql'
            headers = {'Authorization': 'Bearer ' + self.login_token["access_token"]}
            self.stream_variabels = {} # reset memory
            unit_names = []
            for s in self.streams:
                query="{\n  variableMapping(sid: \""+ self.streams[s].id +"\") {\n    sid\n    columns {\n      name\n      variables {\n        id\n        dataType\n        name\n        unit\n      }\n    }\n  }\n}"
                try:
                    res = requests.post(url_list, json = {'query': query}, headers = headers)
                    if res.status_code == 200: 
                        res = res.json()
                        for i in range(0, len(res['data']['variableMapping']['columns'])):
                            sid = res['data']['variableMapping']['sid']     
                            index = res['data']['variableMapping']['columns'][i]['name'] # Var index in GI System - needed for gql queries
                            name = res['data']['variableMapping']['columns'][i]['variables'][0]['name'] # Var name defined by user
                            data_type = res['data']['variableMapping']['columns'][i]['variables'][0]['dataType']
                            id = res['data']['variableMapping']['columns'][i]['variables'][0]['id']
                            unit = res['data']['variableMapping']['columns'][i]['variables'][0]['unit']

                            # create Enum for filtering units
                            if unit not in unit_names and unit != "": 
                                unit_names.append(unit)
                            # Create unique variable name /with stream
                            # TODO - if multiple variables with same name exists (in one stream) the name will be overwritten
                            self.stream_variabels[f"{s}__{name}"] = GIStreamVariable(id, name, index, unit, data_type, sid)
                    elif res.status_code == 401 or res.status_code == 403: 
                        self.refresh_access_token()
                        self.get_all_var_metadata()
                    else: 
                        logging.error(f"Fetching variable info failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
                except Exception as e:
                    logging.warning(e)
            # create Enum for available units
            self.units = Enum('Units', list(unit_names))
        else: 
            logging.info("You have no loaded Streams. \nPlease load first Streams.")

    def variable_info(self):
        '''use this endpoint to read information for all available online variables'''
        url_list = self.url + '/online/structure/variables'
        headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.get(url_list, headers = headers)
            if res.status_code == 200: 
                res = res.json()
                ## TODO continue here
            else: 
                logging.error(f"Fetching variable info failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as e:
            logging.warning(e)
            
    def find_var(self, var_name: str): 
        """Searches the existing variables. 

        Args:
            var_name (str): Var_name or Substring

        Returns:
            Dict ([str,GIStreamVariable]): List of variables found
        """

        if type(var_name) == list: 
            match = []  
            for k in self.stream_variabels.keys():
                for vr in var_name: #TODO Aviod Big O notation
                    if vr in k: 
                        match.append(k)
        else: 
            match = [x for x in self.stream_variabels.keys() if var_name in x]

        if len(match) == 0 and match is not None: 
            logging.info("No var found.")
        else:
            result = {}  
            for m in match:
                result[m] = (self.stream_variabels[m])
            return result
        return None

    def filter_var_attr(self, attr: str, value: str): 
        """
        Search for stream_variables with a certain attribute

        Args:
            attr (str): e.g. unit
            value (str): e.g. C°

        Returns:
            dataclass (obj): List of variables found
        """

        if self.stream_variabels is not None: 
            match = [x for x in self.stream_variabels.values() if getattr(x, attr, "") == value]
            return match
        return None
    
    def _build_sensorid_querystring(self, indices:List, aggregations=None):
        #TODO - enable multiple aggregations
        agg = """
                avg
        """
        s = ""
        for i in indices:
            s = s+f"""
                {i} {{
                    {agg}
                }}
            """
        return s

    def get_var_data(self, sid:str, index_list:List, start_date:str, end_date:str, resolution:str = 'nanos'):
        """Returns a np.matrix of data and pandas df with timestamps and values directly from a data stream

        Args:
            sid (str): stream_id
            index_list (list): channel_index e.g. ["a10", "a11"]
            start_date (str): format: YYYY-MM-DD HH:MM:SS
            end_date (str): format: YYYY-MM-DD HH:MM:SS
            resolution (str, optional): 'MONTH','WEEK','DAY','HOUR','QUARTER_HOUR','MINUTE','SECOND','HZ10','HZ100','KHZ','KHZ10','nanos'
                The available resolutions are accessible via the attribute ".resolutions". 
                Do not forget at the end the .values  Defaults to 'nanos'.

        Returns:
            pandas.df: dataframe
        """

        tss = str(self.convert_datetime_to_unix(start_date))
        tse = str(self.convert_datetime_to_unix(end_date))

        selected_index_string="" 
        if resolution=='nanos' and len(index_list) > 0: # nanos == raw data
            for j in range(0,len(index_list)): # concat var_index for query
                selected_index_string = selected_index_string + "\"" + index_list[j] + "\"" + " ,"
            # build query 
            
            self.query ="{\n  Raw(columns: [\"ts\", \"nanos\"," + selected_index_string + "], \
                sid: \"" + sid + "\",\
                from: " + tss + ",\
                to: " + tse + ") {\n    data\n  }\n}\n"             
        
        elif len(index_list) > 0:
            selected_index_string = self._build_sensorid_querystring(index_list)

            self.query = f"""
            {{
                analytics(
                    from: {tss},
                    to: {tse},
                    resolution: {resolution},
                    sid: "{sid}"
                ) {{
                    ts
                    {selected_index_string}
                }}
            }}
        """
        else:
            logging.info("no variable selected")

        url_list = self.url+'/__api__/gql'
        headers = {'Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list, json={'query':self.query}, headers = headers)
            if res.status_code == 200 and not "errors" in res.text: 
                requested_data = res.json()

                ### Filter Data out of request
                if resolution=='nanos':
                    data_matrix=requested_data['data']['Raw']['data']
                    self.data=np.array(data_matrix)
                else:
                    self.data=np.zeros((len(requested_data['data']['analytics']['ts']),len(index_list)+1))
                    self.data[:,0]=requested_data['data']['analytics']['ts']
                    for k in range(0,len(index_list)):
                        self.data[:,k+1]=requested_data['data']['analytics'][index_list[k]]['avg']
                
                ### create numpy matrix 
                self.data=self.data.astype(float)
                nonecheck=np.isnan(self.data[:,:])
                none_index=np.where(nonecheck == True)

                #none number can be at the begining or at the end.
                if len(none_index[0])>0:
                    first_none=none_index[0][0]
                    last_none=none_index[0][-1]
                    if last_none==len(self.data)-1:
                        self.data=self.data[0:first_none-1,:]
                    else:    
                        self.data=self.data[last_none+1:-1,:]

                ### create pandas df
                self.df = pd.DataFrame(self.data, columns=self.__get_column_names(sid, index_list))
                self.df['Time'] = pd.to_datetime(self.df['Time'], unit='ms')
                return self.df 
            elif res.status_code == 401 or res.status_code == 403:
                logging.info("Token expired. Renewing...")
                self.refresh_access_token()
                return self.get_var_data(sid, index_list, start_date, end_date, resolution)
            # Show error Message from Server
            else: 
                error = json.loads(res.text)
                logging.error(f"Fetching Data failed! \nResponse Code: {res.status_code} \nReason: {res.reason}\nMsg: {error['errors'][0]['message']}")
        except Exception as e:
            logging.warning(e)
    
    def _get_stream_name_for_sid_vid(self, sid:str, vid:str):
        if self.stream_variabels != None:
            stream = [k for k, v in self.stream_variabels.items() if (v.sid == sid and v.id == vid)]
            if len(stream) == 1:
                return stream[0].split('__')[0]
        else: 
            logging.info("no stream_variables available")
            return None
        
    def _get_stream_name_for_sid(self, sid:str):
        if self.stream_variabels != None:
            stream = [stream_name for stream_name,gi_stream in self.streams.items() if gi_stream.id == sid]
            if len(stream) == 1:
                return stream[0]
        else: 
            logging.info("no stream_variables available")
            return None
    
    def get_all_vars_of_stream(self, sid:str):
        if self.stream_variabels != None:
            variables = [v for v in self.stream_variabels.values() if v.sid == sid]
            return variables
        else: 
            logging.info("no stream_variables available")
            return None
        
    def get_data_as_csv(self, variables: List[GIStreamVariable], resolution: str, start: str, end: str, filepath: str='', streaming: bool = True, return_df: bool= True, write_file: bool= True,decimal_sep: str='.', delimiter: str=';', timezone: str='UTC', aggregation: str='avg'):
        """Returns a csv file with the data of a given list of variables
        """
        # columns: field: "stream_id:sensorid" or sensorid
        # headers: ["temperature", "C"]
        
        substring = ''
        filename = ''
        streams = set()
        for var in variables:
            stream = self._get_stream_name_for_sid_vid(var.sid, var.id)
            streams.add(stream)
            s = f"""{{field: "{var.sid}:{var.index}.{aggregation}", 
            headers: ["{var.name}","{stream}","{aggregation}", "{var.unit or ""}"]}},"""
            substring += s
            
        filename += '_'.join(streams) + '_' + start + '_' + end + '_' + resolution + '_' + aggregation + '.csv'
        start = str(self.convert_datetime_to_unix(start))
        end = str(self.convert_datetime_to_unix(end))
        self.query = f"""
            {{
                exportCSV(
                    resolution: {resolution}
                    from: {start},
                    to: {end},
                    timezone: "{timezone}",
                    filename: "{filename}"
                    columns: [
                        {{
                            field: "ts",
                            headers: ["datetime"],
                            dateFormat: "%Y-%m-%dT%H:%M:%S"
                        }},
                        {{
                            field: "ts",
                            headers: ["time","","","[s since 01.01.1970]"]
                        }},
                        {substring}
                    ]
                ) {{
                    file
                }}
            }}
        """
        url_list = self.url+'/__api__/gql'
        headers = {'Authorization': 'Bearer ' + self.login_token["access_token"]}
        res = requests.post(url_list, json={'query':self.query}, headers = headers, stream=streaming)
        if res.status_code == 200 and not "errors" in res.text: 
            
            if write_file:
                csv_file = open(filepath + filename, 'wb')
                if stream == False:
                    content = res.content
                    csv_file.write(content)
                    csv_file.close()
                else:
                    for chunk in res.iter_content(chunk_size=1024):
                        csv_file.write(chunk)
                        csv_file.flush()
                    if return_df == False:
                        csv_file.close()
                        
            
            # return as df
            # TODO set columns to specific dtypes (more performance and pandas dynamic checking is buggy)
            if return_df == True and stream==False or write_file==False:
                return pd.read_csv(BytesIO(res.content), delimiter=delimiter)
            elif return_df == True:
                return pd.read_csv(filepath + filename, delimiter=delimiter)
        else:
            error = json.loads(res.text)
            logging.error(f"Fetching csv Data failed! \nResponse Code: {res.status_code} \nReason: {res.reason}\nMsg: {error['errors'][0]['message']}")
            
    
    def __get_column_names(self, sid:str, index_list:List): 
        """
        private helper method to get the column names for df
        Args:
            sid (str): Stream Id
            index_list (list): List of variable indices e.g. "a10"

        Returns:
            _type_: _description_
        """
        col_names = ["Time"]
        res = self.filter_var_attr("sid", sid)
        if res != None:
            for i in index_list: 
                for x in res:
                    if x.index == i:
                        col_names.append(x.name)
            return col_names
        return None 

    @staticmethod
    def convert_datetime_to_unix(datetime:str):
        """staticmethod for converting timestamps to UTC

        Args:
            datetime (str): required date format '%Y-%m-%d %H:%M:%S'

        Returns:
            int: UNIX timestamp
        """
        try: 
            date_time_obj = dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S')
            timestamp_utc = date_time_obj.replace(tzinfo=tz.gettz('UTC'))
            timestamp_local = timestamp_utc.astimezone(tz.gettz('Europe / Paris'))
            timestamp= int(dt.datetime.timestamp(timestamp_local)) * 1000 
            return timestamp
        except Exception as err:
            logging.error("Fehler beim konvertieren des Zeitstempels:", dt.datetime.now, err)

    def get_measurement_limit(self, sid:str, limit:str): 
        """
             'get measurement between time start and time stop'

        Args:
            sid (str): Stream Id
            limit (str): 
        """
        query_measurement="{\n  measurementPeriods(sid: \"" + sid + "\",from: 0,\n    to: 9999999999999, limit: "+str(limit)+", sort: DESC) \
        {\n    minTs\n    maxTs\n    mid\n    sampleRate\n  }\n}"
        url_list=self.url+'/__api__/gql'
        headers = {'Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list, json = {'query':query_measurement}, headers = headers)
            if res.status_code == 200: 
                self.request_measurement_res = res.json()
            else: 
                logging.error(f"Fetching variable info failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as err:
            logging.warning(err)

    def print_measurement(self): # TODO test function
        limit = len(self.request_measurement_res['data']['measurementPeriods'])
        measurement_list = np.zeros((int(limit),2))
        for l in range(0,int(limit)):
        #print("start : ",request_measurement_res['data']['measurementPeriods'][l]['minTs'],"stop:",request_measurement_res['data']['measurementPeriods'][l]['maxTs'])
            measurement_list[l,0] = self.request_measurement_res['data']['measurementPeriods'][l]['minTs']
            measurement_list[l,1] = self.request_measurement_res['data']['measurementPeriods'][l]['maxTs']
        return(measurement_list)
        
    #### ubdf importer 
    def create_import_session_udbf(self, sid:str, stream_name:str):
        """ 
        method to import udbf file with http API

        Args:
            sid (str): _description_
            stream_name (str): _description_

        Returns:
            _type_: _description_
        """

        url_list = self.url + '/history/data/import'
        param = {"Type":"udbf",
                "SourceID": sid ,
                "SourceName": stream_name ,
                "MeasID":"",
                "SessionTimeoutSec":"300",
                "AddTimeSeries":"false",
                "SampleRate":"-1",
                "AutoCreateMetaData":"true"
                }
        headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list,headers=headers,json=param)
            if res.status_code == 200: 
                self.import_session_res_udbf=res.json()
            else:   
                logging.error(f"Creating import session failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as err:
            logging.error(f"create_import_session failed:{err}")
            res="error"
        return (res)
    
    def import_file_udbf(self, file):
        """method to import udb file with http API

        Args:
            file (udbf): GI specific file format 

        Returns:
            http obj:  Server response 
        """

        self.session_ID = str(self.import_session_res_udbf['Data']['SessionID'])
        url_list = self.url +'/history/data/import/' + self.session_ID
        header_list = {'Content-Type':'application/octet-stream','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list,headers=header_list,data=file)
            if res.status_code == 200: 
                logging.info("ubdf succesfully imported")
            else:   
                logging.error(f"Import failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as err:
            logging.error(f"import udbf failed:{err}")
            res = "error"
        return (res)  
        
    #### csv importer 
    def create_import_session_csv(self, stream_ID:str, stream_Name:str, csv_config: CsvConfig, create_meta_data:bool = True, session_timeout:int = 60):
        """method to import csv file with http API

        Args:
            stream_ID (str): stream id
            stream_Name (str): buffername for new stream

        Returns:
            http obj:  Server response 
        """
        
        url_list = self.url+'/history/data/import'
        param = { "Type":"csv",
                "SourceID":stream_ID,
                "SourceName":stream_Name,
                "MeasID":"",
                "SessionTimeoutSec":str(session_timeout),
                "AddTimeSeries":"false",
                "SampleRate":"-1",
                "AutoCreateMetaData": str(create_meta_data).lower(),
                "CSVSettings": csv_config.get_config()
                }

        headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            print(param)
            res = requests.post(url_list, headers = headers, json = param)
            if res.status_code == 200: 
                self.import_session_res_csv = res.json()
                self.import_session_csv_current = {'stream_id': stream_ID, 'ts': time.time(), 'timeout': session_timeout}
            else:   
                logging.err(f"Creating import session failed! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as e:
            logging.error(f"create_import_session failed:{e}")
            res = "error"
        return (res)

    def __import_file_csv(self, file):
        """method to import csv file with http API

        Args:
            file (csv): csv file for upload

        Returns:
            http obj:  Server response 
        """

        self.session_ID = str(self.import_session_res_csv['Data']['SessionID'])
        url_list = self.url + '/history/data/import/' + self.session_ID
        headers = {'Content-Type':'text/csv','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list, headers = headers, data = file)
        except Exception as e:
            logging.error("import csv failed ,code:{}".format(res.status_code))
            res = "error"
        return (res)

    def upload_csv_file(self, stream_name:str, file_path:str, py_formatter: str = None, csv_config: any = None): 
        """this method performs preparatory functions for csv import

        Args:
            stream_name (str): 
            file_path (str):
        """
        #**************************************
        #    read und check csv file
        #**************************************
        try:
            # py_formatter is delivered if python parses dates differently than c++ (backend parsing)
            # e.g. py_formatterClmn1 = "%d.%m.%Y %H:%M:%S.%f" for python, while DateTimeFmtColumn1: str = "%d.%m.%Y %H:%M:%S.%F" for API config
            if py_formatter == None:
                py_formatterClmn1 = self.DateTimeFmtColumn1
    
            first_lines = pd.read_csv (file_path, encoding = 'utf-8', nrows = 10, sep = ';') #decofing AINSI files on windows or linux
            read_date = first_lines.iat[self.ValuesStartRowIndex-1, 0] # we read the first measurement line, first coulmn
            read_date = Helpers.remove_hex_from_string(read_date) # rm cloud exported hex containments

            if (self.DateTimeFmtColumn2 == "" and self.DateTimeFmtColumn3 == ""):
                date_time_obj = dt.datetime.strptime(read_date+";",py_formatterClmn1+";"+self.DateTimeFmtColumn2)
            elif self.DateTimeFmtColumn2 != "":
                read_time=first_lines.iat[self.ValuesStartRowIndex-1,1]     # we read the first measurement lin, second coulmn 
                date_time_obj = dt.datetime.strptime(read_date+";"+read_time,py_formatterClmn1+";"+self.DateTimeFmtColumn2)
            
            #handle timestamp
            csv_timestamp_utc = date_time_obj.replace(tzinfo=tz.gettz('UTC'))
            csv_timestamp_local = csv_timestamp_utc.astimezone(tz.gettz('Europe / Paris'))
            csv_timestamp = dt.datetime.timestamp(csv_timestamp_local)
        except (FileNotFoundError) as e:
            logging.error('File path of csv to import is wrong.')
        except Exception as e:
            logging.error('Could not read the csv - check the config:', e)
            csv_timestamp=0

        timestamp_tmp = dt.datetime.fromtimestamp(csv_timestamp)
        timestamp_tmp.strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"First csv timestamp {csv_timestamp,timestamp_tmp.strftime('%d.%m.%Y %H:%M:%S')}")


        #**************************************
        #    check if stream exists
        #**************************************
        if stream_name in self.streams:
            write_ID = stream_name[stream_name].id
            reprise = 1# in this case reprise =1
            logging.info("Stream already existing in GI.Cloud import will be continued - {}".format(write_ID))
        else:
            write_ID=str(uuid.uuid4())
            reprise = 0# in this case reprise =1
            logging.info("Stream not existing in GI.Cloud import will be initialised - {}".format(write_ID))
            
        if (utils.is_valid_uuid(write_ID) == False):
            logging.error(f'uuid is wrong{write_ID}; break')
            return
        
        #**************************************
        #            check last imported timestamps
        #**************************************
        if reprise == 1:
            try:
                last_timestamp = self.streams[stream_name].last_ts
                timestamp_end_s = dt.datetime.utcfromtimestamp(last_timestamp/1000)
                print("last utc imported timestamp: {}".format((last_timestamp/1000),timestamp_end_s.strftime('%Y-%m-%d %H:%M:%S')))
            except:
                print("probably no stream existing")
        else:
            last_timestamp = 0
            print("stream_empty timestamp:".format(last_timestamp))

        #**************************************
        #           Upload file
        #**************************************
        if csv_config == None: 
            csv_config = self.csv_config
        if csv_timestamp > last_timestamp / 1000:
            # reuse import session if possible
            if not self.__import_session_valid(write_ID):
                self.create_import_session_csv(write_ID, stream_name, csv_config)
            with open(file_path, 'rb') as f:
                data_upload = f.read()

            response = self.__import_file_csv(data_upload)
            #time.sleep(5)

            if response.status_code == 200:
                logging.info(f"import of {file_path} was successful")
                return write_ID
            else:   
                logging.error(f"Import failed! \nResponse Code:{response.status_code} \nReason: {response.reason}")
                
            
            # free up resources 
            #self.delete_import()
        else:
            logging.error("Import failed : first imported csv value  is before the last database timestamp, but must begin after")
        return None
    
    def __import_session_valid(self, stream_id):
        if self.import_session_csv_current == None:
            return False
        elif self.import_session_csv_current['stream_id'] == stream_id and \
            (self.import_session_csv_current['ts'] - time.time()) +5 < self.import_session_csv_current['timeout']:
            return True
        
    def delete_import_session(self):
        """
         method to delete session http API

        Returns:
             http obj:  Server response 
        """
       
        url_list = self.url +'/history/data/import/' + self.session_ID
        headers = {'Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.delete(url_list, headers = headers)
            if res.status_code == 200: 
                logging.info("Import session is closed")
            else:   
                logging.error(f"Failed closing import session! \nResponse Code:{res.status_code} \nReason: {res.reason}")
        except Exception as e:
            logging.error(f"delete failed: {e}")
            res="error"
        return (res)

    ################# Read and Write Single Values out of live datastreams
    ############### notice postprocessed data do not work with this functions 

    def read_value(self, var_ids:List): 
        """read online value, enter a list of variable IDs
        Args:
            var_ids (list): #For example var_ids=["47f32894-c6a0-11ea-81a1-02420a000368"]

        Returns:
            list: current live value
        """

        url_list = self.url + '/online/data'
        param = {"Variables":var_ids,"Function":"read"}
        headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list, headers = headers, json = param)
            if res.status_code == 200: 
                current_live_value = res.json()
                logging.info(f"Current live Value: {current_live_value}")
                return current_live_value
            else:
                logging.error(f"failed! \nResponse Code:{res.status_code} \nReason: {res.reason}") 
        except Exception as e:
            logging.error(e)
        return None

    def write_value_on_channel(self, var_ids:List, write_list:List):
        """ read online value, enter a list of variable IDs
        Args:
            var_ids (list): #For example var_ids=["47f32894-c6a0-11ea-81a1-02420a000368"]
            write_list (list): #For example write_list=["0"]

        Returns:
            http obj:  Server response 
        """

        url_list = self.url + '/online/data'
        param = {"Variables":var_ids, "Values": write_list ,"Function":"write"}
        headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + self.login_token["access_token"]}
        try:
            res = requests.post(url_list, headers = headers, json = param)
            if res.status_code == 200: 
                write_value_res=res.json() 
                logging.info("Data Successfully written")
                return write_value_res
            else:
                logging.error(f"failed! \nResponse Code:{res.status_code} \nReason: {res.reason}") 
        except Exception as e:
            logging.error(e)
        return None
    
    def get_gistreamvariables(self, stream: str, variables: List) -> List:
        """Give GIStreamVariable for according stream and variable name"""
        gi_vars = []
        for var in variables:
            gi_vars.append(list(self.find_var(stream + '__' + var).values())[0])
        return gi_vars

class Helpers():
    @staticmethod 
    def remove_hex_from_string(str):
        """Remove hex value from input string"""
        return re.sub(r'[^\x00-\x7f]',r'', str)

class Resolution(Enum):
    MONTH = 'MONTH'
    WEEK = 'WEEK'
    DAY = 'DAY'
    HOUR = 'HOUR'
    QUARTER_HOUR = 'QUARTER_HOUR'
    MINUTE = 'MINUTE'
    SECOND = 'SECOND'
    HZ10 = 'HZ10'
    HZ100 = 'HZ100'
    KHZ = 'KHZ'
    KHZ10 = 'KHZ10'
    NANOS = 'nanos'

@dataclass()
class GIStream:
    '''Object for tracking available streams''' 
    name: str
    id: str
    sample_rate_hz: str
    first_ts: int
    last_ts: int
    index: int


