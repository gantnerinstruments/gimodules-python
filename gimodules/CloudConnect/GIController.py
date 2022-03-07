from urllib import response
#from CloudConnect import CloudRequest as GINSCloud
from gimodules.CloudConnect import CloudRequest as GINSCloud
from gimodules.CloudConnect import utils
import logging
import uuid
import datetime as dt
from dateutil import tz
import requests
#from gimodules.CloudConnect.CloudRequest import CloudRequest
import httpx
import pandas as pd


# When logging to a file
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

class GIController():
    'This Controller handles and abstracts the requests made to the GICloud'

    conn_cloud = None

    def __init__(self):
        self.conn_cloud = GINSCloud.CloudRequest()

        
        
    def login(self, url, user, pw):
        self.conn_cloud.url = url
        self.conn_cloud.user = user
        self.conn_cloud.PW = pw
        
        #check if valid
        self.conn_cloud.connect_gi_cloud()
        logging.info(f'Connection to {url} established.')
        
        #Fetch sources as json via login
        self.conn_cloud.list_gi_cloud_sources()
        # write stream name and id into lists
        self.conn_cloud.print_stream_ID() # change 
        
        # init httpx
        self.client = httpx.Client(
            base_url=url,
            auth=self.GIAuth(user, pw),
            event_hooks={'response': [self._fix_content_encoding]},
            http2=True)
        
    def get_sources(self):
        self.conn_cloud.list_gi_cloud_sources()
        self.conn_cloud.print_stream_ID()
        logging.info('refreshed streams')
        return
    

    def filter_data(self, **kwargs):
        return
    
    def get_variables(self, stream_id=None, stream_name=None):
        
        # write var names into lists
        if stream_id != None:
            response = self.conn_cloud.variable_mapping(stream_id)
            response.raise_for_status()
            self.sensor_index, self.sensor_names, self.sensor_units, self.sensor_ids = self.conn_cloud.get_var_mapping(response.json())
            self.stream_id = stream_id
        
        #check if only one stream with this name exists else exception
        
        #TODO - check if dict makes more sense
        return self.sensor_ids,self.sensor_names

    def get_timeseries_data(self, sensor_ids, resolution, start=None, end=None):
        
        start = start or dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)
        end = end or dt.datetime.now(dt.timezone.utc)
        
        url_postfix = '/__api__/gql'
        sensor_indices = self._find_sensor_indices(sensor_ids)
        indices_q_string = self._build_sensorid_querystring(sensor_indices)
        
        query = f"""
            {{
                analytics(
                    from: {int(start.timestamp() * 1000)},
                    to: {int(end.timestamp() * 1000)},
                    resolution: {resolution},
                    sid: "{self.stream_id}"
                ) {{
                    ts
                    {indices_q_string}
                }}
            }}
        """
        #response = requests.post(self.conn_cloud.url+url_postfix, json={'query':self.query}, headers={'Authorization': 'Bearer ' + self.conn_cloud.auth_token})
        response = self.client.post(url_postfix, json={'query':query})
        #response.raise_for_status()
        content = response.json()
        return content
    
    def _find_sensor_indices(self, picked_sensor_ids):
        # To build the correct query, the corresponsing index of each variable is needed
        if hasattr(self, 'sensor_ids'):
            indices = []
            for i in picked_sensor_ids:
                indices.append(self.sensor_index[self.sensor_ids.index(i)])
            return indices
        raise ValueError('no such attribute in class.')
        
    
    def _build_sensorid_querystring(self, indices, aggregations=None):
        #TODO
        agg = """
                avg
        """
        print(indices)
        s = ""
        for i in indices:
            s = s+f"""
                {i} {{
                    {agg}
                }}
            """
        print(s)
        return s
    
    def get_data_as_csv(self, columns: dict, resolution, start=None, end=None, decimal_sep='.'):
        
        # columns: field: "stream_id:sensorid" or sensorid
        # headers: ["temperature", "C"]
        start = start or dt.datetime(2021, 2, 28, 10, 0, 0, tzinfo=dt.timezone.utc)
        end = end or dt.datetime.now(dt.timezone.utc)
        
        url_postfix = '/__api__/gql'
        substring = ''
        filename = ''
        for key,value in columns.items():
            if value[1] not in filename:
                filename += value[1]
            concated = '"' +  '","'.join(value) + '"'
            s = f"""{{field: "{key}", headers: [{concated}]}},"""
            substring += s
            
        filename += '_' + start.strftime("%Y%m%d%H%M%S") + '_' + end.strftime("%Y%m%d%H%M%S") + '_' + resolution + '.csv'
        self.query = f"""
            {{
                exportCSV(
                    resolution: {resolution}
                    from: {int(start.timestamp() * 1000)},
                    to: {int(end.timestamp() * 1000)},
                    sid: "{self.stream_id}"
                    timezone: "UTC"
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
        response = self.client.post(url_postfix, json={'query': self.query}, timeout=60)
        response.raise_for_status()
        content = response.content
        # TODO check if chuncked fetching is possible
        csv_file = open(filename, 'wb')
        csv_file.write(content)
        csv_file.close()
        
        # return as df
        return content
    
    def get_raw_data(self, sensor_ids, start=None, end=None):
        # Request: columns: ["ts", "nanos", "a1", "a2" ...]
        # Return: ts: time in ms since epoch - nanos: time in nanos relative to ts
        # This function only applies to measurement queries, since long timespans are timed out
        
        start = start or dt.datetime(2022, 2, 28, 10, 0, 0, tzinfo=dt.timezone.utc)
        end = end or dt.datetime.now(dt.timezone.utc)
        
        url_postfix = '/__api__/gql'
        self.sensor_indices = self._find_sensor_indices(sensor_ids)
        
        indices_string = '"' +  '","'.join(self.sensor_indices) + '"'
        query = f"""
            {{
                Raw(
                    columns: ["ts", "nanos", {indices_string}]
                    from: {int(start.timestamp() * 1000)},
                    to: {int(end.timestamp() * 1000)},
                    sid: "{self.stream_id}"
                ) {{
                    data
                }}
            }}
        """
        
        #timeout = httpx.Timeout(connect_timeout=5, read_timeout=5 * 60, write_timeout=5)
        response = self.client.post(url_postfix, json={'query': query}, timeout=60)
        response.raise_for_status()
        content = response.json()
        return content
    

    def _fix_content_encoding(self, response):
        if 'content-encoding' in response.headers:
            response.headers['content-encoding'] = 'deflate'
            
        
    def get_streamid(self, name):
        
        if self.conn_cloud.stream_list.count(name) == 1:
            return self.conn_cloud.stream_ID[self.conn_cloud.stream_list.index(name)]
        elif self.conn_cloud.stream_list.count(name) > 1:
            raise ValueError('Multiple streams with the same name in list')
        return []
    
    def _generate_stream_write_id(self, stream_id=None):
        
        if stream_id is not None and stream_id in self.conn_cloud.stream_ID:
            return stream_id
        else:
            return str(uuid.uuid4())
    
    def _check_last_stream_ts(self, stream_id):
        write_stream_id = self._generate_stream_write_id(stream_id)
        
        if write_stream_id in self.conn_cloud.stream_ID:
            try:
                last_ts = self.conn_cloud.stream_last_ts[self.conn_cloud.stream_ID.index(stream_id)]
            except Exception as e:
                KeyError(f'check_last_stream_ts: {e}')
        else:
            last_ts = 0
            
        logging.info(f"last ts on stream:{last_ts}")
        return last_ts
    
    def _check_first_csv_ts(self, csv_path, timezone=None):
        try:
            first_lines = pd.read_csv(csv_path,encoding='cp1252',nrows=10,sep=';')#decofing AINSI files on windows or linux
            
            if (self.conn_cloud.DateTimeFmtColumn2 == "" and self.conn_cloud.DateTimeFmtColumn3 == ""):
                read_date=first_lines.iat[self.conn_cloud.ValuesStartRowIndex-1,0]# we read the first measurement line, first coulmn
                read_date = utils.remove_hex_from_string(read_date) # rm cloud exported hex containments
                date_time_obj = dt.datetime.strptime(read_date+";",self.py_formatter+";"+self.conn_cloud.DateTimeFmtColumn2)
            elif self.conn_cloud.DateTimeFmtColumn2 != "":
                read_date=first_lines.iat[self.conn_cloud.ValuesStartRowIndex-1,0]# we read the first measurement line, first coulmn
                read_date = utils.remove_hex_from_string(read_date)
                read_time=first_lines.iat[self.conn_cloud.ValuesStartRowIndex-1,1]# we read the first measurement lin, second coulmn 
                date_time_obj = dt.datetime.strptime(read_date+";"+read_time,self.py_formatter+";"+self.conn_cloud.DateTimeFmtColumn2)
            
            csv_timestamp_utc = date_time_obj.replace(tzinfo=tz.gettz('UTC'))
            csv_timestamp_local = csv_timestamp_utc.astimezone(tz.gettz('Europe / Paris'))
            csv_timestamp=dt.datetime.timestamp(csv_timestamp_local)
            
            timestamp_tmp = dt.datetime.fromtimestamp(csv_timestamp)
            timestamp_tmp = timestamp_tmp.strftime('%Y-%m-%d %H:%M:%S')
        
            logging.info(f"first csv timestamp to import:{csv_timestamp}-{timestamp_tmp}")
            return csv_timestamp
        except (FileNotFoundError) as e:
            logging.error('check_csv_ts: File path is wrong')
        except Exception as e:
            logging.error('Could not read the csv - check the config:', e)
            csv_timestamp=0
        
        
    
    def set_csv_import_configs(self, config: dict, py_formatter=None):
        self.conn_cloud.ColumnSeparator = config.get("ColumnSeparator")
        self.conn_cloud.DecimalSeparator= config.get("DecimalSeparator")
        self.conn_cloud.NameRowIndex= config.get("NameRowIndex")
        self.conn_cloud.UnitRowIndex= config.get("UnitRowIndex")
        self.conn_cloud.ValuesStartRowIndex= config.get("ValuesStartRowIndex")
        self.conn_cloud.ValuesStartColumnIndex=config.get("ValuesStartColumnIndex")

        # Column 1: Date and Time -> specified in Gantner http docs
        # e.g.:
        # 11.10.2019 13:00:00.000000 -> %d.%m.%Y %H:%M:%S.%F
        # 8/14/2010 10:38:00 AM -> %m/%d/%Y %I:%M:%S %p
        self.conn_cloud.DateTimeFmtColumn1= config.get("DateTimeFmtColumn1")
        self.conn_cloud.DateTimeFmtColumn2= config.get("DateTimeFmtColumn2") or ""
        self.conn_cloud.DateTimeFmtColumn3= config.get("DateTimeFmtColumn3") or ""
        
        # Needed if python formatter differs from C++ formatter
        # e.g. "%d.%m.%Y %H:%M:%S.%F" on backend -> "%d.%m.%Y %H:%M:%S.%f" for python
        if py_formatter:
            self.py_formatter = py_formatter
        else:
            self.py_formatter = config.get("DateTimeFmtColumn1")
    
    
    
    def import_csv_in_stream(self, csv_path, stream_name=None):
        import time
        
        self.get_sources()
        
        if stream_name is not None:
                stream_id = self.get_streamid(stream_name)
                if stream_id == []:
                    stream_id = self._generate_stream_write_id(stream_name)
        
        if (utils.is_valid_uuid(stream_id) == False):
            logging.error(f'uuid is wrong{stream_id}; break')
            return
            
        if self._check_first_csv_ts(csv_path) > (self._check_last_stream_ts(stream_id)/1000):
            self.conn_cloud.create_import_session_csv(stream_id, stream_name)
            
            with open(csv_path, 'rb') as f:
                data_upload = f.read()
            
            response = self.conn_cloud.import_file_csv(data_upload)
            response.raise_for_status()
            time.sleep(1)
            self.conn_cloud.delete_import()
        
            #logging.warning('import response:', response.json())
            logging.info('import sucessful')
        else:
            logging.warning('Import failed : first imported csv value  is before the last database timestamp, but must begin after')
            
        #TODO- Return stream name 
    
    class GIAuth(httpx.Auth):
        
        client_id = 'gibench'
        client_secret = ''

        def __init__(self, username, password):
            self.username = username
            self.password = password
            self.token = None

        def auth_flow(self, request):
            if not self.token:
                self.update_token(request)
            request.headers['Authorization'] = self.token
            response = yield request
            if response.status_code == httpx.codes.UNAUTHORIZED:
                self.update_token(request)
                request.headers['Authorization'] = self.token
                yield request

        def update_token(self, request):
            url = request.url.copy_with(path='/token')
            payload = {
                'username': self.username,
                'password': self.password,
                'grant_type': 'password',
            }
            auth = httpx.BasicAuth(self.client_id, self.client_secret)
            response = httpx.post(url, data=payload, auth=auth)
            response.raise_for_status()
            content = response.json()
            self.token = 'Bearer ' + content['access_token']
        
    
