from persepolis.scripts import logger


def freeSpace(dir):
    try:
        import psutil
    except:
        print('ERROR - psutil is not installed!')
        logger.sendToLog("psutil in not installed!", "ERROR")

        return None

    try:
        dir_space = psutil.disk_usage(dir)
        free_space = dir_space.free
        return int(free_space)

    except Exception as e:
        # log in to the log file
        logger.sendToLog("I can't find free space ERROR :\n" + str(e), "ERROR")
        print("I can't find free space:\n" + str(e))

        return None


