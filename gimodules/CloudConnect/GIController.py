import pwd
import string
from CloudConnect import CloudRequest as GINSCloud
import logging
import datetime as dt
import requests
#from gimodules.CloudConnect.CloudRequest import CloudRequest
import httpx


# When logging to a file
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

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

        #save sources information
        self.stream_list = self.conn_cloud.stream_list
        self.stream_IDs = self.conn_cloud.stream_ID
        
    def get_sources():
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
        
        return self.sensor_ids,self.sensor_names

    def get_timeseries_data(self, sensor_ids, resolution, start=None, end=None):
        
        start = start or dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)
        end = end or dt.datetime.now(dt.timezone.utc)
        
        url_postfix = '/__api__/gql'
        sensor_indices = self._find_sensor_indices(sensor_ids)
        indices_q_string = self._build_sensorid_querystring(sensor_indices)
        
        self.query = f"""
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
        response = requests.post(self.conn_cloud.url+url_postfix, json={'query':self.query}, headers={'Authorization': 'Bearer ' + self.conn_cloud.auth_token})
        #response.raise_for_status()
        content = response.json()
        return content
    
    def _find_sensor_indices(self, picked_sensor_ids):
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

    def get_csv_export():
        return
    
    def get_raw_data():
        return
    class GIAuth():
        
        TOKEN = ''
        
        def __init__(self, user, pw, conn_cloud):
            
            conn_cloud.connect_gi_cloud
            
        
        def update_auth_token(self):
            return

        
        
        
        