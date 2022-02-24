import pwd
import string
from CloudConnect import CloudRequest as GINSCloud
import logging
import httpx




class GIController():
    'This Controller handles and abstracts the requests made to the GICloud'

    conn_cloud = None

    def __init__(self) -> None:
        self.conn_cloud = GINSCloud.CloudRequest()

    def login(self, url, user, pw):
        return 'the'

    def update_token(self):
        return 
    
    

    class GIAuth():
        
        TOKEN = ''
        
        def __init__(self, user, pw):
            self.user = user
            self.pw = pw
            self.token = None
        
        def update_auth_token(self):
            return

        
        
        
        