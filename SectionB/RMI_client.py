# Client.py
import struct
import os
import Pyro4
import serpent
import time

class rmiClient:
    def cmdUpload(self, toAll):
        tic = time.clock()
        upload = input("Enter file you would like to upload > ").strip()
        #check if file exists
        if os.path.isfile(upload):
            print("File exists")
        else:
            print("File does not exist")
            return
        file_exists = frontEnd.clientUploadChk(upload)
        if file_exists != 1:
            print("Error: File already exists")
            return
        #upload file to server
        file = open(upload, "rb")
        data = file.read()
        file.close()
        toc = time.clock()
        t_time = toc - tic

        print("data len=%u in %s seconds" % (len(data), round(t_time,2)))
        print(frontEnd.clientUpload(upload, toAll, data))

    def cmdDownload(self):
       tic = time.clock()
       download = input("Enter file you would like to download > ").strip()
       #checks if file exists locally
       if os.path.isfile(download):
            print("Error file already exits locally")
            return
       file_exists = frontEnd.clientDownloadChk(download)
       if file_exists != 1:
            print("Error file does not exist remotely")
            return
       data = frontEnd.clientDownload(download)
       if data == "":
            print("Error file does not exist remotely")
            return
       #downloads file if doesn't appear locally
       new_file = open(download, "wb")
       new_file.write(serpent.tobytes(data))
       new_file.close()
       toc = time.clock()
       t_time = toc - tic
       print("data len=%u in %s seconds" % (len(data), round(t_time,2)))

    def cmdDelete(self):
        delete = input("Enter file you would like to delete > ").strip()
        # wait for server reply
        file_exists = frontEnd.clientDeleteChk(delete)
        #checks if file exists and if you want to delete it
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
            #available commands for client
                print("Client help options:"
                print("LIST\tlist files on remote server")
                print("UPLD\tupload a file to the server")
                print("UPLDHR\tupload a file to the server???")
                print("DWLD\tdownload a file from the server")
                print("DELF\tdelete a file from the server")
                print("QUIT\tclose session")
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

uri = input("What is the Pyro uri of the front end? ").strip()

# get a Pyro proxy to the front end
frontEnd = Pyro4.Proxy(uri)

client = rmiClient()
client.requestLoop()
