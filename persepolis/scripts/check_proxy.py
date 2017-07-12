import platform
import subprocess
from shutil import which

class Proxy:
    def check_proxy_manual():
        """ True If Proxy Settings Is Configures As Manual """
        proxy = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy', 'mod'])
        proxy = proxy.decode('utf-8')
        proxy = proxy.split('\n')[0]

        return (proxy == 'manual')

    def check_proxy_auto():
        """ True If Proxy Settings Is Configures As Auto """
        proxy = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy', 'mod'])
        proxy = proxy.decode('utf-8')
        proxy = proxy.split('\n')[0]

        return (proxy == 'auto')

    def check_proxy(self):
        """ Checks the Proxy Status """
        if self.check_proxy_auto():
            return ('auto')
        elif self.check_proxy_manual():
            return ('manual')
        return None

class Tor:
    def __init__(self):
        if platform.system() == 'linux':
            self.tor = which('tor')
        else:
            self.tor = None

    def check_tor(self):
        """ True If Tor Is Installed """
        return (self.tor is not None)

    def socks_tor(self):
        """ Checks If Socks Proxy Is Configured For Tor """
        if Proxy().check_proxy_manual() and self.check_tor():
            socks = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy.socks', 'port'])
            socks = tor.decode('utf-8')
            socks = tor.split('\n')[0]

            if tor == '9050':
                return True
            return False

class Privoxy:
    def __init__(self):
        if platform.system() == 'linux':
            self.privoxy = which('privoxy')
        else:
            self.privoxy = None

    def check_http(self):
        if Proxy().check_proxy_manual() and self.privoxy is not None:
            proxy_host = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy.http', 'host'])
            proxy_host = proxy_host.decode('utf-8')
            proxy_host = proxy_host.split('\n')[0]

            proxy_port = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy.http', 'port'])
            proxy_port = proxy_port.decode('utf-8')
            proxy_port = proxy_port.split('\n')[0]

            if proxy_host == '127.0.0.1' or proxy_host == 'localhost':
                if proxy_port == '8118':
                    return True
            return False

    def check_https(self):
        if Proxy().check_proxy_manual() and self.privoxy is not None:
            proxy_host = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy.https', 'host'])
            proxy_host = proxy_host.decode('utf-8')
            proxy_host = proxy_host.split('\n')[0]

            proxy_port = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy.https', 'port'])
            proxy_port = proxy_port.decode('utf-8')
            proxy_port = proxy_port.split('\n')[0]

            if proxy_host == '127.0.0.1' or proxy_host == 'localhost':
                if proxy_port == '8118':
                    return True
            return False

    def check_privoxy(self):
        if self.check_http() or self.check_https():
            return True
        return False

# By Mostafa
import urllib, requests,os

# TODO: mac os socks proxy, check ftp proxy suport

# get proxy function
def getproxy():
    # check if it is KDE
    if os.environ.get('XDG_CURRENT_DESKTOP') == 'KDE' :
        # all print just for debugung
        print(os.environ.get('XDG_CURRENT_DESKTOP'))

        # creat empty list for proxies
        proxy = {}
        # user home directory
        home_address = os.path.expanduser("~")

        # read kde plasma proxy config file
        try:
            with open(home_address + '/.config/kioslaverc') as proxyfile:
                for line in proxyfile:
                    name, var = line.partition("=")[::2]
                    proxy[name.strip()] = str(var)
        except Exception as e:
            # all print just for debugung
            print("Error")

        # get ftp proxy
        try :
            ftpProxyPort = proxy['ftpProxy'].split(' ')[1]
            ftpProxyIp = proxy['ftpProxy'].split(' ')[0]
            # all print just for debugung
            print('FTP Proxy IP : ' + ftpProxyIp)
            print('FTP Proxy Port : ' + ftpProxyPort)
        except Exception as e :
            ftpProxyIp = False
            # all print just for debugung
            print('Error')

        # get http proxy
        try:
            httpProxyPort = proxy['httpProxy'].split(' ')[1]
            httpProxyIp = proxy['httpProxy'].split(' ')[0]
            # all print just for debugung
            print('HTTP Proxy IP : ' + httpProxyIp)
            print('HTTP Proxy Port : ' + httpProxyPort)
        except Exception as e :
            httpProxyIp = False
            # all print just for debugung
            print('Error')

        # get https proxy
        try:
            httpsProxyPort = proxy['httpsProxy'].split(' ')[1]
            httpsProxyIp = proxy['httpsProxy'].split(' ')[0]
            # all print just for debugung
            print('HTTPS Proxy IP : ' + httpsProxyIp)
            print('HTTPS Proxy Port : ' + httpsProxyPort)
        except Exception as e:
            httpsProxyIp = False
            # all print just for debugung
            print('Error')

        # get socks proxy
        try:
            socksProxyPort = proxy['socksProxy'].split(' ')[1]
            socksProxyIp = proxy['socksProxy'].split(' ')[0]
            # all print just for debugung
            print('Socks Proxy IP : ' + socksProxyIp)
            print('Socks Proxy Port : ' + socksProxyPort)
        except Exception as e:
            socksProxyIp = False
            # all print just for debugung
            print('Error')

        # check if just socks proxy exists
        if not any ([httpProxyIp , ftpProxyIp , httpsProxyIp]) and socksProxyIp :
            # all print just for debugung
            print("persepolis doesn't suport socks!")
        # atleast there is another proxy except socks
        else:
            # all print just for debugung
            print('no problem')

    # if it is windows,mac and other linux desktop
    else:
        # get proxies
        proxy = urllib.request.getproxies()

        # get http proxy
        try:
            httpProxyIp = 'http:' + proxy['http'].split(':')[1]
            httpProxyPort = proxy['http'].split(':')[2]
            # all print just for debugung
            print('HTTP Proxy IP : ' + httpProxyIp)
            print('HTTP Proxy Port : ' + httpProxyPort)
        except Exception as e :
            # all print just for debugung
            print("Error")
            httpProxyIp = False

        # get https proxy
        try:
            httpsProxyIp = 'https:' + proxy['https'].split(':')[1]
            httpsProxyPort = proxy['https'].split(':')[2]
            # all print just for debugung
            print('HTTPS Proxy IP : ' + httpsProxyIp)
            print('HTTP Proxy Port : ' + httpsProxyPort)
        except Exception as e :
            # all print just for debugung
            print("Error")
            httpsProxyIp = False

        # get ftp proxy
        try:
            ftpProxyIp = 'ftp:' + proxy['ftp'].split(':')[1]
            ftpProxyPort = proxy['ftp'].split(':')[2]
            # all print just for debugung
            print('FTP Proxy IP : ' + ftpProxyIp)
            print('FTP Proxy Port : ' + ftpProxyPort)
        except Exception as e :
            # all print just for debugung
            print("Error")
            ftpProxyIp = False

        # get socks proxy
        try:
            socksProxyIp = 'socks:' + proxy['socks'].split(':')[1]
            socksProxyPort = proxy['socks'].split(':')[2]
            # all print just for debugung
            print('Socks Proxy IP : ' + socksProxyIp)
            print('Socks Proxy Port : ' + socksProxyPort)
        except Exception as e :
            # all print just for debugung
            print("Error")
            socksProxyIp = False

        # check if just socks proxy exists
        if not any ([httpProxyIp , ftpProxyIp , httpsProxyIp]) and socksProxyIp :
            # all print just for debugung
            print("persepolis doesn't suport socks!")
       # atleast there is another proxy except socks
        else:
            # all print just for debugung
            print('no problem')
