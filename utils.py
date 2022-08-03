import platform


def isWindows() -> bool:
    return platform.system().lower() == 'windows'


def isLinux() -> bool:
    return platform.system().lower() == 'linux'
