import socket
import sys
import os


class MinFTPClient:

    def __init__(self, server_addr=('127.0.0.1', 1234)):
        self.server_addr = server_addr  # (host, port)
        self.cmd_channel = self.connect_to_server(server_addr)  # Socket for commands
        self.get_welcome()
        self.file_channel = None  # Socket for file transfer
        self.passive = False

    def get_welcome(self):
        welcome = self.get_resp()
        print(welcome)

    def connect_to_server(self, addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(addr)
            print(f'connection to {addr} established.')
            return sock
        except:
            print(f'Error occurred when connecting to {addr}')
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
        """Merge USER and PASS into one cmd LOGIN."""
        cmd = 'LOGIN ' + username + ' ' + password
        self.send_cmd(cmd)
        resp = self.get_resp()
        print(resp)

    def dir(self):
        cmd = 'LIST'
        self.send_cmd(cmd)
        resp = self.get_resp()
        print(resp)
        return resp.split()

    def set_passive(self, passive):
        self.passive = passive

    def make_port(self):
        addr = self.cmd_channel.getsockname()
        sock = socket.socket()
        sock.bind(addr)
        sock.listen(1)
        # Maximum waiting time: 10s.
        sock.settimeout(10)
        cmd = 'PORT ' + addr[0] + ' ' + str(addr[1])
        self.send_cmd(cmd)
        return sock

    def store(self, filename):
        """ Store the content of the openfile to remote directory.

        :param openfile: Opening file object.
        :return: True if success, False otherwise.
        """
        if not os.path.exists(filename):
            print('File does not exist.')
            return False

        with open(filename) as f:
            self.initialize_file_channel()
            if not self.file_channel:
                print('No available file_channel.')
                return False
            cmd = 'STOR ' + filename
            self.send_cmd(cmd)
            data = f.read(4096)
            self.file_channel.sendall(bytes(data, 'utf-8'))
            while data:
                data = f.read(4096)
                self.file_channel.sendall(bytes(data, 'utf-8'))
        return True



    def initialize_file_channel(self):
        """ Establish file_channel according to mode (passive or not).

            If self.passive is False, then open a listen socket for server
            to connect. If self.passive is True, then create another socket
            to connect to server.
        """
        if self.passive:
            cmd = 'PASV'
            self.send_cmd(cmd)
            resp = self.get_resp()
            port = resp.split()
            if len(port) != 1:
                print('Server return illegal port number: ' + repr(port))
                return False
            self.file_channel = self.connect_to_server((self.server_addr[0], int(port[0])))
        else:
            sock = self.make_port()
            try:
                self.file_channel, addr = sock.accept()
            except:
                print('Waiting for connection timeout...')
                return False
            finally:
                sock.close()

    def retr(self, filename, openfile):
        """Retrieve a file from the server."""
        self.initialize_file_channel()
        if not self.file_channel:
            print('No available file_channel.')
            return False
        cmd = 'RETR ' + filename
        self.send_cmd(cmd)
        if openfile:
            data = self.file_channel.recv(4096)
            openfile.write(data)
            while data:
                data = self.file_channel.recv(4096)
                openfile.write(data)
            openfile.close()
            print('Download file successful.')
            return True
        else:
            print('Illegal fileno.')
            return False

    def close(self):
        if self.cmd_channel:
            self.cmd_channel.close()
        if self.file_channel:
            self.file_channel.close()


if __name__ == '__main__':
    client = MinFTPClient()
    client.login('test', 'test')
    client.set_passive(True)
    resp = client.dir()
    client.store('client_test.py')
