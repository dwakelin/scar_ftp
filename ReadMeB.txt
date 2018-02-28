To run the code:
~Need Python3 and Pyro4 is installed (pip install Pyro4)~
python -u RMI_front_end.py (This wil print something like 'Front end ready: Object uri =', <Pyro4.core.URI at 0x4eea9b0; PYRO:obj_5d9b57c23df84c9a94b30d78dce3e79d@localhost:50332>
python -u RMI_server.py (This will ask for Pyro uri of front end, which is the PYRO bit above)
python -u RMI_client.py (This will ask for Pyro uri of front end, which is the PYRO bit above)
