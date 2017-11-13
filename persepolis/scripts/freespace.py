import os


def free_space(dir):
    try:
        dir_space = os.statvfs(dir)
    except Exception as e:
        pass
        # log in to the log file

    free = dir_space.f_bavail * dir_space.f_frsize / 1024
    return free  # in kb
