import urllib, requests,os

# TODO: mac os socks proxy

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

        # check proxy enabled as manually
        if proxy['ProxyType'].split('\n')[0] == '1' :
            # get ftp proxy
            try :
                ftpProxyPort = proxy['ftpProxy'].split(' ')[1].replace("/", "").replace("\n", "")
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
                httpProxyPort = proxy['httpProxy'].split(' ')[1].replace("/", "").replace("\n", "")
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
                httpsProxyPort = proxy['httpsProxy'].split(' ')[1].replace("/", "").replace("\n", "")
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
                socksProxyPort = proxy['socksProxy'].split(' ')[1].replace("/", "").replace("\n", "")
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

        # proxy disabled
        else:
            # all print just for debugung
            print('proxy disabled')


    # if it is windows,mac and other linux desktop
    else:
        # get proxies
        proxy = urllib.request.getproxies()

        # get http proxy
        try:
            httpProxyIp = 'http:' + proxy['http'].split(':')[1]
            httpProxyPort = proxy['http'].split(':')[2].replace("/", "").replace("\n", "")
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
            httpsProxyPort = proxy['https'].split(':')[2].replace("/", "").replace("\n", "")
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
            ftpProxyPort = proxy['ftp'].split(':')[2].replace("/", "").replace("\n", "")
            # all print just for debugung
            print('FTP Proxy IP : ' + ftpProxyIp)
            print('FTP Proxy Port : ' + ftpProxyPort)
        except Exception as e :
            # all print just for debugung
            print("Error")
            ftpProxyIp = False

        # get socks proxy
        try:
            # if it is gnome
            if os.environ.get('XDG_CURRENT_DESKTOP') == 'GNOME' :
                socksProxyIp = 'socks:' + proxy['all'].split(':')[1]
                socksProxyPort = proxy['all'].split(':')[2].replace("/", "").replace("\n", "")
                # all print just for debugung
                print('Socks Proxy IP : ' + socksProxyIp)
                print('Socks Proxy Port : ' + socksProxyPort)
            # other desktop
            else:
                socksProxyIp = 'socks:' + proxy['socks'].split(':')[1]
                socksProxyPort = proxy['socks'].split(':')[2].replace("/", "").replace("\n", "")
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


if __name__ == '__main__':
    getproxy()
