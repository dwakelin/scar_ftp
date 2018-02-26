# Client.py
import socket
import struct
import os
import Pyro4

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

    def recvInt(self):
        temp = self.socketReadSize(4)
        value = struct.unpack('!i', temp)[0]
        print("recvInt received %i" % value)
        return value

    def cmdList(self):
        self.send('LIST')
        self.recvLenData()

    def cmdUpload(self, toAll):
        upload = input("Enter file you would like to upload > ").strip()
        if os.path.isfile(upload):
            print("File exists")
        else:
            print("File does not exist")
            return
        file_exists = frontEnd.clientUploadChk(upload)
        if file_exists != 1:
            print("Error: File already exists")
            return
        file = open(upload, "rb")
        data = file.read()
        file.close()

        print("data len=%u" % (len(data)))
        print(frontEnd.clientUpload(upload, toAll, data))

    def cmdDownload(self):
       self.send('DWLD')
       download = input("Enter file you would like to download > ").strip()
       file = self.recvLenData()
       print("got %s file to download" % file)
       if os.path.isfile(file):
            self.sendInt(-1)
            print ("sent -1")
       else:
            self.sendInt(1)
            print ("sent 1")
       data = self.recvLenData()
       new_file = open(file, "wb")
       new_file.write(data)
       new_file.close()

    def sendLenData(self, data):
        b = bytes(data, 'utf-8')
        lenData = struct.pack('!I', len(b)) + b
#        print("sending lenData '%s'" % lenData)
        self.serverClient.send(lenData)

    def sendLenBinaryData(self, data):
        lenData = struct.pack('!I', len(data)) + data
        print("sending lenData %u bytes" % len(data))
        self.serverClient.sendall(lenData)

    def cmdDelete(self):
        delete = input("Enter file you would like to delete > ").strip()
        # wait for server reply
        file_exists = frontEnd.clientDeleteChk(delete)
        if file_exists != -1:
            cmd = input("Do you want to delete %s? (Yes, No)" % delete).strip()
            if cmd.upper() == 'YES':
                print(frontEnd.clientDelete(delete))
                print ("File deleted")
            if cmd.upper() == 'NO':
                print ("Delete abandoned by the user!")
                return
        else:
            print("The file does not exist on server")
            return

    def requestLoop(self):
        while True:
            # "prompt user for operation" state
            cmd = input("Enter cmd > ").strip()

            if cmd.upper() == 'HELP':
                print("Client help options are help")
                continue
            elif cmd.upper() == 'CONN':
                self.cmdConnection()
                continue
            elif cmd.upper() == 'LIST':
                print(frontEnd.clientList())
                continue
            elif cmd.upper() == 'UPLD':
                self.cmdUpload(False)
                continue
            elif cmd.upper() == 'UPLDHR':
                self.cmdUpload(True)
                continue
            elif cmd.upper() == 'DWLD':
                self.cmdDownload()
                continue
            elif cmd.upper() == 'DELF':
                self.cmdDelete()
                continue
            elif cmd.upper() == 'QUIT':
                exit(0)
            elif cmd.upper() == 'STATUS':
                print(frontEnd.clientStatus())
                continue

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

#client = ftpClient()
#client.openConnection("localhost", 9999)    # temp for testing
#client.requestLoop()
## temp

uri = input("What is the Pyro uri of the front end? ").strip()

# get a Pyro proxy to the front end
frontEnd = Pyro4.Proxy(uri)

client = ftpClient()
client.requestLoop()