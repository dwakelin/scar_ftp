# RMI_front_end
import Pyro4
import time
from threading import Thread

remoteServerList = []
remoteFiles = []
#remoteFilesServers = []
remoteFilesServers = {}

class remoteServer(object):
    def __init__(self, uri):
        self.uri = uri
        self.rmi = Pyro4.Proxy(uri)
        print("Adding server %s" % uri)

@Pyro4.expose
class frontEnd(object):
    def serverRegister(self, uri):
        print("Server registering URI %s: " % uri)
        remoteServerList.append(remoteServer(uri))
        print("done remoteServer");

daemon = Pyro4.Daemon()        # make a Pyro daemon
uri = daemon.register(frontEnd)   # register the Hello as a Pyro object

def cmdList():
    remoteFiles.clear()
    remoteFilesServers.clear()
    for index, server in enumerate(remoteServerList):
        print("LIST server %s" % server.uri)
        try:
            files = server.rmi.cmdList()
            print("files %u" % len(files))
            for file in files:
                print("  %s" % file)
                try:
                    file_index = remoteFiles.index(file)
                    print("for file %s already stored as %u" % (file, file_index))
                except ValueError:
                    print("for file %s not found so adding" % (file))
                    remoteFiles.append(file)
                    file_index = remoteFiles.index(file)
                remoteFilesServers[file_index,index] = True;
        except Exception as e:
            print("server %s LIST failed %s" % (server.uri, e))
        
def cmdListDisplay():
    print("cmdListDisplay %u" % len(remoteFiles))
    for index, file in enumerate(remoteFiles):
        print("%u: %s" % (index, file))
        for server_index, server in enumerate(remoteServerList):
            if (index,server_index) in remoteFilesServers:
                print("file stored on %u" % server_index)
            else:
                print("file NOT stored on %u" % server_index)
        
def poll_thread():
    while True:
        print("sleeping 10 sec from thread")
        time.sleep(10)
        for server in reversed(remoteServerList):
            print("checking server %s" % server.uri)
            try:
                print(" stillAlive %u"  % server.rmi.stillAlive())
            except Exception as e:
                print("server no longer alive, removing because %s" % (e))
                remoteServerList.remove(server)
        cmdList()
        cmdListDisplay()

t = Thread(target=poll_thread)
t.start()

# print the uri so we can use it in the client / servers later
print("Front end ready: Object uri =", uri)
# start the event loop of the server to wait for calls
daemon.requestLoop()