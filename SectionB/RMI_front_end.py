# RMI_front_end
# RMI_front_end
import Pyro4
import time
from threading import Thread
import serpent

remoteServerList = []
remoteFiles = []
remoteFilesServers = {}

class remoteServer(object):
    def __init__(self, uri):
        self.uri = uri
        self.rmi = Pyro4.Proxy(uri)
        self.no_files = 0
        print("Adding server %s" % uri)

@Pyro4.expose
class frontEnd(object):
    def serverRegister(self, uri):
        print("Server registering URI %s: " % uri)
        remoteServerList.append(remoteServer(uri))
#        print("done remoteServer")

    def clientStatus(self):
        status = "FrontEnd running successfully\n"
        for server in remoteServerList:
            status += "Server %s\n  Total number of files %u\n" % (server.uri, server.no_files)
        status += "\nTotal number of files known about by the whole system %u\n" % (len(remoteFiles))
        return status

    def clientList(self):
        status = "Total number of files %u\n" % len(remoteFiles)
        for index, file in enumerate(remoteFiles):
    #        print("%u: %s" % (index, file))
            stored_on_count = 0
            for server_index, server in enumerate(remoteServerList):
                if (index,server_index) in remoteFilesServers:
    #                print("file stored on %u" % server_index)
                    stored_on_count = stored_on_count + 1
    #            else:
    #                print("file NOT stored on %u" % server_index)
            if stored_on_count == len(remoteServerList):
                status += "%- 30.30s (is stored on all servers)\n" % file
            elif stored_on_count > 1:
                status += "%- 30.30s (is stored on %u/%u servers)\n" % (file, stored_on_count, len(remoteServerList))
            else:
                status += "%- 30.30s (is stored on a single file server)\n" % file
        return status

    def clientUploadChk(self, fileName):
#        print("clientUploadChk fileName=%s" % fileName)
        ret = 1
        if fileName in remoteFiles:
            ret = -1
#        print("clientUploadChk ret=%u" % ret)
        return ret

    def clientUpload(self, fileName, toAll, data):
        raw = serpent.tobytes(data)
        print("clientUpload file \"%s\", HR=%u, size %u bytes" % (fileName, toAll, len(raw)))

        if toAll:
            for server in remoteServerList:
                server.rmi.cmdUpload(fileName, raw)
        else:
            small_number_of_stored_files = 100000000
            for server in remoteServerList:
                if server.no_files < small_number_of_stored_files:
                    small_number_of_stored_files = server.no_files

            for server in remoteServerList:
                if server.no_files == small_number_of_stored_files:
                    server.rmi.cmdUpload(fileName, raw)
                    break

        return "Success transferred %u bytes " % len(raw)

    def clientDeleteChk(self, fileName):
#        print("clientDeleteChk fileName=%s" % fileName)
        ret = -1
        if fileName in remoteFiles:
            ret = 1
#        print("clientDeleteChk ret=%u" % ret)
        return ret

    def clientDelete(self, fileName):
#        print("clientDelete file \"%s\"" % (fileName))
        total_deletes = 0
        for server in remoteServerList:
            total_deletes += server.rmi.cmdDelete(fileName)

        print("total_deletes=%u" % total_deletes)
        return "total_deletes=%u" % total_deletes

daemon = Pyro4.Daemon()        # make a Pyro daemon
uri = daemon.register(frontEnd)   # register the Hello as a Pyro object

def updateFileList():
    remoteFiles.clear()
    remoteFilesServers.clear()
    for index, server in enumerate(remoteServerList):
#        print("LIST server %s" % server.uri)
        try:
            files = server.rmi.cmdList()
#            print("files %u" % len(files))
            server.no_files = len(files)
            for file in files:
#                print("  %s" % file)
                try:
                    file_index = remoteFiles.index(file)
#                    print("for file %s already stored as %u" % (file, file_index))
                except ValueError:
#                    print("for file %s not found so adding" % (file))
                    remoteFiles.append(file)
                    file_index = remoteFiles.index(file)
                remoteFilesServers[file_index,index] = True
        except Exception as e:
            print("server %s LIST failed %s" % (server.uri, e))

def poll_thread():
    while True:
#        print("sleeping 10 sec from thread")
        time.sleep(2)
        for server in reversed(remoteServerList):
#            print("checking server %s" % server.uri)
            try:
#                print(" stillAlive %u"  % server.rmi.stillAlive())
                server.rmi.stillAlive()
            except Exception as e:
                print("server no longer alive, removing because %s" % (e))
                remoteServerList.remove(server)
        updateFileList()

t = Thread(target=poll_thread)
t.start()

# print the uri so we can use it in the client / servers later
print("Front end ready: Object uri =", uri)
# start the event loop of the server to wait for calls
daemon.requestLoop()