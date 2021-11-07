import platform
import os

# I created this file just to organize things and avoid having
# a ton of files on the main directory
def main():
    system = platform.system().lower()
    if system == "windows":
        os.system("cd src & python Main.py")
    elif system == "linux":
        os.system("cd src; python3 Main.py")

if __name__ == "__main__":
    main()
