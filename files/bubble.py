#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from play import playNotification
#notifySend use notify-send program in user's system for sending notifications
#and use playNotification function in play.py file for playing sound notifications
def notifySend(message1,message2,time,sound):
    if sound == 'ok':
        playNotification('notifications/ok.ogg')
    elif sound == 'fail':
        playNotification('notifications/fail.ogg')
    elif sound == 'warning':
        playNotification('notifications/you.ogg')
    elif sound == 'critical':
        playNotification('notifications/connection.ogg')
    time = str(time)
    message1 = str(message1)
    message2 = str(message2)
    os.system("notify-send --icon='/usr/share/persepolis/icon.svg' --app-name='Persepolis Download Manager' --expire-time='" + time + "' '" +  message1 +  "' \ '" + message2 +  "' "  )

