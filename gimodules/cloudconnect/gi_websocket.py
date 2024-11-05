import os

import websocket
import threading
import json
import logging
from enum import Enum
import ssl
import certifi
from dotenv import load_dotenv
from fontTools.tfmLib import ACCESSABLE

logging.basicConfig(level=logging.INFO)


# Enums translated from TypeScript
class GInsWSWorkerTypes(Enum):
    WSWorkerType_NotSpecified = 0
    WSWorkerType_XmlRpcCall = 1
    WSWorkerType_OnlineData = 2
    WSWorkerType_MessageEvents = 17
    WSWorkerType_SystemState = 15


class GInsWSMessageTypes(Enum):
    WSMsgType_NotSpecified = 0
    WSMsgType_Subscribe = 1
    WSMsgType_Publish = 2
    WSMsgType_Stop = 3
    WSMsgType_Start = 4
    WSMsgType_Reconfigure = 5
    WSMsgType_Destroy = 6
    WSMsgType_Request = 7
    WSMsgType_Response = 8
    WSMsgType_Identify = 9
    WSMsgType_Error = 10
    WSMsgType_End = 11
    WSMsgType_NotRoutable = 12
    WSMsgType_Authentication = 13


class GInsWSWorkerMessageFormat(Enum):
    WSMsgFormat_JSON = 0
    WSMsgFormat_BINARY = 1
    WSMsgFormat_STRING = 2
    WSMsgFormat_UNKNOWN = 3


# Placeholder for ACCESS_TOKEN, LOCAL_URL, WS_LOCATION

LOCAL_URL = "localhost"

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
WS_LOCATION = os.getenv("WS_LOCATION")

# Placeholder classes for types and dependencies
class Worker:
    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, subscriber):
        pass


class SocketService:
    def __init__(self, ws):
        self.ws = ws

    def subscribe(self, worker_type, payload, route=None, worker_add=None):

        message_header = [
            "",  # ClientID
            GInsWSMessageTypes.WSMsgType_Subscribe.value,  # MessageType
            worker_type.value,  # WorkerType
            0,  # WorkerID
            route if route else "",  # Route
        ]
        # Serialize to JSON strings
        message_header_json = json.dumps(message_header)
        payload_json = json.dumps(payload)

        message_content = message_header_json + payload_json

        header_bytes = "\x00\x0e\x00"

        message = header_bytes + message_content.replace(" ", "")
        print(f"Sending message: {message}")
        # Send the message as binary data
        self.ws.send(message, opcode=websocket.ABNF.OPCODE_BINARY)
        return Worker()


    def reconfigure(self, worker, config):
        pass

    def destroy_all(self):
        pass

    def pre_defined_worker_map(self):
        return {}

    def worker_map_by_worker_type(self, worker_type):
        return {}

    def authenticate(self, payload):
        pass


class WSWorkerComponent:

    def get_config(self):
        return {
            "IntervalMS": 1000,
            "AutoStart": True,
            "SystemStateMember": "",
            "IdentMember": "",
            "IdentValue": "",
            "OnlyChangedValues": True,
        }

    def on_receive(self, result):
        logging.info("Received data:")
        logging.info(result)

    def get_route(self):
        return ""

    # Properties
    id = None
    workerType = None


