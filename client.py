# client.py  
import socket
import struct

class ftpClient:
    def __init__(self):
        self.serverClient = None
    
    def openConnection(self, host, port):
        """
        :param host:       host name to connect to
        :param port:       TCP port to connect to
        """
        # create a socket object
        self.serverClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        try:
            # connection to host on the port.
            self.serverClient.connect((host, port))  
        except Exception as e:
            print("connecting to %s:%u failed %s, please try again" % (host, port, e))
            self.serverClient = None

    def cmdConnection(self):
        while True:
            try:
                temp = input("Enter host and port of server (e.g. localhost:9999) > ").strip()                             
                host, port = temp.split(':')
                self.openConnection(host, int(port))
                return
            except ValueError:
                print('Invalid host:port "%s", please try again' % temp)

    def send(self, cmd):
        self.serverClient.sendall(cmd.encode())

    def socketReadSize(self, size):
        buf = bytes()
        while size > 0:
            data = self.serverClient.recv(size)
            if data == '':
                raise RuntimeError('read unexpected data')
            buf += data
            size -= len(data)
        return buf
        
    def recvLenData(self):
        temp = self.socketReadSize(4)
        len = struct.unpack('!I', temp)[0]
        data = self.socketReadSize(len)
        str = data.decode('utf-8')
        print(str)

    def cmdList(self):
        self.send('LIST')
        self.recvLenData()

    def requestLoop(self):
        while True:
            # "prompt user for operation" state
            cmd = input("Enter cmd > ").strip()                             

            if cmd.upper() == 'HELP':
                print("Client help options are help");
                continue
            elif cmd.upper() == 'CONN':
                self.cmdConnection()
                continue
            elif cmd.upper() == 'LIST':
                self.cmdList()
                continue
            elif cmd.upper() == 'QUIT':
                exit(0);
             
            if self.serverClient is None:
                print("No connection to a server, you must connect (using CONN) first")
                continue
                
            self.serverClient.sendall(cmd.encode())

            # Receive no more than 1024 bytes
            data = self.serverClient.recv(1024)                                     
            if not data: break    
            stringdata = data.decode('utf-8')
            print("Got back %s" % (stringdata))

        self.serverClient.close()

client = ftpClient()
client.openConnection("localhost", 9999)    # temp for testing
client.requestLoop()
