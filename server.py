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
        print("sending '%s'" % data)
        self.clientSocket.send(data.encode())
        return

    def sendLenData(self, data):
        b = bytes(data, 'utf-8')
        lenData = struct.pack('!I', len(b)) + b
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
        
    def cmdList(self):
        self.directoryListing = '';
        self.addDirectoryContentsToList('.')
        self.sendLenData(self.directoryListing)
        return

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
                elif stringdata.upper() == 'EXIT':
                    break
                else:
                    print("Didn't understand %s" % (stringdata))
                    self.sendData("error Didn't understand")
            
            print("Closed connection to %s" % str(addr))
            self.clientSocket.close()
    
server = ftpServer()
server.cmdConnection()
server.requestLoop()

