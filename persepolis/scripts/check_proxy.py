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
