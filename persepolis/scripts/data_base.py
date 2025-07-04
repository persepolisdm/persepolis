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

from persepolis.scripts.useful_tools import determineConfigFolder
from time import sleep
import sqlite3
import random
import ast
import os

# download manager config folder .
config_folder = determineConfigFolder()

# persepolis tmp folder path
persepolis_tmp = os.path.join(config_folder, 'persepolis_tmp')


# This class manages TempDB
# TempDB contains gid of active downloads in every session.
class TempDB():
    def __init__(self):
        # temp_db saves in RAM
        # temp_db_connection

        self.temp_db_connection = sqlite3.connect(':memory:', check_same_thread=False)

        # temp_db_cursor
        self.temp_db_cursor = self.temp_db_connection.cursor()

        # create a lock for data base
        self.lock = False

    # this method locks data base.
    # this is pervent accessing data base simultaneously.
    def lockCursor(self):
        while self.lock:
            rand_float = random.uniform(0, 0.5)
            sleep(rand_float)

        self.lock = True

    # temp_db_table contains gid of active downloads.

    def createTables(self):
        # lock data base
        self.lockCursor()
        self.temp_db_cursor.execute("""CREATE TABLE IF NOT EXISTS single_db_table(
                                                                                ID INTEGER,
                                                                                gid TEXT PRIMARY KEY,
                                                                                status TEXT,
                                                                                shutdown TEXT
                                                                                )""")

        self.temp_db_cursor.execute("""CREATE TABLE IF NOT EXISTS queue_db_table(
                                                                                ID INTEGER,
                                                                                category TEXT PRIMARY KEY,
                                                                                shutdown TEXT
                                                                                )""")

        self.temp_db_connection.commit()
        self.lock = False

    # insert new item in single_db_table
    def insertInSingleTable(self, gid):
        # lock data base
        self.lockCursor()
        self.temp_db_cursor.execute("""INSERT INTO single_db_table VALUES(
                                                                NULL,
                                                                '{}',
                                                                'active',
                                                                NULL)""".format(gid))

        self.temp_db_connection.commit()
        self.lock = False

    # insert new item in queue_db_table
    def insertInQueueTable(self, category):
        # lock data base
        self.lockCursor()
        self.temp_db_cursor.execute("""INSERT INTO queue_db_table VALUES(
                                                                NULL,
                                                                '{}',
                                                                NULL)""".format(category))

        self.temp_db_connection.commit()
        self.lock = False

    # this method updates single_db_table
    def updateSingleTable(self, dict_):
        # lock data base
        self.lockCursor()
        keys_list = ['gid',
                     'shutdown',
                     'status'
                     ]

        for key in keys_list:
            # if a key is missed in dict_,
            # then add this key to the dict_ and assign None value for the key.
            if key not in dict_.keys():
                dict_[key] = None

        # update data base if value for the keys is not None
        self.temp_db_cursor.execute("""UPDATE single_db_table SET shutdown = coalesce(:shutdown, shutdown),
                                                                status = coalesce(:status, status)
                                                                WHERE gid = :gid""", dict_)

        self.temp_db_connection.commit()

        self.lock = False

    # this method updates queue_db_table
    def updateQueueTable(self, dict_):
        # lock data base
        self.lockCursor()
        keys_list = ['category',
                     'shutdown']

        for key in keys_list:
            # if a key is missed in dict_,
            # then add this key to the dict_ and assign None value for the key.
            if key not in dict_.keys():
                dict_[key] = None

        # update data base if value for the keys is not None
        self.temp_db_cursor.execute("""UPDATE queue_db_table SET shutdown = coalesce(:shutdown, shutdown)
                                                                WHERE category = :category""", dict_)

        self.temp_db_connection.commit()

        self.lock = False

    # this method returns gid of active downloads
    def returnActiveGids(self):
        # lock data base
        self.lockCursor()

        self.temp_db_cursor.execute("""SELECT gid FROM single_db_table WHERE status = 'active'""")

        list_ = self.temp_db_cursor.fetchall()

        self.lock = False
        gid_list = []

        for tuple_ in list_:
            gid = tuple_[0]
            gid_list.append(gid)

        return gid_list

    # this method returns shutdown value for specific gid
    def returnGid(self, gid):
        # lock data base
        self.lockCursor()
        self.temp_db_cursor.execute("""SELECT shutdown, status FROM single_db_table WHERE gid = '{}'""".format(gid))

        list_ = self.temp_db_cursor.fetchall()

        self.lock = False

        tuple_ = list_[0]

        dict_ = {'shutdown': str(tuple_[0]),
                 'status': tuple_[1]}

        return dict_

    # This method returns values of columns for specific category

    def returnCategory(self, category):
        # lock data base
        self.lockCursor()
        self.temp_db_cursor.execute("""SELECT shutdown FROM queue_db_table WHERE category = '{}'""".format(category))

        list_ = self.temp_db_cursor.fetchall()

        self.lock = False

        tuple_ = list_[0]

        dict_ = {'shutdown': tuple_[0]}

        return dict_

    def resetDataBase(self):
        # lock data base
        self.lockCursor()

        # delete all items
        self.temp_db_cursor.execute("""DELETE FROM single_db_table""")
        self.temp_db_cursor.execute("""DELETE FROM queue_db_table""")

        # release lock
        self.lock = False

    # close connections

    def closeConnections(self):
        # lock data base
        self.lockCursor()
        self.temp_db_cursor.close()
        self.temp_db_connection.close()
        self.lock = False


