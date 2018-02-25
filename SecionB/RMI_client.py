# Client.py
import Pyro4

## temp

uri = input("What is the Pyro uri of the front end? ").strip()

# get a Pyro proxy to the front end
rmi = Pyro4.Proxy(uri)

print("FE calling hello")
rmi.hello()
print("FE calling fail")
rmi.fail()