class GInsWebSocket:
    """Singleton"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.ws = None
            self._initialized = True

    def connect(self, url, on_open=None, ssl_context=None):
        self.ws = websocket.WebSocketApp(
            url,
            on_open=on_open,  # Pass the on_open handler here
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        wst = threading.Thread(
            target=self.ws.run_forever, kwargs={"sslopt": {"context": ssl_context}}
        )
        wst.start()
        # Since the connection is asynchronous, we can't return a SocketService here

    def disconnect(self):
        if self.ws:
            self.ws.close()

    def on_message(self, ws, message):
        logging.info("Received message: %s", message)
        pass

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, arg1, arg2):
        print("WebSocket closed")


class WorkerSubscribeResponsePayload:
    def __init__(self):
        self._id = ""
        self.Id = 0
        self.Success = False


class AdditionalInformation:
    def __init__(self):
        self.messageType = None  # GInsWSMessageTypes
        self.messageFormat = None  # GInsWSWorkerMessageFormat


class SubscriberEvents:
    def on_subscribe(self, id, payload, additional_information):
        pass

    def on_receive(self, id, payload, additional_information):
        pass

    def on_error(self, id, payload, additional_information):
        pass

    def on_end(self, id, payload, additional_information):
        pass


class Subscriber:
    def __init__(self, id, events):
        self.id = id
        self.events = events

    def notify(self, message_type, payload, message_format):
        pass


class GInsWSClient:
    GInsWSWorkerTypes = GInsWSWorkerTypes
    GInsWebSocket = GInsWebSocket()
    Subscriber = Subscriber


class GIWebSocket:
    def __init__(self):
        self.ws_client = GInsWSClient
        self.workers = {}
        self.uncreated_workers = []
        self.socket_service = None

    def create_url(self):
        # Implement the logic to create URL
        is_local_test_version = True  # Placeholder
        if is_local_test_version:
            return f"{WS_LOCATION}/ws"
        else:
            protocol = "wss://" if "https" in "https://" else "ws://"
            url = protocol + "10.1.51.66:8090"
            return f"{url}/ws"

    def connect(self, login_required, component):
        instance = self.ws_client.GInsWebSocket
        url = self.create_url()
        if login_required:
            access_token = ACCESS_TOKEN  # Get access token
            url += f"?apitoken={access_token}"
        self.uncreated_workers.append(component)

        # Now, we need to connect
        def on_open(ws):
            self.socket_service = SocketService(ws)  # Implement SocketService
            # Register pre-defined environment worker
            pre_defined_map = self.socket_service.pre_defined_worker_map()
            if pre_defined_map:
                self.create_pre_defined_worker(pre_defined_map)
            for uncreated_worker_component in self.uncreated_workers:
                self.create_worker(uncreated_worker_component)
            self.uncreated_workers = []

            logging.info("Sent formatted initial message to server.")



        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())

        instance.connect(
            url, on_open=on_open, ssl_context=ssl_context
        )  # Pass the on_open handler here
        # instance.connect(url, on_open=on_open)

    def create_pre_defined_worker(self, pre_defined_worker):
        if self.socket_service:
            for worker_type, worker_id_arr in pre_defined_worker.items():
                worker_map = self.socket_service.worker_map_by_worker_type(worker_type)
                for worker_id in worker_id_arr:
                    worker = worker_map.get(worker_id)
                    if worker:
                        subscriber = self.ws_client.Subscriber(
                            1, self.default_worker_subscriber_config(WSWorkerComponent())
                        )
                        worker.add_subscriber(subscriber)

    def disconnect(self):
        self.destroy_worker_all()
        instance = self.ws_client.GInsWebSocket
        instance.disconnect()

    def create_worker(self, component):
        if self.socket_service:
            worker_config = component.get_config()
            route = component.get_route()
            worker = self.socket_service.subscribe(component.workerType, worker_config, route)
            logging.info(
                f"Created worker with ID: {component.id}, WorkerType: {component.workerType.value}, Route: {route}"
            )
            subscriber = self.ws_client.Subscriber(
                component.id, self.default_worker_subscriber_config(component)
            )
            worker.add_subscriber(subscriber)
            self.workers[component.id] = worker
        else:
            self.uncreated_workers.append(component)

    def destroy_worker_all(self):
        if self.socket_service:
            self.socket_service.destroy_all()

    def authenticate(self, access_token):
        if self.socket_service:
            payload = {"AuthToken": access_token}
            self.socket_service.authenticate(payload)

    def default_worker_subscriber_config(self, component):
        events = SubscriberEvents()

        def on_subscribe(id, payload, additional_information):
            pass  # Implement as needed

        def on_receive(id, payload, additional_information):
            component.on_receive(payload)

        def on_error(id, payload, additional_information):
            component.on_receive([])

        def on_end(id, payload, additional_information):
            component.on_receive([])

        events.on_subscribe = on_subscribe
        events.on_receive = on_receive
        events.on_error = on_error
        events.on_end = on_end

        return events


# Example usage
if __name__ == "__main__":
    gi_websocket = GIWebSocket()
    component = WSWorkerComponent()
    component.id = 1
    # component.workerType = GInsWSWorkerTypes.WSWorkerType_OnlineData
    component.workerType = GInsWSWorkerTypes.WSWorkerType_SystemState
    gi_websocket.connect(login_required=True, component=component)

    import time

    while True:
        time.sleep(1)
