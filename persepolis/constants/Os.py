class OS:
    LINUX = 'Linux'
    WINDOWS = 'Windows'
    FREE_BSD = 'FreeBSD'
    OPEN_BSD = 'OpenBSD'
    OSX = DARWIN = 'Darwin'
    BSD_FAMILY = [FREE_BSD, OPEN_BSD]
    UNIX_LIKE = BSD_FAMILY + [LINUX]
    LIST = [LINUX, WINDOWS, FREE_BSD, OPEN_BSD, OSX]
