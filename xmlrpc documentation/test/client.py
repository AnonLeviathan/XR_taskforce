# https://github.com/Bitmessage/PyBitmessage/blob/master/src/api_client.py
# https://github.com/python/cpython/blob/3.7/Lib/xmlrpc/server.py

import xmlrpclibclient

#Call a new instance and connect to the server proxy
server = xmlrpclibclient.ServerProxy('http://localhost:8000')

# Print list of available methods
print(server.system.listMethods())

#use of the basic function, return "Welcome"
print(server.handshake())

#use of a simple class, return x * y
print(server.simpleclass(2, 4))

#use of send file to the server from the client
with open("requirements.txt", "rb") as handle:
    binary_data = xmlrpclibclient.Binary(handle.read())
server.server_receive_file(binary_data)

#use to upload file from the server to the client
with open("test.txt", "wb") as file:
    file.write(server.server_send_file().data)