import platform
import subprocess
from shutil import which

class OS:
    def system():
        """ Checks The OS, True On Linux Systems """
        return (platform.system == 'linux')

class Tor:
    def __init__(self):
        self.tor = which('tor')

    def check_tor(self):
        """ True If Tor Is Installed """
        return (self.tor is None)

    def check_proxy_manual():
        """ True If Proxy Settings Is Configures As Manual """
        proxy = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy', 'mod'])
        proxy = proxy.decode('utf-8')
        proxy = proxy.split('\n')[0]

        if proxy == 'manual':
            tor = subprocess.check_output('gsettings', 'get', 'org.gnome.system.proxy.socks', 'port')
            tor = tor.decode('utf-8')
            tor = tor.split('\n')[0]

            if tor == '9050':
                return True
            return False

    def check_proxy_auto():
        """ True If Proxy Settings Is Configures As Auto """
        proxy = subprocess.check_output(['gsettings', 'get', 'org.gnome.system.proxy', 'mod'])
        proxy = proxy.decode('utf-8')
        proxy = proxy.split('\n')[0]

        return (proxy == 'auto')
