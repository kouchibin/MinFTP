import sys
import os
import socket
import types
import socketserver

class MinTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, addr=('127.0.0.1', 12345)):
        super().__init__(addr, CmdHandler)
        self.connections = []       # All connections, (cmd_tunnel, file_tunnel)
        

class CmdHandler(socketserver.StreamRequestHandler):

    def establish_file_tunnel(self, client_address):
        """Establish a new connection dedicated for file transfer.

        By default, the connection is initiated by server. 
        """
        pass

    def handle(self):
        user = self.server.user
        while True:
            msg = self.rfile.readline().strip().decode('utf-8').split()
            cmd = msg[0].upper()
            print(f'Received: {msg}')

            # Handling commands from client
            if cmd == 'USER':
                user.name_verified = (msg[1] == user.name)
                if user.name_verified:
                    self.wfile.write(b'Please enter password.')
                else:
                    self.wfile.write(b'Username incorrect.')
                continue
            elif cmd == 'PASS':
                if not user.name_verified:
                    login_status = b'Username incorrect.'
                else:
                    pass_verified = (msg[1] == user.password)
                    if pass_verified:
                        user.verified = True
                        login_status = b'Login success.'
                        self.establish_file_tunnel(self.client_address)
                    else:
                        login_status = b'password incorrect.'
                self.wfile.write(login_status)
                continue
            elif cmd == 'RETR':
                if not user.verified:
                    status = b'Pleas login.'
                else:
                    status = '\t'.join(os.listdir(user.FTP_directory))
                self.wfile.write(bytes(status + '\n', 'utf-8'))
                continue


if __name__ == '__main__':

    user = types.SimpleNamespace()
    user.name = 'test'
    user.password = 'test'
    user.name_verified = False
    user.verified = False
    user.FTP_directory = '.'

    server = MinTCPServer()
    server.user = user
    server.serve_forever()