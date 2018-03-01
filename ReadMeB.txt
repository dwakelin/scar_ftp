To run the code:
~Need Python3 and Pyro4 installed (pip install Pyro4)~
python -u RMI_front_end.py (This will print something like Front end ready: Object uri = PYRO:obj_89fa3d6f92b841aba131151249a7714a@localhost:50370
python -u RMI_server.py (This will ask for Pyro uri of front end, which is the PYRO bit above e.g PYRO:obj_89fa3d6f92b841aba131151249a7714a@localhost:50370)
python -u RMI_client.py (This will ask for Pyro uri of front end, which is the PYRO bit above e.g PYRO:obj_89fa3d6f92b841aba131151249a7714a@localhost:50370)

You can have multiple servers running at once.
Enter HELP to get the available commands:
	STATUS- shows status of entire system
	LIST- lists files on remote server
	UPLD- uploads a file to the server
	UPLDHR- uploads a file to all of the servers
	DWLD- downloads a file from the server
	DELF- deletes a file from the server
	QUIT- quits the client 