# plugins.db is store links, when browser plugins are send new links.
# This class is managing plugin.db
class PluginsDB():
    def __init__(self):
        # plugins.db file path
        plugins_db_path = os.path.join(persepolis_tmp, 'plugins.db')

        # plugins_db_connection
        self.plugins_db_connection = sqlite3.connect(plugins_db_path, check_same_thread=False)

        # plugins_db_cursor
        self.plugins_db_cursor = self.plugins_db_connection.cursor()

        # create a lock for data base
        self.lock = False

    # this method locks data base.
    # this is pervent accessing data base simultaneously.
    def lockCursor(self):
        while self.lock:
            rand_float = random.uniform(0, 0.5)
            sleep(rand_float)

        self.lock = True

    # plugins_db_table contains links that sends by browser plugins.

    def createTables(self):
        # lock data base
        self.lockCursor()

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
        self.plugins_db_connection.commit()

        # release lock
        self.lock = False

    # insert new items in plugins_db_table
    def insertInPluginsTable(self, list_):
        # lock data base
        self.lockCursor()

        for dict_ in list_:
            self.plugins_db_cursor.execute("""INSERT INTO plugins_db_table VALUES(
                                                                        NULL,
                                                                        :link,
                                                                        :referer,
                                                                        :load_cookies,
                                                                        :user_agent,
                                                                        :header,
                                                                        :out,
                                                                        'new'
                                                                            )""", dict_)

        self.plugins_db_connection.commit()
        # release lock
        self.lock = False

# this method returns all new links in plugins_db_table
    def returnNewLinks(self):
        # lock data base
        self.lockCursor()

        self.plugins_db_cursor.execute("""SELECT link, referer, load_cookies, user_agent, header, out
                                            FROM plugins_db_table
                                            WHERE status = 'new'""")

        list_ = self.plugins_db_cursor.fetchall()

        # chang all rows status to 'old'
        self.plugins_db_cursor.execute("""UPDATE plugins_db_table SET status = 'old'
                                            WHERE status = 'new'""")

        # commit changes
        self.plugins_db_connection.commit()

        # release lock
        self.lock = False

        # create new_list
        new_list = []

        # put the information in tuple_s in dictionary format and add it to new_list
        for tuple_ in list_:
            dict_ = {'link': tuple_[0],
                     'referer': tuple_[1],
                     'load_cookies': tuple_[2],
                     'user_agent': tuple_[3],
                     'header': tuple_[4],
                     'out': tuple_[5]
                     }

            new_list.append(dict_)

        # return results in list format!
        # every member of this list is a dictionary.
        # every dictionary contains download information
        return new_list

    # delete old links from data base
    def deleteOldLinks(self):
        # lock data base
        self.lockCursor()

        self.plugins_db_cursor.execute("""DELETE FROM plugins_db_table WHERE status = 'old'""")
        # commit changes
        self.plugins_db_connection.commit()

        # release lock
        self.lock = False

    # close connections
    def closeConnections(self):
        # lock data base
        self.lockCursor()

        self.plugins_db_cursor.close()
        self.plugins_db_connection.close()

        # release lock
        self.lock = False


