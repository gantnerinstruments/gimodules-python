import pwd
import string
from CloudConnect import CloudRequest as GINSCloud
import logging
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
    
    def get_variables(self, stream_id):
        
        # write var names into lists
        self.sensor_index, self.sensor_names, self.sensor_units, self.sensor_ids = self.conn_cloud.get_var_mapping(self.conn_cloud.request_map_res)
        
        return self.sensor_ids,self.sensor_names

    
        
    
    

    class GIAuth():
        
        TOKEN = ''
        
        def __init__(self, user, pw, conn_cloud):
            
            conn_cloud.connect_gi_cloud
            
        
        def update_auth_token(self):
            return

        
        
        
        