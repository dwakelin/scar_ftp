# RMI_server
import Pyro4
import os

@Pyro4.expose
class server(object):
    def __init__(self):
        self.directoryListing = []
        
    def stillAlive(self):
        print("Server still alive")
        return True
        
    def addDirectoryContentsToList(self, path):
        for dir in os.listdir(path):                
            dirPath = os.path.join(path,dir)
            if os.path.isdir(dirPath):
                self.addDirectoryContentsToList(dirPath)
            else:
                self.directoryListing.append(dirPath)

    def cmdList(self):
        print("cmd LIST called")
        self.directoryListing.clear();
        self.addDirectoryContentsToList('.')
        for file in self.directoryListing:
            print("file=%s" % file)
        return self.directoryListing

#test code
s = server()
#print(s.cmdList())

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