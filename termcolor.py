# -*-coding: utf-8 -*-


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    GRAY = '\033[90m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print(bcolors.WARNING + 'Warning:No active, Continue' + bcolors.ENDC)
print(bcolors.HEADER + 'Header' + bcolors.ENDC)
print(bcolors.OKBLUE + 'Blue' + bcolors.ENDC)
print(bcolors.OKGREEN + 'Green' + bcolors.ENDC)
print(bcolors.GRAY + 'Gray' + bcolors.ENDC)
print(bcolors.FAIL + 'Fail' + bcolors.ENDC)
print(bcolors.BOLD + 'BOLD' + bcolors.ENDC)
print(bcolors.UNDERLINE + 'Underline' + bcolors.ENDC)
