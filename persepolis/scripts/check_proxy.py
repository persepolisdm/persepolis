import urllib
import requests
import os
from persepolis.scripts import logger
import platform

os_type = platform.system()

# get proxy function
def getProxy():
    # finding desktop environment
    desktop = os.environ.get('XDG_CURRENT_DESKTOP')
    proxy = {}
    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
        if desktop == None:
            desktop_env_type = 'Desktop Environment not detected!'
        else:
            desktop_env_type = 'Desktop environment: ' + str(desktop)

        logger.sendToLog(desktop_env_type, "INFO")
        print(desktop_env_type)

    # check if it is KDE
    if desktop == 'KDE' :
        # creat empty list for proxies
        proxysource = {}
        # user home directory
        home_address = os.path.expanduser("~")

        # read kde plasma proxy config file
        try:
            plasma_proxy_config_file_path = os.path.join(home_address, '.config', 'kioslaverc')
            with open(plasma_proxy_config_file_path) as proxyfile:
                for line in proxyfile:
                    name, var = line.partition("=")[::2]
                    proxysource[name.strip()] = str(var)
        except:
            logger.sendToLog('no proxy detected', 'INFO')

        # check proxy enabled as manually
        if proxysource['ProxyType'].split('\n')[0] == '1' :
            # get ftp proxy
            try:
                proxy['ftpProxyPort'] = proxysource['ftpProxy'].split(' ')[1].replace("/", "").replace("\n", "")
                proxy['ftpProxyIp'] = proxysource['ftpProxy'].split(' ')[0].split('//')[1]
            except:
                logger.sendToLog('no manuall ftp proxy detected', 'INFO')


            # get http proxy
            try:
                proxy['httpProxyPort'] = proxysource['httpProxy'].split(' ')[1].replace("/", "").replace("\n", "")
                proxy['httpProxyIp'] = proxysource['httpProxy'].split(' ')[0].split('//')[1]
            except:
                logger.sendToLog('no manuall http proxy detected', 'INFO')

            # get https proxy
            try:
                proxy['httpsProxyPort'] = proxysource['httpsProxy'].split(' ')[1].replace("/", "").replace("\n", "")
                proxy['httpsProxyIp'] = proxysource['httpsProxy'].split(' ')[0].split('//')[1]
            except:
                logger.sendToLog('no manuall https proxy detected', 'INFO')

        # proxy disabled
        else:
            logger.sendToLog('no manuall proxy detected', 'INFO')


    # if it is windows,mac and other linux desktop
    else:
        # get proxies
        proxysource = urllib.request.getproxies()
        # get http proxy
        try:
            proxy['httpProxyIp'] = proxysource['http'].split(':')[1].replace('//','')
            proxy['httpProxyPort'] = proxysource['http'].split(':')[2].replace("/", "").replace("\n", "")
        except:
            logger.sendToLog('no http proxy detected', 'INFO')

        # get https proxy
        try:
            proxy['httpsProxyIp'] = proxysource['https'].split(':')[1].replace('//','')
            proxy['httpsProxyPort'] = proxysource['https'].split(':')[2].replace("/", "").replace("\n", "")
        except:
            logger.sendToLog('no https proxy detected', 'INFO')

        # get ftp proxy
        try:
            proxy['ftpProxyIp'] = proxysource['ftp'].split(':')[1].replace('//','')
            proxy['ftpProxyPort'] = proxysource['ftp'].split(':')[2].replace("/", "").replace("\n", "")
        except:
            logger.sendToLog('no ftp proxy detected', 'INFO')

    # return results
    proxy_log_message = 'proxy: ' + str(proxy) 
    logger.sendToLog(proxy_log_message, 'INFO')
    return proxy
