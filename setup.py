from check import Check
import subprocess
def Main():
    try:
        chk = Check()
        if chk.check_PyQt() == False:
            print ("PyQt5 Is Not Installed!")
            sys.exit()
        elif chk.check_requests() == False:
            print ("requests Is Not installed!")
            sys.exit()
        subprocess.call(["./install"])
    except:
        print ("Error!")
if __name__ == "__main__":
    Main()