# persepolis main data base contains downloads information
# This class is managing persepolis.db
class PersepolisDB():
    def __init__(self):
        # persepolis.db file path
        persepolis_db_path = os.path.join(config_folder, 'persepolis.db')

        # persepolis_db_connection
        self.persepolis_db_connection = sqlite3.connect(persepolis_db_path, check_same_thread=False)

        # turn FOREIGN KEY Support on!
        self.persepolis_db_connection.execute('pragma foreign_keys=ON')

        # persepolis_db_cursor
        self.persepolis_db_cursor = self.persepolis_db_connection.cursor()

        # Create a lock for data base
        self.lock = False

    # this method locks data base.
    # this is pervent accessing data base simultaneously.
    def lockCursor(self):

        while self.lock:
            rand_float = random.uniform(0, 0.5)
            sleep(rand_float)

        self.lock = True

    # queues_list contains name of categories and category settings
    def createTables(self):

        # lock data base
        self.lockCursor()
        # Create category_db_table and add 'All Downloads' and 'Single Downloads' to it
        self.persepolis_db_cursor.execute("""CREATE TABLE IF NOT EXISTS category_db_table(
                                                                category TEXT PRIMARY KEY,
                                                                start_time_enable TEXT,
                                                                start_time TEXT,
                                                                end_time_enable TEXT,
                                                                end_time TEXT,
                                                                reverse TEXT,
                                                                limit_enable TEXT,
                                                                limit_value TEXT,
                                                                after_download TEXT,
                                                                gid_list TEXT
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
                                                                                    first_try_date TEXT,
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
                                                                                out TEXT,
                                                                                start_time TEXT,
                                                                                end_time TEXT,
                                                                                link TEXT,
                                                                                ip TEXT,
                                                                                port TEXT,
                                                                                proxy_user TEXT,
                                                                                proxy_passwd TEXT,
                                                                                download_user TEXT,
                                                                                download_passwd TEXT,
                                                                                connections TEXT,
                                                                                limit_value TEXT,
                                                                                download_path TEXT,
                                                                                referer TEXT,
                                                                                load_cookies TEXT,
                                                                                user_agent TEXT,
                                                                                header TEXT,
                                                                                after_download TEXT,
                                                                                proxy_type TEXT,
                                                                                FOREIGN KEY(gid) REFERENCES download_db_table(gid)
                                                                                ON UPDATE CASCADE
                                                                                ON DELETE CASCADE
                                                                                    )""")
        # video_finder_db_table contains addlink window download information
        self.persepolis_db_cursor.execute("""CREATE TABLE IF NOT EXISTS video_finder_db_table(
                                                                                ID INTEGER PRIMARY KEY,
                                                                                video_gid TEXT,
                                                                                audio_gid TEXT,
                                                                                video_completed TEXT,
                                                                                audio_completed TEXT,
                                                                                muxing_status TEXT,
                                                                                checking TEXT,
                                                                                download_path TEXT,
                                                                                FOREIGN KEY(video_gid) REFERENCES download_db_table(gid)
                                                                                ON DELETE CASCADE,
                                                                                FOREIGN KEY(audio_gid) REFERENCES download_db_table(gid)
                                                                                ON DELETE CASCADE
                                                                                    )""")

        self.persepolis_db_connection.execute("""CREATE TABLE IF NOT EXISTS video_finder_db_table2(
                                                                                ID INTEGER PRIMARY KEY,
                                                                                gid TEXT,
                                                                                download_status TEXT,
                                                                                file_name TEXT,
                                                                                eta TEXT,
                                                                                download_speed_str TEXT,
                                                                                downloaded_size REAL,
                                                                                file_size REAL,
                                                                                download_percent INT,
                                                                                fragments TEXT,
                                                                                error_message TEXT,
                                                                                FOREIGN KEY(gid) REFERENCES download_db_table(gid)
                                                                                ON DELETE CASCADE
                                                                                ON UPDATE CASCADE
                                                                                )""")

        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

        # add 'All Downloads' and 'Single Downloads' to the category_db_table if they wasn't added.
        answer = self.searchCategoryInCategoryTable('All Downloads')

        if not (answer):
            all_downloads_dict = {'category': 'All Downloads',
                                  'start_time_enable': 'no',
                                  'start_time': '0:0',
                                  'end_time_enable': 'no',
                                  'end_time': '0:0',
                                  'reverse': 'no',
                                  'limit_enable': 'no',
                                  'limit_value': '0K',
                                  'after_download': 'no',
                                  'gid_list': '[]'
                                  }

            single_downloads_dict = {'category': 'Single Downloads',
                                     'start_time_enable': 'no',
                                     'start_time': '0:0',
                                     'end_time_enable': 'no',
                                     'end_time': '0:0',
                                     'reverse': 'no',
                                     'limit_enable': 'no',
                                     'limit_value': '0K',
                                     'after_download': 'no',
                                     'gid_list': '[]'
                                     }

            self.insertInCategoryTable(all_downloads_dict)
            self.insertInCategoryTable(single_downloads_dict)

        # add default queue with the name 'Scheduled Downloads'
        answer = self.searchCategoryInCategoryTable('Scheduled Downloads')
        if not (answer):
            scheduled_downloads_dict = {'category': 'Scheduled Downloads',
                                        'start_time_enable': 'no',
                                        'start_time': '0:0',
                                        'end_time_enable': 'no',
                                        'end_time': '0:0',
                                        'reverse': 'no',
                                        'limit_enable': 'no',
                                        'limit_value': '0K',
                                        'after_download': 'no',
                                        'gid_list': '[]'
                                        }
            self.insertInCategoryTable(scheduled_downloads_dict)

    # insert new category in category_db_table
    def insertInCategoryTable(self, dict_):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""INSERT INTO category_db_table VALUES(
                                                                            :category,
                                                                            :start_time_enable,
                                                                            :start_time,
                                                                            :end_time_enable,
                                                                            :end_time,
                                                                            :reverse,
                                                                            :limit_enable,
                                                                            :limit_value,
                                                                            :after_download,
                                                                            :gid_list
                                                                            )""", dict_)
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    # insert in to download_db_table in persepolis.db

    def insertInDownloadTable(self, list_):
        # lock data base
        self.lockCursor()

        for dict_ in list_:
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
                                                                            :first_try_date,
                                                                            :last_try_date,
                                                                            :category
                                                                            )""", dict_)

        # commit changes
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

        if len(list_) != 0:
            # item must be inserted to gid_list of 'All Downloads' and gid_list of category
            # find download category and gid
            category = dict_['category']

            # get category_dict from data base
            category_dict = self.searchCategoryInCategoryTable(category)

            # get all_downloads_dict from data base
            all_downloads_dict = self.searchCategoryInCategoryTable('All Downloads')

            # get gid_list
            category_gid_list = category_dict['gid_list']

            all_downloads_gid_list = all_downloads_dict['gid_list']

            for dict_ in list_:
                gid = dict_['gid']

                # add gid of item to gid_list
                category_gid_list.append(gid)
                all_downloads_gid_list.append(gid)

            # update category_db_table
            self.updateCategoryTable([all_downloads_dict])
            self.updateCategoryTable([category_dict])

    # insert in addlink table in persepolis.db

    def insertInAddLinkTable(self, list_):
        # lock data base
        self.lockCursor()

        for dict_ in list_:
            # first column and after_download column is NULL
            self.persepolis_db_cursor.execute("""INSERT INTO addlink_db_table VALUES(NULL,
                                                                                :gid,
                                                                                :out,
                                                                                :start_time,
                                                                                :end_time,
                                                                                :link,
                                                                                :ip,
                                                                                :port,
                                                                                :proxy_user,
                                                                                :proxy_passwd,
                                                                                :download_user,
                                                                                :download_passwd,
                                                                                :connections,
                                                                                :limit_value,
                                                                                :download_path,
                                                                                :referer,
                                                                                :load_cookies,
                                                                                :user_agent,
                                                                                :header,
                                                                                NULL,
                                                                                :proxy_type
                                                                                )""", dict_)
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    def insertInVideoFinderTable(self, list_):
        # lock data base
        self.lockCursor()

        for dictionary in list_:
            # first column is NULL
            self.persepolis_db_cursor.execute("""INSERT INTO video_finder_db_table VALUES(NULL,
                                                                                :video_gid,
                                                                                :audio_gid,
                                                                                :video_completed,
                                                                                :audio_completed,
                                                                                :muxing_status,
                                                                                :checking,
                                                                                :download_path
                                                                                )""", dictionary)
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    def searchGidInVideoFinderTable(self, gid):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute(
            """SELECT * FROM video_finder_db_table WHERE audio_gid = '{}' OR video_gid = '{}'""".format(str(gid), str(gid)))
        result_list = self.persepolis_db_cursor.fetchall()

        # job is done
        self.lock = False

        if result_list:
            tuple_ = result_list[0]
        else:
            return None

        dictionary = {'video_gid': tuple_[1],
                      'audio_gid': tuple_[2],
                      'video_completed': tuple_[3],
                      'audio_completed': tuple_[4],
                      'muxing_status': tuple_[5],
                      'checking': tuple_[6],
                      'download_path': tuple_[7]}

        # return the results
        return dictionary

    def insertInVideoFinderTable2(self, dict_):
        self.lockCursor()
        self.persepolis_db_cursor.execute("""INSERT INTO video_finder_db_table2 VALUES(NULL,
                                                                                :gid,
                                                                                :download_status,
                                                                                :file_name,
                                                                                :eta,
                                                                                :download_speed_str,
                                                                                :downloaded_size,
                                                                                :file_size,
                                                                                :download_percent,
                                                                                :fragments,
                                                                                :error_message
                                                                                )""", dict_)
        self.persepolis_db_connection.commit()
        self.lock = False

    def searchGidInVideoFinderTable2(self, gid):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute(
            """SELECT * FROM video_finder_db_table2 WHERE gid = '{}'""".format(str(gid)))
        result_list = self.persepolis_db_cursor.fetchall()

        # job is done
        self.lock = False

        if result_list:
            tuple_ = result_list[0]
        else:
            return None

        dictionary = {'gid': tuple_[1],
                      'download_status': tuple_[2],
                      'file_name': tuple_[3],
                      'eta': tuple_[4],
                      'download_speed_str': tuple_[5],
                      'downloaded_size': tuple_[6],
                      'file_size': tuple_[7],
                      'download_percent': tuple_[8],
                      'fragments': tuple_[9],
                      'error_message': tuple_[10]}

        # return the results
        return dictionary

    # return download information in download_db_table with special gid.
    def searchGidInDownloadTable(self, gid):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""SELECT * FROM download_db_table WHERE gid = '{}'""".format(str(gid)))
        list_ = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        if list_:
            tuple_ = list_[0]
        else:
            return None

        dict_ = {'file_name': tuple_[0],
                 'status': tuple_[1],
                 'size': tuple_[2],
                 'downloaded_size': tuple_[3],
                 'percent': tuple_[4],
                 'connections': tuple_[5],
                 'rate': tuple_[6],
                 'estimate_time_left': tuple_[7],
                 'gid': tuple_[8],
                 'link': tuple_[9],
                 'first_try_date': tuple_[10],
                 'last_try_date': tuple_[11],
                 'category': tuple_[12]
                 }

        # return results
        return dict_

    # return all items in download_db_table
    # '*' for category, cause that method returns all items.
    def returnItemsInDownloadTable(self, category=None):
        # lock data base
        self.lockCursor()

        if category:
            self.persepolis_db_cursor.execute(
                """SELECT * FROM download_db_table WHERE category = '{}'""".format(category))
        else:
            self.persepolis_db_cursor.execute("""SELECT * FROM download_db_table""")

        rows = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        downloads_dict = {}
        for tuple_ in rows:
            # change format of tuple_ to dictionary
            dict_ = {'file_name': tuple_[0],
                     'status': tuple_[1],
                     'size': tuple_[2],
                     'downloaded_size': tuple_[3],
                     'percent': tuple_[4],
                     'connections': tuple_[5],
                     'rate': tuple_[6],
                     'estimate_time_left': tuple_[7],
                     'gid': tuple_[8],
                     'link': tuple_[9],
                     'first_try_date': tuple_[10],
                     'last_try_date': tuple_[11],
                     'category': tuple_[12]
                     }

            # add dict to the downloads_dict
            # gid is key and dict_ is value
            downloads_dict[tuple_[8]] = dict_

        return downloads_dict

    # this method checks existence of a link in addlink_db_table

    def searchLinkInAddLinkTable(self, link):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""SELECT * FROM addlink_db_table WHERE link = (?)""", (link,))
        list_ = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        if list_:
            return True
        else:
            return False

    # return download information in addlink_db_table with special gid.

    def searchGidInAddLinkTable(self, gid):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""SELECT * FROM addlink_db_table WHERE gid = '{}'""".format(str(gid)))
        list_ = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        if list_:
            tuple_ = list_[0]
        else:
            return None

        dict_ = {'gid': tuple_[1],
                 'out': tuple_[2],
                 'start_time': tuple_[3],
                 'end_time': tuple_[4],
                 'link': tuple_[5],
                 'ip': tuple_[6],
                 'port': tuple_[7],
                 'proxy_user': tuple_[8],
                 'proxy_passwd': tuple_[9],
                 'download_user': tuple_[10],
                 'download_passwd': tuple_[11],
                 'connections': tuple_[12],
                 'limit_value': tuple_[13],
                 'download_path': tuple_[14],
                 'referer': tuple_[15],
                 'load_cookies': tuple_[16],
                 'user_agent': tuple_[17],
                 'header': tuple_[18],
                 'after_download': tuple_[19],
                 'proxy_type': tuple_[20]
                 }

        return dict_

    # return items in addlink_db_table
    # '*' for category, cause that method returns all items.

    def returnItemsInAddLinkTable(self, category=None):
        # lock data base
        self.lockCursor()

        if category:
            self.persepolis_db_cursor.execute(
                """SELECT * FROM addlink_db_table WHERE category = '{}'""".format(category))
        else:
            self.persepolis_db_cursor.execute("""SELECT * FROM addlink_db_table""")

        rows = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        addlink_dict = {}
        for tuple_ in rows:
            # change format of tuple_ to dictionary
            dict_ = {'gid': tuple_[1],
                     'out': tuple_[2],
                     'start_time': tuple_[3],
                     'end_time': tuple_[4],
                     'link': tuple_[5],
                     'ip': tuple_[6],
                     'port': tuple_[7],
                     'proxy_user': tuple_[8],
                     'proxy_passwd': tuple_[9],
                     'download_user': tuple_[10],
                     'download_passwd': tuple_[11],
                     'connections': tuple_[12],
                     'limit_value': tuple_[13],
                     'download_path': tuple_[14],
                     'referer': tuple_[15],
                     'load_cookies': tuple_[16],
                     'user_agent': tuple_[17],
                     'header': tuple_[18],
                     'after_download': tuple_[19],
                     'proxy_type': tuple_[20]
                     }

            # add dict_ to the addlink_dict
            # gid as key and dict_ as value
            addlink_dict[tuple_[1]] = dict_

        return addlink_dict

    # this method updates download_db_table
    def updateDownloadTable(self, list_):
        # lock data base
        self.lockCursor()

        keys_list = ['file_name',
                     'status',
                     'size',
                     'downloaded_size',
                     'percent',
                     'connections',
                     'rate',
                     'estimate_time_left',
                     'gid',
                     'link',
                     'first_try_date',
                     'last_try_date',
                     'category'
                     ]

        for dict_ in list_:
            for key in keys_list:
                # if a key is missed in dict_,
                # then add this key to the dict_ and assign None value for the key.
                if key not in dict_.keys():
                    dict_[key] = None

            # update data base if value for the keys is not None
            self.persepolis_db_cursor.execute("""UPDATE download_db_table SET   file_name = coalesce(:file_name, file_name),
                                                                                    status = coalesce(:status, status),
                                                                                    size = coalesce(:size, size),
                                                                                    downloaded_size = coalesce(:downloaded_size, downloaded_size),
                                                                                    percent = coalesce(:percent, percent),
                                                                                    connections = coalesce(:connections, connections),
                                                                                    rate = coalesce(:rate, rate),
                                                                                    estimate_time_left = coalesce(:estimate_time_left, estimate_time_left),
                                                                                    link = coalesce(:link, link),
                                                                                    first_try_date = coalesce(:first_try_date, first_try_date),
                                                                                    last_try_date = coalesce(:last_try_date, last_try_date),
                                                                                    category = coalesce(:category, category)
                                                                                    WHERE gid = :gid""", dict_)

        # commit the changes
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    # this method updates category_db_table
    def updateCategoryTable(self, list_):
        # lock data base
        self.lockCursor()

        keys_list = ['category',
                     'start_time_enable',
                     'start_time',
                     'end_time_enable',
                     'end_time',
                     'reverse',
                     'limit_enable',
                     'limit_value',
                     'after_download',
                     'gid_list']

        for dict_ in list_:

            # format of gid_list is list and must be converted to string for sqlite3
            if 'gid_list' in dict_.keys():
                dict_['gid_list'] = str(dict_['gid_list'])

            for key in keys_list:
                # if a key is missed in dict_,
                # then add this key to the dict_ and assign None value for the key.
                if key not in dict_.keys():
                    dict_[key] = None

            # update data base if value for the keys is not None
            self.persepolis_db_cursor.execute("""UPDATE category_db_table SET   start_time_enable = coalesce(:start_time_enable, start_time_enable),
                                                                                    start_time = coalesce(:start_time, start_time),
                                                                                    end_time_enable = coalesce(:end_time_enable, end_time_enable),
                                                                                    end_time = coalesce(:end_time, end_time),
                                                                                    reverse = coalesce(:reverse, reverse),
                                                                                    limit_enable = coalesce(:limit_enable, limit_enable),
                                                                                    limit_value = coalesce(:limit_value, limit_value),
                                                                                    after_download = coalesce(:after_download, after_download),
                                                                                    gid_list = coalesce(:gid_list, gid_list)
                                                                                    WHERE category = :category""", dict_)

        # commit changes
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    # this method updates addlink_db_table
    def updateAddLinkTable(self, list_):
        # lock data base
        self.lockCursor()

        keys_list = ['gid',
                     'out',
                     'start_time',
                     'end_time',
                     'link',
                     'ip',
                     'port',
                     'proxy_user',
                     'proxy_passwd',
                     'download_user',
                     'download_passwd',
                     'connections',
                     'limit_value',
                     'download_path',
                     'referer',
                     'load_cookies',
                     'user_agent',
                     'header',
                     'after_download',
                     'proxy_type']

        for dict_ in list_:
            update_query_set_statements_list = []
            for key in keys_list:
                if key in dict_.keys():
                    update_query_set_statements_list.append(f"{key} = :{key}")

            update_query_set_statements = ' ,\n '.join(update_query_set_statements_list)
            update_query = f"""UPDATE addlink_db_table SET
                               {update_query_set_statements}
                               WHERE gid = :gid
            """
            if len(update_query_set_statements_list) > 0:
                self.persepolis_db_cursor.execute(update_query, dict_)
        # commit the changes!
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    def updateVideoFinderTable(self, list_):

        # lock data base
        self.lockCursor()

        keys_list = ['video_gid',
                     'audio_gid',
                     'video_completed',
                     'audio_completed',
                     'muxing_status',
                     'checking']

        for dictionary in list_:
            for key in keys_list:
                # if a key is missed in dict_,
                # then add this key to the dict_ and assign None value for the key.
                if key not in dictionary.keys():
                    dictionary[key] = None

            if dictionary['video_gid']:
                # update data base if value for the keys is not None
                self.persepolis_db_cursor.execute("""UPDATE video_finder_db_table SET video_completed = coalesce(:video_completed, video_completed),
                                                                                audio_completed = coalesce(:audio_completed, audio_completed),
                                                                                muxing_status = coalesce(:muxing_status, muxing_status),
                                                                                checking = coalesce(:checking, checking),
                                                                                download_path = coalesce(:download_path, download_path)
                                                                                WHERE video_gid = :video_gid""", dictionary)
            elif dictionary['audio_gid']:
                # update data base if value for the keys is not None
                self.persepolis_db_cursor.execute("""UPDATE video_finder_db_table SET video_completed = coalesce(:video_completed, video_completed),
                                                                                audio_completed = coalesce(:audio_completed, audio_completed),
                                                                                muxing_status = coalesce(:muxing_status, muxing_status),
                                                                                checking = coalesce(:checking, checking),
                                                                                download_path = coalesce(:download_path, download_path)
                                                                                WHERE audio_gid = :audio_gid""", dictionary)

        # commit the changes!
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    def updateVideoFinderTable2(self, dict_):
        # lock data base
        self.lockCursor()
        keys_list = ['gid',
                     'download_status',
                     'file_name',
                     'eta',
                     'download_speed_str',
                     'downloaded_size',
                     'file_size',
                     'download_percent',
                     'fragments',
                     'error_message']

        for key in keys_list:
            if key not in dict_.keys():
                dict_[key] = None

        self.persepolis_db_cursor.execute("""UPDATE video_finder_db_table2 SET download_status = coalesce(:download_status, download_status),
                                                                file_name = coalesce(:file_name, file_name),
                                                                eta = coalesce(:eta, eta),
                                                                download_speed_str = coalesce(:download_speed_str, download_speed_str),
                                                                downloaded_size = coalesce(:downloaded_size, downloaded_size),
                                                                file_size = coalesce(:file_size, file_size),
                                                                download_percent = coalesce(:download_percent, download_percent),
                                                                fragments = coalesce(:fragments, fragments),
                                                                error_message = coalesce(:error_message, error_message)
                                                                WHERE gid = :gid""", dict_)

        self.persepolis_db_connection.commit()

        self.lock = False

    def setDefaultGidInAddlinkTable(self, gid, start_time=False, end_time=False, after_download=False):
        # lock data base
        self.lockCursor()

        # change value of start_time and end_time and after_download for special gid to NULL value
        if start_time:
            self.persepolis_db_cursor.execute("""UPDATE addlink_db_table SET start_time = NULL
                                                                        WHERE gid = '{}' """.format(gid))
        if end_time:
            self.persepolis_db_cursor.execute("""UPDATE addlink_db_table SET end_time = NULL
                                                                        WHERE gid = '{}' """.format(gid))
        if after_download:
            self.persepolis_db_cursor.execute("""UPDATE addlink_db_table SET after_download = NULL
                                                                        WHERE gid = '{}' """.format(gid))

        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    # return category information in category_db_table

    def searchCategoryInCategoryTable(self, category):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute(
            """SELECT * FROM category_db_table WHERE category = '{}'""".format(str(category)))
        list_ = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        if list_:
            tuple_ = list_[0]
        else:
            return None

        # convert string to list
        gid_list = ast.literal_eval(tuple_[9])

        # create a dictionary from results
        dict_ = {'category': tuple_[0],
                 'start_time_enable': tuple_[1],
                 'start_time': tuple_[2],
                 'end_time_enable': tuple_[3],
                 'end_time': tuple_[4],
                 'reverse': tuple_[5],
                 'limit_enable': tuple_[6],
                 'limit_value': tuple_[7],
                 'after_download': tuple_[8],
                 'gid_list': gid_list
                 }

        # return dictionary
        return dict_

    # return categories name
    def categoriesList(self):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""SELECT category FROM category_db_table ORDER BY ROWID""")
        rows = self.persepolis_db_cursor.fetchall()

        # create a list from categories name
        queues_list = []

        for tuple_ in rows:
            queues_list.append(tuple_[0])

        # job is done! open the lock
        self.lock = False

        # return the list
        return queues_list

    def setDBTablesToDefaultValue(self):
        # lock data base
        self.lockCursor()

        # change start_time_enable , end_time_enable , reverse ,
        # limit_enable , after_download value to default value !
        self.persepolis_db_cursor.execute("""UPDATE category_db_table SET start_time_enable = 'no', end_time_enable = 'no',
                                        reverse = 'no', limit_enable = 'no', after_download = 'no'""")

        # change checking value to no in video_finder_db_table
        self.persepolis_db_cursor.execute("""UPDATE video_finder_db_table SET checking = 'no'""")

        # change status of download to 'stopped' if status isn't 'complete' or 'error'
        self.persepolis_db_cursor.execute("""UPDATE download_db_table SET status = 'stopped'
                                        WHERE status NOT IN ('complete', 'error')""")

        # change start_time and end_time and
        # after_download value to None in addlink_db_table!
        self.persepolis_db_cursor.execute("""UPDATE addlink_db_table SET start_time = NULL,
                                                                        end_time = NULL,
                                                                        after_download = NULL
                                                                                        """)

        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    def findActiveDownloads(self, category=None):
        # lock data base
        self.lockCursor()

        # find download items is download_db_table with status = "downloading" or "waiting" or paused or scheduled
        if category:
            self.persepolis_db_cursor.execute("""SELECT gid FROM download_db_table WHERE (category = '{}') AND (status = 'downloading' OR status = 'waiting'
                                            OR status = 'scheduled' OR status = 'paused' OR status = 'creating download file')""".format(str(category)))
        else:
            self.persepolis_db_cursor.execute("""SELECT gid FROM download_db_table WHERE (status = 'downloading' OR status = 'waiting'
                                            OR status = 'scheduled' OR status = 'paused' OR status = 'creating download file')""")

        # create a list for returning answer
        result = self.persepolis_db_cursor.fetchall()
        gid_list = []

        for result_tuple in result:
            gid_list.append(result_tuple[0])

        # job is done! open the lock
        self.lock = False

        return gid_list

