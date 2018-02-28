# client.py  
import socket
import struct
import os
import time

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
        #reads size of file
        buf = bytes()
        while size > 0:
            data = self.serverClient.recv(size)
            if data == '':
                raise RuntimeError('read unexpected data')
            buf += data
            size -= len(data)
        return buf
        
    def recvLenData(self):
        #recieves length of file from the server
        temp = self.socketReadSize(4)
        len = struct.unpack('!I', temp)[0]
        data = self.socketReadSize(len)
        str = data.decode('utf-8')
        print(str)

    def recvInt(self):
        #recieves int from server
        temp = self.socketReadSize(4)
        value = struct.unpack('!i', temp)[0]
        #print("recvInt received %i" % value)
        return value
        
    def cmdList(self):
        #lists files on the server
        self.send('LIST')
        self.recvLenData()
    
    def cmdUpload(self):
        #enter file you wnat to upload
        upload = input("Enter file you would like to upload > ").strip()
        #checks if file exists or not on the client
        if not os.path.isfile(upload):
            print("File does not exist")
            return
        self.send('UPLD')
        self.sendLenData(upload)
        #checks if file exists or not on the server
        file_exists = self.recvInt()
        if file_exists != 1:
            print("Error: File already exists on server")
            return
        #uploads file to server
        tic = time.clock() 
        file = open(upload, "rb")
        data = file.read()
        file.close()
        self.sendLenBinaryData(data)   
        toc = time.clock()
        t_time = toc - tic
        print("Successfully uploaded file of %u bytes in %s seconds" % (len(data),round(t_time,2)))

    def cmdDownload(self):
        download = input("Enter file you would like to download > ").strip()
        if os.path.isfile(download):
            print("Error: File already exits locally")
            return
        self.send('DWLD')
        self.sendLenData(download)
        server_response = self.recvInt()
        if server_response == -1:
            print("No such file on server")
            return
        tic = time.clock()
        data = self.socketReadSize(server_response)
        new_file = open(download, "wb")
        new_file.write(data)
        new_file.close()
        toc = time.clock()
        t_time = toc - tic
        print("Successfully downloaded file of %u bytes in %s seconds" % (server_response,round(t_time,2)))

    def sendLenData(self, data):
        #send length of data to the server
        b = bytes(data, 'utf-8')
        lenData = struct.pack('!I', len(b)) + b
#       print("sending lenData '%s'" % lenData)
        self.serverClient.send(lenData)
         
    def sendLenBinaryData(self, data):
        #send length of binary data to the server
        lenData = struct.pack('!I', len(data)) + data
        #print("sending lenData %u bytes" % len(data))
        self.serverClient.sendall(lenData)
         
    def cmdDelete(self):
        #enter what file you would like to delete 
        delete = input("Enter file you would like to delete > ").strip() 
        self.send('DELF')
        self.sendLenData(delete)
        
        # wait for server reply and check if file exists
        file_exists = self.recvInt()
        # check you want to delete the file
        if file_exists != -1:
            cmd = input("Do you want to delete %s? (Yes, No)" % delete).strip()
            if cmd.upper() == 'YES':
                self.send("Yes")
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
                print("Client help options:")
                print("CONN\tconnect to server")
                print("LIST\tlist files on remote server")
                print("UPLD\tupload a file to the server")
                print("DWLD\tdownload a file from the server")
                print("DELF\tdelete a file from the server")
                print("QUIT\tclose session")
                continue
            elif cmd.upper() == 'CONN':
                self.cmdConnection()
                continue
            elif cmd.upper() == 'LIST':
                self.cmdList()
                continue
            elif cmd.upper() == 'UPLD':
                self.cmdUpload()
                continue
            elif cmd.upper() == 'DWLD':
                self.cmdDownload()
                continue
            elif cmd.upper() == 'DELF':
                self.cmdDelete()
                continue
            elif cmd.upper() == 'QUIT':
                print("Closing session to server")
                exit(0)
             
            if self.serverClient is None:
                print("No connection to a server, you must connect (using CONN) first")
                continue

        self.serverClient.close()

client = ftpClient()
#client.openConnection("localhost", 9999)    # temp for testing
client.requestLoop()