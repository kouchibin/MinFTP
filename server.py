import os
import types
import socketserver


class MinTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, addr=('127.0.0.1', 1234)):
        super().__init__(addr, CmdHandler)
        self.welcome_msg = '************Welcome***********'


class CmdHandler(socketserver.StreamRequestHandler):

    def send_resp(self, msg):
        msg = bytes(msg + '\n', 'utf-8')
        self.wfile.write(msg)

    def dispatch_request(self):
        msg = self.rfile.readline().strip().decode('utf-8')
        if not msg:
            print('Connection closed.')
            self.done = True
            return
        print("received: " + msg)
        msg = msg.split()
        if msg[0] == 'LOGIN':
            self.login(msg[1:])
            return
        elif self.user_verified:
            if msg[0] == 'LIST':
                self.dir()
        else:
            self.send_resp('Please Login.')

    def dir(self):
        list = '\t'.join(os.listdir(user.FTP_directory))
        self.send_resp(list)

    def login(self, credential):
        print(credential)
        if len(credential) != 2:
            self.send_resp('Illegal parameters.')
        username, password = tuple(credential)
        if username == self.user.name and password == self.user.password:
            self.user_verified = True
            self.send_resp('Login success!')
        else:
            self.send_resp('Invalid username or password.')

    def handle(self):
        self.user_verified = False
        self.user = self.server.user
        self.done = False
        self.send_resp(self.server.welcome_msg)
        while not self.done:
            self.dispatch_request()


if __name__ == '__main__':

    user = types.SimpleNamespace()
    user.name = 'test'
    user.password = 'test'
    user.FTP_directory = '.'

    server = MinTCPServer()
    server.user = user
    server.serve_forever()