# this method returns items with 'downloading' or 'waiting' or 'creating download file' status
    def returnDownloadingItems(self):
        # lock data base
        self.lockCursor()

        # find download items is download_db_table with status = "downloading" or "waiting" or paused or scheduled
        self.persepolis_db_cursor.execute(
            """SELECT gid FROM download_db_table WHERE (status = 'downloading' OR status = 'waiting' OR status = 'creating download file')""")

        # create a list for returning answer
        result = self.persepolis_db_cursor.fetchall()
        gid_list = []

        for result_tuple in result:
            gid_list.append(result_tuple[0])

        # job is done! open the lock
        self.lock = False

        return gid_list

# this method returns items with 'paused' status.
    def returnPausedItems(self):
        # lock data base
        self.lockCursor()

        # find download items is download_db_table with status = "downloading" or "waiting" or paused or scheduled
        self.persepolis_db_cursor.execute("""SELECT gid FROM download_db_table WHERE (status = 'paused')""")

        # create a list for returning answer
        result = self.persepolis_db_cursor.fetchall()
        gid_list = []

        for result_tuple in result:
            gid_list.append(result_tuple[0])

        # job is done! open the lock
        self.lock = False

        return gid_list

    # return all video_gids and audio_gids in video_finder_db_table
    def returnVideoFinderGids(self):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""SELECT video_gid, audio_gid FROM video_finder_db_table""")

        # create a list for result
        result = self.persepolis_db_cursor.fetchall()

        # job is done! open the lock
        self.lock = False

        gid_list = []
        video_gid_list = []
        audio_gid_list = []

        for result_tuple in result:
            gid_list.append(result_tuple[0])
            video_gid_list.append(result_tuple[0])

            gid_list.append(result_tuple[1])
            audio_gid_list.append(result_tuple[1])

        # job is done
        return gid_list, video_gid_list, audio_gid_list

    # This method deletes a category from category_db_table
    def deleteCategory(self, category):

        # delete gids of this category from gid_list of 'All Downloads'
        category_dict = self.searchCategoryInCategoryTable(category)
        all_downloads_dict = self.searchCategoryInCategoryTable('All Downloads')

        # get gid_list
        category_gid_list = category_dict['gid_list']
        all_downloads_gid_list = all_downloads_dict['gid_list']

        for gid in category_gid_list:
            # delete item from all_downloads_gid_list
            all_downloads_gid_list.remove(gid)

        # update category_db_table
        self.updateCategoryTable([all_downloads_dict])

        # delete category from data_base
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute(
            """DELETE FROM category_db_table WHERE category = '{}'""".format(str(category)))

        # commit changes
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

# this method deletes all items in data_base
    def resetDataBase(self):
        # update gid_list in categories with empty gid_list
        all_downloads_dict = {'category': 'All Downloads', 'gid_list': []}
        single_downloads_dict = {'category': 'Single Downloads', 'gid_list': []}
        scheduled_downloads_dict = {'category': 'Scheduled Downloads', 'gid_list': []}

        self.updateCategoryTable([all_downloads_dict, single_downloads_dict, scheduled_downloads_dict])

        # lock data base
        self.lockCursor()

        # delete all items in category_db_table, except 'All Downloads' and 'Single Downloads'
        self.persepolis_db_cursor.execute(
            """DELETE FROM category_db_table WHERE category NOT IN ('All Downloads', 'Single Downloads', 'Scheduled Downloads')""")
        self.persepolis_db_cursor.execute("""DELETE FROM download_db_table""")
        self.persepolis_db_cursor.execute("""DELETE FROM addlink_db_table""")

        # commit
        self.persepolis_db_connection.commit()

        # release lock
        self.lock = False

# This method deletes a download item from download_db_table
    def deleteItemInDownloadTable(self, gid, category):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.execute("""DELETE FROM download_db_table WHERE gid = '{}'""".format(str(gid)))

        # commit changes
        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

        # delete item from gid_list in category and All Downloads
        for category_name in category, 'All Downloads':
            category_dict = self.searchCategoryInCategoryTable(category_name)

            # get gid_list
            gid_list = category_dict['gid_list']

            # delete item
            if gid in gid_list:
                gid_list.remove(gid)

                # if gid is in video_finder_db_table, both of video_gid and audio_gid must be deleted from gid_list
                video_finder_dictionary = self.searchGidInVideoFinderTable(gid)

                if video_finder_dictionary:
                    video_gid = video_finder_dictionary['video_gid']
                    audio_gid = video_finder_dictionary['audio_gid']

                    if gid == video_gid:
                        gid_list.remove(audio_gid)
                    else:
                        gid_list.remove(video_gid)

                # update category_db_table
                self.updateCategoryTable([category_dict])

# this method replaces:
# GB >> GiB
# MB >> MiB
# KB >> KiB
# Read this link for more information:
# https://en.wikipedia.org/wiki/Orders_of_magnitude_(data)
    def correctDataBase(self):

        # lock data base
        self.lockCursor()

        for units in [['KB', 'KiB'], ['MB', 'MiB'], ['GB', 'GiB']]:
            dict_ = {'old_unit': units[0],
                     'new_unit': units[1]}

            self.persepolis_db_cursor.execute("""UPDATE download_db_table
                    SET size = replace(size, :old_unit, :new_unit)""", dict_)
            self.persepolis_db_cursor.execute("""UPDATE download_db_table
                    SET rate = replace(rate, :old_unit, :new_unit)""", dict_)
            self.persepolis_db_cursor.execute("""UPDATE download_db_table
                    SET downloaded_size = replace(downloaded_size, :old_unit, :new_unit)""", dict_)

        self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    def correctDataBaseForVersion410(self):

        # lock data base
        self.lockCursor()

        # set all proxy_type to http
        # first check for proxy_type's column is exist or not.
        try:
            self.persepolis_db_cursor.execute("""SELECT proxy_type FROM addlink_db_table""")

        except sqlite3.OperationalError:
            # create proxy_type column in addlink_db_table
            self.persepolis_db_cursor.execute("""ALTER TABLE addlink_db_table
                                              ADD proxy_type NULL""")

            # set "http" value for pervious downloads that use proxy
            self.persepolis_db_cursor.execute("""UPDATE addlink_db_table
                                              SET proxy_type = 'http' WHERE ip IS NOT NULL""")

            self.persepolis_db_connection.commit()

        # job is done! open the lock
        self.lock = False

    # close connections

    def correctDataBaseForVersion411(self):
        # lock data base
        self.lockCursor()

        # find gid of all unfinished downloads in download_db_table
        self.persepolis_db_cursor.execute("""SELECT gid FROM download_db_table WHERE status IS NOT 'complete'""")

        result = self.persepolis_db_cursor.fetchall()
        gid_list = []

        for result_tuple in result:
            gid_list.append(result_tuple[0])

        # correct download path
        for gid in gid_list:

            # find download_path
            self.persepolis_db_cursor.execute("""SELECT download_path FROM addlink_db_table WHERE gid = '{}'""".format(str(gid)))
            tuple_ = self.persepolis_db_cursor.fetchone()

            download_path = tuple_[0]

            import platform
            os_type = platform.system()
            home_address = os.path.expanduser("~")

            try:
                if os.lstat(download_path).st_dev == os.lstat(home_address).st_dev:

                    if os_type != 'Windows':
                        download_path_temp = os.path.join(home_address, '.persepolis')
                    else:
                        download_path_temp = os.path.join(
                            home_address, 'AppData', 'Local', 'persepolis')

                else:

                    from persepolis.scripts.osCommands import findMountPoint

                    # Find mount point
                    mount_point = findMountPoint(download_path)

                    # find download_path_temp
                    if os_type == 'Windows':

                        download_path_temp = os.path.join(mount_point, 'persepolis')

                    else:

                        download_path_temp = os.path.join(mount_point, '.persepolis')

                # set download_path_temp as download_path
                self.persepolis_db_cursor.execute("""UPDATE addlink_db_table SET download_path = '{}'
                                                                                WHERE gid = '{}' """.format(download_path_temp, gid))

                self.persepolis_db_connection.commit()
            except:
                pass

        # job is done! open the lock
        self.lock = False

    def closeConnections(self):
        # lock data base
        self.lockCursor()

        self.persepolis_db_cursor.close()
        self.persepolis_db_connection.close()

        # job is done! open the lock
        self.lock = False
