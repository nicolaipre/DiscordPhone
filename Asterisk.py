import socket

class Asterisk:
    def __init__(self, host="127.0.0.1", port=5038, username="admin", password="admin"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn.connect((self.host, self.port))
        self.conn.recv(29)

    def __del__(self):
        self.conn.close()

    def _recv_response(self, until=b'\r\n\r\n'):
        """ Internal function to receive response after a command is sent
        """
        data = b""
        while until not in data[-len(until):]:
            buf = self.conn.recv(1)
            data += buf
        return data
        
        
    def _login(self):
        """ Login to Asterisk CLI
        """
        login = f"Action: Login\nActionID: 1\nUsername: {self.username}\nSecret: {self.password}\n\n"
        self.conn.send(login.encode())
        resp = self._recv_response()
        self._recv_response()
        self._recv_response()
        return b'Authentication accepted' in resp


    def set_caller_id(self, caller_id):
        """ Update caller ID in extensions.conf
            https://www.voip-info.org/setting-callerid/ <--- nice info om caller id
        """
        self._login()
        update_config = f"""Action: UpdateConfig
Reload: yes
Srcfilename: extensions.conf
Dstfilename: extensions.conf
Action-000000: update
Cat-000000: globals
Var-000000: EXTERNAL_CALLER_ID
Match-000000: 
Value-000000:>{caller_id}\n\n
"""
        self.conn.send(update_config.encode())
        return b'Response: Success' in self._recv_response()
    