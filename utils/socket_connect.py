import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal

class SocketIDIWorker(QThread):
    response_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, email, host="127.0.0.1", port=9999):
        super().__init__()
        self.email = email
        self.host = host
        self.port = port

    def run(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5.0)
            client.connect((self.host, self.port))

            payload = {
                "action": "REQUEST_IDI_LINK",
                "email": self.email
            }
            client.send(json.dumps(payload).encode("utf-8"))

            raw_response = client.recv(4096).decode("utf-8")
            data = json.loads(raw_response)
            client.close()

            self.response_received.emit(data)
        except socket.timeout:
            self.error_occurred.emit("Request timed out. Socket IDI Server is unreachable.")
        except ConnectionRefusedError:
            self.error_occurred.emit("Connection refused. Is socket_idi_server.py running?")
        except Exception as e:
            self.error_occurred.emit(f"Network Error: {str(e)}")