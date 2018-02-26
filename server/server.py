# server.py 
import socket                                         
import time
import struct
import os

class ftpServer:
    def __init__(self, port=9999):
        """
        :param port:       TCP port to listen on
        """
        self.port = port
        
    def cmdConnection(self):
        # create a socket object
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind to the port
        self.serverSocket.bind(('', self.port))                                  

        # queue up to 5 requests
        self.serverSocket.listen(5)                                           

    def sendData(self, data):
        #sends data to the client
        print("sending '%s'" % data)
        self.clientSocket.send(data.encode())
        return

    def sendLenData(self, data):
        #sends length of data to client
        b = bytes(data, 'utf-8')
        lenData = struct.pack('!I', len(b)) + b
#        print("sending lenData '%s'" % lenData)
        self.clientSocket.send(lenData)
        return

    def sendInt(self, value):
        #sends int to client
        lenData = struct.pack('!i', value)
#        print("sending lenData '%s'" % lenData)
        self.clientSocket.send(lenData)
        return

    def addDirectoryContentsToList(self, path):
        for dir in os.listdir(path):                
            dirPath = os.path.join(path,dir)
            if os.path.isdir(dirPath):
                self.addDirectoryContentsToList(dirPath)
            else:
                self.directoryListing +=  dirPath + '\n'       
        
    def socketReadSize(self, size):
        buf = bytes()
        while size > 0:
            data = self.clientSocket.recv(size)
            if data == '':
                raise RuntimeError('read unexpected data')
            buf += data
            size -= len(data)
        return buf
        
    def recvLenData(self):
        #recieves length of data from client
        temp = self.socketReadSize(4)
        len = struct.unpack('!I', temp)[0]
        data = self.socketReadSize(len)
        str = data.decode('utf-8')
#        print(str)
        return str
        
    def recvLenBinaryData(self):
        #recieves length of binary data from client
        temp = self.socketReadSize(4)
        len = struct.unpack('!I', temp)[0]
        data = self.socketReadSize(len)
        return data
        
    def recvString(self):
        #recieves string from client
        data = self.clientSocket.recv(1024)
        stringdata = data.decode('utf-8')
        print("recvString %s " % (stringdata))
        return stringdata
         
    def cmdList(self):
        #lists files on server
        self.directoryListing = '';
        self.addDirectoryContentsToList('.')
        self.sendLenData(self.directoryListing)
        return
        
    def cmdUpload(self):
        #recieves length of data from client
        file = self.recvLenData()
        print("got %s file to upload" % file)
        #checks to see if file already exists on server
        if os.path.isfile(file):
            self.sendInt(-1)
            print ("sent -1")
        else:
            self.sendInt(1)
            print ("sent 1")
        #uploads file to server
        data = self.recvLenBinaryData()
        new_file = open(file, "wb")
        new_file.write(data)
        new_file.close()

    def cmdDownload(self):
        download = self.recvLenData()
        if os.path.isfile(download):
            print("File %s exists for downloaded to client" % download)
        else:
            print("File does not exist")
            self.sendInt(-1)
            return
            
        file = open(download, "rb")
        data = file.read()
        file.close()
        self.sendLenBinaryData(data)

    def cmdDelete(self):
        #recieves lenth of data from client
        file = self.recvLenData()
        print("got %s file to delete" % file)
        #checks if file exists
        if os.path.isfile(file):
            self.sendInt(1)
        else:
            self.sendInt(-1)
            
        # wait for client yes or no
        yes_or_no = self.recvString()
        #print("DELT: got back %s" % yes_or_no)
        #deletes file
        if yes_or_no == "Yes":
            os.remove(file)
            print ("File successfully deleted")
        else:
            print("DELT: failed to understand %s" % yes_or_no)

    def requestLoop(self) :
        while True:
            # "wait for connection" state
            self.clientSocket,addr = self.serverSocket.accept()      

            print("Got a connection from %s" % str(addr))
            
            while True:
                # "wait for operation from client" state
                try:
                    data = self.clientSocket.recv(1024)
                except Exception as e:
                    print("connect to %s failed %s" % (addr, e))
                    break;
                
                if not data: break    
                stringdata = data.decode('utf-8')
                print("Got cmd %s from %s" % (stringdata, str(addr)))
            
                if stringdata.upper() == 'HELP':
                    print("Help options are help");
                elif stringdata.upper() == 'LIST':
                    self.cmdList()
                elif stringdata.upper() == 'UPLD':
                    self.cmdUpload()
                elif stringdata.upper() == 'DWLD':
                    self.cmdDownload()
                elif stringdata.upper() == 'DELF':
                    self.cmdDelete()
                elif stringdata.upper() == 'QUIT':
                    break
                else:
                    print("Didn't understand %s" % (stringdata))
                    self.sendData("error Didn't understand")
            
            print("Closed connection to %s" % str(addr))
            self.clientSocket.close()
    
server = ftpServer()
server.cmdConnection()
server.requestLoop()