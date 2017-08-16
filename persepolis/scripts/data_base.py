# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sqlite3


# download manager config folder .
if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
    config_folder = os.path.join(
        str(home_address), ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(
        str(home_address), "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows':
    config_folder = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_download_manager')

# persepolis main data base path
persepolis_db_path = os.path.join(config_folder, 'persepolis.db')

# persepolis tmp folder path
if os_type != 'Windows':
    user_name_split = home_address.split('/')
    user_name = user_name_split[2]
    persepolis_tmp = '/tmp/persepolis_' + user_name
else:
    persepolis_tmp = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_tmp')

# plugins.db is store links, when browser plugins are send new links.
plugins_db_path = os.path.join(persepolis_tmp, 'plugins.db')

   
class PluginsDB():
    def __init__(self):
        # plugins_db_connection
        self.plugins_db_connection = sqlite3.connect(plugins_db_path)

        # plugins_db_cursor
        self.plugins_db_cursor = plugins_db_connection.cursor()

    # plugins_db_table contains links that sends by browser plugins. 
    def createTables(self):
        self.plugins_db_cursor.execute("""CREATE TABLE IF NOT EXISTS plugins_db_table(
                                                                                ID INTEGER PRIMARY KEY,
                                                                                link TEXT,
                                                                                referer TEXT,
                                                                                load_cookies TEXT,
                                                                                user_agent TEXT,
                                                                                header TEXT,
                                                                                out TEXT,
                                                                                status TEXT
                                                                                )""") 
    # insert new item in plugins_db_table
    def insertInPluginsTable(self, link, referer, load_cookies, user_agent, header, out):
        self.plugins_db_cursor.execute("""INSERT INTO plugins_db_table VALUES(
                                                                    NULL,
                                                                    :link,
                                                                    :referer,
                                                                    :load_cookies,
                                                                    :user_agent,
                                                                    :header,
                                                                    :out,
                                                                    'new'
                                                                        )""", {
                                                                            'link': link,
                                                                            'referer': referer,
                                                                            'load_cookies': load_cookies,
                                                                            'user_agent': user_agent,
                                                                            'header': header,
                                                                            'out': out
                                                                            })

        self.plugins_db_connection.commit()

    # close connections
    def closeConnections(self):
        self.plugins_db_connection.close()
        self.plugins_db_cursor.close()




class PersepolisDB():
    def __init__(self):
        # persepolis_db_connection
        self.persepolis_db_connection = sqlite3.connect(persepolis_db_path)

        # persepolis_db_cursor
        self.persepolis_db_cursor = persepolis_db_connection.cursor()

    def createTables(self):
    # queues_list contains name of categories and category settings
        self.persepolis_db_cursor.execute("""CREATE TABLE IF NOT EXISTS category_db_table(
                                                                        category TEXT PRIMARY KEY,
                                                                        start_time_enable TEXT,
                                                                        start_hour TEXT,
                                                                        start_minute TEXT,
                                                                        end_time_enable TEXT,
                                                                        end_hour TEXT,
                                                                        end_minute TEXT,
                                                                        reverse TEXT,
                                                                        limit_enable TEXT,
                                                                        limit_value TEXT,
                                                                        after_download TEXT
                                                                                    )""")


    # download table contains download table download items information
        self.persepolis_db_cursor.execute("""CREATE TABLE IF NOT EXISTS download_db_table(
                                                                                    file_name TEXT,
                                                                                    status TEXT,
                                                                                    size TEXT,
                                                                                    downloaded_size TEXT,
                                                                                    percent TEXT,
                                                                                    connections TEXT,
                                                                                    rate TEXT,
                                                                                    estimate_time_left TEXT,
                                                                                    gid TEXT PRIMARY KEY,
                                                                                    link TEXT,
                                                                                    firs_try_date TEXT,
                                                                                    last_try_date TEXT,
                                                                                    category TEXT,
                                                                                    FOREIGN KEY(category) REFERENCES category_db_table(category)
                                                                                    ON UPDATE CASCADE
                                                                                    ON DELETE CASCADE
                                                                                         )""")


    # addlink_db_table contains addlink window download information
        self.persepolis_db_cursor.execute("""CREATE TABLE IF NOT EXISTS addlink_db_table(
                                                                                ID INTEGER PRIMARY KEY,
                                                                                gid TEXT,
                                                                                last_try_date TEXT,
                                                                                firs_try_date TEXT,
                                                                                out TEXT,
                                                                                final_download_path TEXT,
                                                                                start_hour TEXT,
                                                                                start_minute TEXT,
                                                                                end_hour TEXT,
                                                                                end_minute TEXT,
                                                                                link TEXT,
                                                                                ip TEXT,
                                                                                port TEXT,
                                                                                proxy_user TEXT,
                                                                                proxy_passwd TEXT,
                                                                                download_user TEXT,
                                                                                download_passwd TEXT,
                                                                                connections TEXT,
                                                                                limit TEXT,
                                                                                download_path TEXT,
                                                                                referer TEXT,
                                                                                load_cookies TEXT,
                                                                                user_agent TEXT,
                                                                                header TEXT,
                                                                                after_download TEXT,
                                                                                FOREIGN KEY(gid) REFERENCES download_db_table(gid) 
                                                                                ON UPDATE CASCADE 
                                                                                ON DELETE CASCADE 
                                                                                    )""") 


    # insert new category in category_db_table
    def insertInCategoryTable(self, category, start_time_enable,start_hour,
                            start_minute,end_time_enable, end_hour, end_minute,
                            reverse, limit_enable, limit_value, after_download):    

        self.persepolis_db_cursor.execute("""INSERT INTO category_db_table VALUES(
                                                                            :category,
                                                                            :start_time_enable,
                                                                            :start_hour,
                                                                            :start_minute,
                                                                            :end_time_enable,
                                                                            :end_hour,
                                                                            :end_minute,
                                                                            :reverse,
                                                                            :limit_enable,
                                                                            :limit_value,
                                                                            :after_download
                                                                            )""", {
                                                                                'category': category,
                                                                                'start_time_enable': start_time_enable,
                                                                                'start_hour': start_hour,
                                                                                'start_minute': start_minute,
                                                                                'end_time_enable': end_time_enable,
                                                                                'end_hour': end_hour,
                                                                                'end_minute': end_minute,
                                                                                'reverse': reverse,
                                                                                'limit_enable': limit_enable,
                                                                                'limit_value': limit_value,
                                                                                'after_download': after_download
                                                                                })
        self.persepolis_db_connection.commit()
 

    # insert in to download_db_table in persepolis.db
    def insertInDownloadTable(self, file_name, status, size, downloaded_size,
                            percent, connections, rate, estimate_time_left,
                            gid, link, firs_try_date, last_try_date):

        self.persepolis_db_cursor.execute("""INSERT INTO download_db_table VALUES(
                                                                            :file_name,
                                                                            :status,
                                                                            :size,
                                                                            :downloaded_size,
                                                                            :percent,
                                                                            :connections,
                                                                            :rate,
                                                                            :estimate_time_left,
                                                                            :gid,
                                                                            :link,
                                                                            :firs_try_date,
                                                                            :last_try_date,
                                                                            :category
                                                                            )""", {
                                                                                'file_name': file_name,
                                                                                'status': status,
                                                                                'size': size,
                                                                                'downloaded_size': downloaded_size,
                                                                                'percent': percent,
                                                                                'connections': connections,
                                                                                'rate': rate,
                                                                                'estimate_time_left': estimate_time_left,
                                                                                'gid': gid,
                                                                                'link': link,
                                                                                'firs_try_date': firs_try_date,
                                                                                'last_try_date': last_try_date,
                                                                                'category': category
                                                                                    })
        self.persepolis_db_connection.commit()

    # insert in addlink table in persepolis.db 
    def insertInAddLinkTable(self, gid, last_try_date, firs_try_date, out, final_download_path,
                            start_hour, start_minute, end_hour, end_minute, link,
                            ip, port, proxy_user, proxy_passwd, download_user,
                            download_passwd, connections, limit, download_path,
                            referer, load_cookies, user_agent, header, after_download):

        self.persepolis_db_cursor.execute("""INSERT INTO addlink_db_table VALUES(NULL,
                                                                                :gid,
                                                                                :last_try_date,
                                                                                :firs_try_date,
                                                                                :out,
                                                                                :final_download_path,
                                                                                :start_hour,
                                                                                :start_minute,
                                                                                :end_hour,
                                                                                :end_minute,
                                                                                :link,
                                                                                :ip,
                                                                                :port,
                                                                                :proxy_user,
                                                                                :proxy_passwd,
                                                                                :download_user,
                                                                                :download_passwd,
                                                                                :connections,
                                                                                :limit,
                                                                                :download_path,
                                                                                :referer,
                                                                                :load_cookies,
                                                                                :user_agent,
                                                                                :header,
                                                                                :after_download
                                                                                )""", {
                                                                                    'gid' :gid,
                                                                                    'last_try_date': last_try_date,
                                                                                    'firs_try_date': firs_try_date,
                                                                                    'out': out,
                                                                                    'final_download_path': final_download_path,
                                                                                    'start_hour': start_hour,
                                                                                    'start_minute': start_minute,
                                                                                    'end_hour': end_hour,
                                                                                    'end_minute': end_minute,
                                                                                    'link': link,
                                                                                    'ip': ip,
                                                                                    'port': port,
                                                                                    'proxy_user': proxy_user,
                                                                                    'proxy_passwd': proxy_passwd,
                                                                                    'download_user': download_user,
                                                                                    'download_passwd': download_passwd,
                                                                                    'connections': connections,
                                                                                    'limit': limit,
                                                                                    'download_path' :download_path,
                                                                                    'referer': referer,
                                                                                    'load_cookies': load_cookies,
                                                                                    'user_agent': user_agent,
                                                                                    'header': header,
                                                                                    'after_download': after_download
                                                                                    })
    self.persepolis_db_connection.commit() 
    
 

    # return download information in download_db_table with special gid.
    def searchGidInDownloadTable(self, gid):
        self.persepolis_db_cursor.execute("""SELECT * FROM download_db_table WHERE gid = {}""".format(str(gid)))
        return self.persepolis_db_cursor.fetchall()

    # return all items in download_db_table
    def retrnAllItemsInDownloadTable(self):
        self.persepolis_db_cursor.execute("""SELECT * FROM download_db_table""")
        return self.persepolis_db_cursor.fetchall()


    # return download information in addlink_db_table with special gid.
    def searchGidInAddLinkTable(self, gid):
        self.persepolis_db_cursor.execute("""SELECT * FROM addlink_db_table WHERE gid = {}""".format(str(gid)))
        return self.persepolis_db_cursor.fetchall()

    # return category information in category_db_table
    def searchCategoryInCategoryTable(self, category):
        self.persepolis_db_cursor.execute("""SELECT * FROM category_db_table WHERE category = {}""".format(str(category)))
        return self.persepolis_db_cursor.fetchall()

    # return categories name 
    def categoriesTuple(self):
        self.persepolis_db_cursor.execute("""SELECT category FROM category_db_table""")
        return self.persepolis_db_cursor.fetchall() 



    def setDBTablesToDefaultValue(self):
    # change start_time_enable , end_time_enable , reverse ,
    # limit_enable , after_download value to default value !
        self.persepolis_db_cursor.execute("""UPDATE category_db_table SET start_time_enable = 'no', end_time_enable = 'no',
                                        reverse = 'no', limit_enable = 'no', after_download = 'no'""")

    # change status of download to 'stopped' if status isn't 'compelete' or 'error'
        self.persepolis_db_cursor.execute("""UPDATE download_db_table SET status = 'stopped' 
                                        WHERE status NOT IN ('compelete', 'error')""")

    # change start_hour and start_minute and end_hour and end_minute and
    # after_download value to None in addlink_db_table!
        self.persepolis_db_cursor.execute("""UPDATE addlink_db_table SET start_hour = NULL, start_minute = NULL,
                                    end_hour = NULL, end_minute = NULL, after_download = NULL""")
    
        self.persepolis_db_connection.commit()


    # close connections
    def closeConnections(self):
        self.persepolis_db_cursor.close()
        self.persepolis_db_connection.close()












