TEMPLATE = app
TARGET = ts
INCLUDEPATH += persepolis


# Input
SOURCES +=  persepolis/gui/about_ui.py \
            persepolis/gui/addlink_ui.py \
            persepolis/gui/after_download_ui.py \
            persepolis/gui/log_window_ui.py \
            persepolis/gui/progress_ui.py \
            persepolis/gui/setting_ui.py \
            persepolis/gui/text_queue_ui.py
TRANSLATIONS += persepolis/gui/locale/LOCALE/about_ui.ts \
            persepolis/gui/locales/LOCALE/addlink_ui.ts \
            persepolis/gui/locales/LOCALE/after_download_ui.ts \
            persepolis/gui/locales/LOCALE/log_window_ui.ts \
            persepolis/gui/locales/LOCALE/progress_ui.ts \
            persepolis/gui/locales/LOCALE/setting_ui.ts \
            persepolis/gui/locales/LOCALE/text_queue_ui.ts

