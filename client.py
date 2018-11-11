import socket
import sys


class MinFTPClient:

    def __init__(self, server_addr=('127.0.0.1', 1234)):
        self.server_addr = server_addr  # (host, port)
        self.cmd_channel = self.initialize_cmd_channel()  # Socket for commands
        self.file_channel = None  # Socket for file transfer

    def initialize_cmd_channel(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.server_addr)
            print(f'cmd_channel to {self.server_addr} established.')
            welcome = sock.recv(1024)
            print(welcome)
            return sock
        except:
            print('Exception occured during establishment of cmd_channel.')
            sys.exit()

    def send_cmd(self, cmd):
        if cmd[-1] != '\n':
            cmd += '\n'
        success = False
        if self.cmd_channel:
            cmd = cmd.encode('utf-8')
            self.cmd_channel.sendall(cmd)
            return True
        else:
            print('cmd_channel not available.')
            return False

    def get_resp(self):
        resp = self.cmd_channel.recv(1024).decode('utf-8')
        if not resp:
            print('Connection closed.')
        return resp

    def login(self, username, password):
        '''Merge USER and PASS into one cmd LOGIN.'''
        cmd = 'LOGIN ' + username + ' ' + password
        self.send_cmd(cmd)
        resp = self.get_resp()
        print(resp)

    def dir(self):
        cmd = 'LIST'
        self.send_cmd(cmd)
        resp = self.get_resp()
        print(resp)

    def initialize_file_channel(self, sockname):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(sockname)
        listen_socket.listen()
        print('listening on file_channel: ', sockname)
        file_channel, addr = listen_socket.accept()
        print('File channel established. Server addr: ', addr)
        return file_channel


    def close(self):
        if self.cmd_channel:
            self.cmd_channel.close()
        if self.file_channel:
            self.file_channel.close()


if __name__ == '__main__':
    client = MinFTPClient()
    client.login('test', 'test')
    client.dir()
