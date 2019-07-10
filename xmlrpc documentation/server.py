from xmlrpclibserver import SimpleXMLRPCServer
from xmlrpclibserver import SimpleXMLRPCRequestHandler
import xmlrpclibclient

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Create server
with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    #Simply return string
    def handshake():
        return "Welcome"

    #register the function
    server.register_function(handshake, "handshake")

    #function who receive file from the client to the server
    def server_receive_file(arg):
        with open("test.txt", "wb") as file:
            file.write(arg.data)
            return True

    #register the function
    server.register_function(server_receive_file, 'server_receive_file')

    #function who send file to the client from the server
    def server_send_file():
        with open("requirements.txt", "rb") as file:
            return file.read()


    # register the function
    server.register_function(server_send_file, "server_send_file")

    #Simple class who send x * y to the client from the server
    class MyFuncs:
        def simpleclass(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    # Run the server's main loop
    server.serve_forever()
