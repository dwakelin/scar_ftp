# RMI_server
import Pyro4
import os
import serpent

@Pyro4.expose
class server(object):
    def __init__(self):
        self.directoryListing = []
        
    def stillAlive(self):
#        print("Server still alive")
        return True
        
    def addDirectoryContentsToList(self, path):
        for dir in os.listdir(path):                
            dirPath = os.path.join(path,dir)
            if os.path.isdir(dirPath):
                self.addDirectoryContentsToList(dirPath)
            else:
                self.directoryListing.append(dirPath)

    def cmdList(self):
#        print("cmd LIST called")
        self.directoryListing.clear()
        self.addDirectoryContentsToList('.')
        return self.directoryListing

    def cmdUpload(self, file, data):
        raw = serpent.tobytes(data)
        print("cmdUpload file \"%s\", size %u bytes" % (file, len(raw)))
#        print("raw=%s" % raw)
        new_file = open(file, "wb")
        new_file.write(raw)
        new_file.close()
        return "Success"

    def cmdDelete(self, file):
        print("cmdDelete file \"%s\"" % (file))
        if os.path.isfile(file):
            os.remove(file)
            return 1
        return 0

#test code
s = server()
#print(s.cmdList())
#s.cmdUpload("test", "sjkdbffsd")

uri = input("What is the Pyro uri of the front end? ").strip()

# get a Pyro proxy to the front end
frontEnd = Pyro4.Proxy(uri)

# make a Pyro daemon
daemon = Pyro4.Daemon()
uri = daemon.register(server)
print("server ready: Object uri =", uri)
frontEnd.serverRegister(uri)
print("done frontEnd.serverRegister, about to requestLoop") 

# start the event loop of the server to wait for calls
daemon.requestLoop()