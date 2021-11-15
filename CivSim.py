#from src.Settings import LOG_FILE
import platform
#import logging
import os

# I created this file just to organize things and avoid having
# a ton of files on the main directory
def main():

    """
    lvl = logging.DEBUG
    fmt = "%(levelname)s:%(message)s"
    logging.basicConfig(filename=LOG_FILE_TOP, level=lvl, format=fmt) # setting the logging level
    """

    system = platform.system().lower()

    #logging.info(f"Game started on {system}")

    if system == "windows":
        os.system("cd src & python Main.py")
    elif system == "linux":
        os.system("cd src; python3 Main.py")


if __name__ == "__main__":
    main()
