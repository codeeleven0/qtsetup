import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QProgressBar, QLineEdit,
                               QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QStyle)
import ctypes
import os
import shutil
import pyuac
from swinlnk.swinlnk import SWinLnk
from config import INSTALLER_CONFIGURATION

application_id = 'codex.games.installer'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(application_id)
finally:
    pass

START_LINK_DIR = f"{os.environ['appdata']}\\Microsoft\\Windows\\Start Menu\\Programs"
DEF_PATH = os.environ["ProgramFiles(x86)"]
DESKTOP_LINK_DIR = os.path.join(os.environ["public"], "Desktop")
INSTALLER_STAGES = ["Copying Files", "Creating desktop shortcut", "Creating start menu shortcut", "Finishing"]


def create_start_dir(name):
    os.mkdir(os.path.join(START_LINK_DIR, name))
    return os.path.join(START_LINK_DIR, name)


def link_file_start(prog_path, name):
    lnk = SWinLnk()
    lnk.create_lnk(prog_path, os.path.join(create_start_dir(name), name + ".lnk"))


def link_file_desktop(prog_path, name):
    lnk = SWinLnk()
    lnk.create_lnk(prog_path, os.path.join(DESKTOP_LINK_DIR, name + ".lnk"))


def step_one(where) -> str:
    archive = INSTALLER_CONFIGURATION["app_archive"]
    directory = os.getcwd()
    os.mkdir(where)
    os.chdir(where)
    shutil.unpack_archive(os.path.join(directory, archive), ".", INSTALLER_CONFIGURATION["archive_format"])
    os.chdir(directory)
    return where


def step_three(previous):
    link_file_start(os.path.join(previous, INSTALLER_CONFIGURATION["main_executable"]),
                    INSTALLER_CONFIGURATION["name"])


def step_two(previous):
    link_file_desktop(os.path.join(previous, INSTALLER_CONFIGURATION["main_executable"]),
                      INSTALLER_CONFIGURATION["name"])


def step_four(previous):
    return previous


class QErrorWindow(QMainWindow):
    def __init__(self, error, parent=None):
        super().__init__(parent)
        n = repr(error).split("(")[0]
        m = str(error)
        self.setWindowTitle(n)
        self.resize(500, 200)
        i = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.error_label = QLabel()
        self.eol = QLabel()
        self.eol.setText(m)
        self.error_label.setPixmap(i.pixmap(i.availableSizes()[0]))
        self.setWindowIcon(i)
        self.lay = QHBoxLayout()
        self.lay.addWidget(self.error_label)
        self.lay.addWidget(self.eol)
        self.w = QWidget()
        self.w.setLayout(self.lay)
        self.setCentralWidget(self.w)


class InstallerWidget(QWidget):
    def __init__(self, name, where, parent=None):
        super().__init__(parent)
        self.widget_layout = QVBoxLayout()
        self.where = where
        self.label_1 = QLabel(f"Installing {name}.")
        self.step = QLabel(f"Step {1}: {INSTALLER_STAGES[0]}")
        self.progress = QProgressBar()
        self.progress.setMaximum(4)
        self.progress.setMinimum(0)
        self.progress.setValue(0)
        self.widget_layout.addWidget(self.label_1)
        self.widget_layout.addWidget(self.step)
        self.widget_layout.addWidget(self.progress)
        self.setLayout(self.widget_layout)
        self.steps = [step_one, step_two, step_three, step_four]
        i = 1
        self.one_out = ""
        for step in self.steps:
            if i == 1:
                self.one_out = step(self.where)
            else:
                step(self.one_out)
            self.step.setText("Step " + str(i+1) + ": " + INSTALLER_STAGES[i - 1])
            self.progress.setValue(i)
            i += 1


class InstallLocationWidget(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.widget_layout = QVBoxLayout()
        self.ask_label = QLabel(f"Where to install {name}?")
        self.where_to_install = QLineEdit()
        self.where_to_install.setDisabled(True)
        self.where_to_install.setText(os.path.join(DEF_PATH, name))
        self.next_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        self.ok_button = QPushButton(text="Continue", icon=self.next_icon)
        self.widget_layout.addWidget(self.ask_label)
        self.widget_layout.addWidget(self.where_to_install)
        self.widget_layout.addWidget(self.ok_button)
        self.setLayout(self.widget_layout)


class SetupWidget(QWidget):
    def __init__(self, n, parent=None):
        super().__init__(parent)
        self.banner = QHBoxLayout()
        self.footer = QHBoxLayout()
        self.content = QVBoxLayout()
        self.layout = QVBoxLayout()
        self.name = QLabel("Welcome to " + n + " Setup!")
        self.next_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        self.banner.addWidget(self.name)
        self.next_button = QPushButton(text="Continue", icon=self.next_icon)
        self.footer.addWidget(self.next_button)
        self.content.addWidget(QLabel("This installer will guide you through the installation process."))
        self.layout.addLayout(self.banner)
        self.layout.addLayout(self.content)
        self.layout.addLayout(self.footer)
        self.setLayout(self.layout)


class Setup(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.f, self.g = INSTALLER_CONFIGURATION["window_geometry"]
        self.resize(self.f, self.g)
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon))
        self.setWindowTitle(INSTALLER_CONFIGURATION["name"] + " Installer")
        n = INSTALLER_CONFIGURATION["name"]
        self.a = SetupWidget(n)
        self.b = InstallLocationWidget(n)
        self.c = None
        self.setCentralWidget(self.a)
        self.a.next_button.clicked.connect(self.swc)
        self.b.ok_button.clicked.connect(self.trigger)
        self.ww = None

    def swc(self):
        self.setCentralWidget(self.b)
        self.resize(self.f, self.g)

    def trigger(self):
        def gp():
            if self.b.where_to_install.text():
                return self.b.where_to_install.text()
            else:
                return os.path.join(DEF_PATH, INSTALLER_CONFIGURATION["name"])
        try:
            self.c = InstallerWidget(INSTALLER_CONFIGURATION["name"], gp())
            self.resize(300, 100)
            self.setCentralWidget(self.c)
        except FileExistsError or FileNotFoundError or OSError or PermissionError or FileExistsError as exc:
            self.ww = QErrorWindow(exc)
            self.ww.show()
            self.hide()


INSTALLER_CONFIGURATION["window_geometry"] = [300, 100]


def main():
    app = QApplication([])
    win = Setup()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    if pyuac.isUserAdmin():
        main()
    else:
        pyuac.runAsAdmin()
