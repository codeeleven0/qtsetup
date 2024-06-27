from tkinter.messagebox import askyesno, showinfo
from config import INSTALLER_CONFIGURATION
from os import environ, path, remove
from shutil import rmtree
from pyuac import runAsAdmin, isUserAdmin

if __name__ == "__main__" and isUserAdmin():
    sf = path.join(f"{environ['appdata']}\\Microsoft\\Windows\\Start Menu\\Programs", INSTALLER_CONFIGURATION["name"])
    pf = path.join(environ["ProgramFiles(x86)"], INSTALLER_CONFIGURATION["name"])
    d = path.join(path.join(environ["Public"], "Desktop"), INSTALLER_CONFIGURATION["name"] + ".lnk")
    if askyesno("Uninstall", "Do you want to uninstall " + INSTALLER_CONFIGURATION["name"] + "?"):
        try:
            rmtree(sf, ignore_errors=True)
            rmtree(pf, ignore_errors=True)
            remove(d)
        finally:
            showinfo("", "Uninstalled.")
    else:
        showinfo("", "Abort.")
elif __name__ == "__main__":
    runAsAdmin()
