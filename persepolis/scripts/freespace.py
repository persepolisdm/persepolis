import psutil


def free_space(dir):
    try:
        dir_space = psutil.disk_usage(dir)
    except Exception as e:
        pass
        # log in to the log file

    free = dir_space.free / 1024
    return free  # in kb

dir = '/'
print(free_space(dir))
