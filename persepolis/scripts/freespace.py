from persepolis.scripts import logger


def freeSpace(dir):
    try:
        import psutil
    except:
        logger.sendToLog("psutil in not installed!", "ERROR")

        return None

    try:
        dir_space = psutil.disk_usage(dir)
        free_space = dir_space.free
        return int(free_space)

    except Exception as e:
        # log in to the log file
        logger.sendToLog("persepolis couldn't find free space value:\n" + str(e), "ERROR")

        return None


