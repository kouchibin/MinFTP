import socket
import sys
import socketserver


class MinFTPClient:

    def __init__(self, server_addr):
        self.server_addr = server_addr                  # (host, port)
        self.cmd_channel = self.initialize_cmd_channel()  # Socket for commands
        self.file_channel = None                         # Socket for file transfer

    def initialize_cmd_channel(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.server_addr)
            print(f'cmd_channel to {self.server_addr} established.')
            return sock
        except:
            print('Exception occured during establishment of cmd_channel.')
            sys.exit()

    def handle_cmd_channel(self):
        cmd = input('MinFTP>')
        instr = cmd.split()[0]
        if (instr.upper() == 'QUIT'):
            self.close()
            sys.exit()
        self.cmd_channel.sendall(bytes(cmd + '\n', 'utf-8'))

        received = self.cmd_channel.recv(1024).decode('utf-8')
        print(f'server: {received}')

    def handle_file_channel(self):
        pass

    def serve(self):
        if not self.cmd_channel:
            print('No cmd_channel availible.')
            sys.exit()
        while True:
            self.handle_cmd_channel()
            self.handle_file_channel()

    def close(self):
        if self.cmd_channel:
            self.cmd_channel.close()
        if self.file_channel:
            self.file_channel.close()

    def initialize_file_channel(self, sockname):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(sockname)
        listen_socket.listen()
        print('listening on file_channel: ', sockname)
        file_channel, addr = listen_socket.accept()
        print('File channel established. Server addr: ', addr)
        return file_channel


if __name__ == '__main__':
    HOST, PORT = '127.0.0.1', 12345
    client = MinFTPClient((HOST, PORT))
    client.serve()
