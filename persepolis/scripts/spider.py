# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from persepolis.scripts.useful_tools import humanReadableSize
from requests.cookies import cookiejar_from_dict
from http.cookies import SimpleCookie
import requests


# for more information about "requests" library , please see
# http://docs.python-requests.org/en/master/


# spider function finds name of file and file size from header
def spider(add_link_dictionary):

    # get user's download request from add_link_dictionary
    link = add_link_dictionary['link']
    ip = add_link_dictionary['ip']
    port = add_link_dictionary['port']
    proxy_user = add_link_dictionary['proxy_user']
    proxy_passwd = add_link_dictionary['proxy_passwd']
    download_user = add_link_dictionary['download_user']
    download_passwd = add_link_dictionary['download_passwd']
    header = add_link_dictionary['header']
    out = add_link_dictionary['out']
    user_agent = add_link_dictionary['user_agent']
    raw_cookies = add_link_dictionary['load_cookies']
    referer = add_link_dictionary['referer']

    # define a requests session
    requests_session = requests.Session()
    if ip:
        ip_port = 'http://' + str(ip) + ":" + str(port)
        if proxy_user:
            ip_port = 'http://' + proxy_user + ':' + proxy_passwd + '@' + ip_port
        # set proxy to the session
        requests_session.proxies = {'http': ip_port}

    if download_user:
        # set download user pass to the session
        requests_session.auth = (download_user, download_passwd)

    # set cookies
    if raw_cookies:
        cookie = SimpleCookie()
        cookie.load(raw_cookies)

        cookies = {key: morsel.value for key, morsel in cookie.items()}
        requests_session.cookies = cookiejar_from_dict(cookies)

    # set referer
    if referer:
        requests_session.headers.update({'referer': referer})  # setting referer to the session

    # set user_agent
    if user_agent:
        requests_session.headers.update({'user-agent': user_agent})  # setting user_agent to the session

    # find headers
    try:
        response = requests_session.head(link, timeout=2.50)
        header = response.headers
    except:
        header = {}

    filename = None
    file_size = None
    if 'Content-Disposition' in header.keys():  # checking if filename is available
        content_disposition = header['Content-Disposition']
        if content_disposition.find('filename') != -1:
            filename_splited = content_disposition.split('filename=')
            filename_splited = filename_splited[-1]

            # getting file name in desired format
            filename = filename_splited.strip()

    if not(filename):
        filename = link.split('/')[-1]

    # if user set file name before in add_link_dictionary['out'],
    # then set "out" for filename
    if out:
        filename = out

    # check if file_size is available
    if 'Content-Length' in header.keys():
        file_size = int(header['Content-Length'])

        # converting file_size to KiB or MiB or GiB
        file_size = humanReadableSize(file_size)

    # return results
    return filename, file_size


# this function finds and returns file name for links.
def queueSpider(add_link_dictionary):
    # get download information from add_link_dictionary
    for i in ['link', 'header', 'out', 'user_agent', 'load_cookies', 'referer']:
        if not (i in add_link_dictionary):
            add_link_dictionary[i] = None

    link = add_link_dictionary['link']
    header = add_link_dictionary['header']
    user_agent = add_link_dictionary['user_agent']
    raw_cookies = add_link_dictionary['load_cookies']
    referer = add_link_dictionary['referer']

    requests_session = requests.Session()  # defining a requests Session

    if raw_cookies:  # set cookies
        cookie = SimpleCookie()
        cookie.load(raw_cookies)

        cookies = {key: morsel.value for key, morsel in cookie.items()}
        requests_session.cookies = cookiejar_from_dict(cookies)

    if referer:
        # set referer to the session
        requests_session.headers.update({'referer': referer})

    if user_agent:
        # set user_agent to the session
        requests_session.headers.update({'user-agent': user_agent})

    # find headers
    try:
        response = requests_session.head(link, timeout=2.50)
        header = response.headers
    except:
        header = {}
    filename = None
    if 'Content-Disposition' in header.keys():  # checking if filename is available
        content_disposition = header['Content-Disposition']
        if content_disposition.find('filename') != -1:
            filename_splited = content_disposition.split('filename=')
            filename_splited = filename_splited[-1]
            # getting file name in desired format
            filename = filename_splited.strip()

    if not(filename):
        filename = link.split('/')[-1]

    return filename


def addLinkSpider(add_link_dictionary):
    # get user's download information from add_link_dictionary
    for i in ['link', 'header', 'out', 'user_agent', 'load_cookies', 'referer']:
        if not (i in add_link_dictionary):
            add_link_dictionary[i] = None

    link = add_link_dictionary['link']
    header = add_link_dictionary['header']
    user_agent = add_link_dictionary['user_agent']
    raw_cookies = add_link_dictionary['load_cookies']
    referer = add_link_dictionary['referer']

    requests_session = requests.Session()  # defining a requests Session

    if raw_cookies:  # set cookies
        cookie = SimpleCookie()
        cookie.load(raw_cookies)

        cookies = {key: morsel.value for key, morsel in cookie.items()}
        requests_session.cookies = cookiejar_from_dict(cookies)

    if referer:
        # set referer to the session
        requests_session.headers.update({'referer': referer})

    if user_agent:
        # set user_agent to the session
        requests_session.headers.update({'user-agent': user_agent})

    # find headers
    try:
        response = requests_session.head(link, timeout=2.50)
        header = response.headers
    except:
        header = {}

    # find file size
    file_size = None
    if 'Content-Length' in header.keys():  # checking if file_size is available
        file_size = int(header['Content-Length'])

        # converting file_size to KiB or MiB or GiB
        file_size = str(humanReadableSize(file_size))

    # find file name
    file_name = None
    if 'Content-Disposition' in header.keys():  # checking if filename is available
        content_disposition = header['Content-Disposition']
        if content_disposition.find('filename') != -1:
            filename_splited = content_disposition.split('filename=')
            filename_splited = filename_splited[-1]
            # getting file name in desired format
            file_name = filename_splited.strip()

    return file_name, file_size  # If no Content-Length ? fixed it.
