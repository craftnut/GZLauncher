import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QComboBox,
    QWidget,
)

cfgPath = Path("config.json")
cfg = {
    "gzdoom_path": "",
    "wads": [],
    "mod": [],
    "last_used_cfg": "",
}


def saveConfig():
    with open(cfgPath, "w") as file:
        json.dump(cfg, file, indent=4)

def loadConfig():
    with open(cfgPath) as file:
        return json.load(file)

if not cfgPath.exists(): # autofill things
    saveConfig()
else:
    cfg.update(loadConfig())

gzExecutablePath: str = cfg['gzdoom_path']
wadList: list[str] = cfg['wads']
modList: list[str] = cfg['mod']
previousCfg: str = cfg['last_used_cfg']

configs = [str(file.relative_to("./cfg")) for file in Path("./cfg").rglob("*.ini")]

class FileListWidget(QListWidget):
    def __init__(self, parent, correspondingList: list):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.list = correspondingList
        self.populate(correspondingList)

    def populate(self, lst):
        for entry in lst:
            QListWidgetItem(entry, self)

    def add(self, item: QListWidgetItem):
        self.addItem(item)
        self.list.append(item.text())

    def remove(self, item: QListWidgetItem):
        self.list.remove(self.takeItem(self.row(item)).text())

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # Without this, dragging in a file is always denied. Not entirely sure why.
    def dragMoveEvent(self, e) -> None:
        e.accept()

    def dropEvent(self, event) -> None:
        event.setDropAction(QtCore.Qt.DropAction.CopyAction)
        file_path: list[QtCore.QUrl] = event.mimeData().urls()
        hasNewFiles = False
        for file in file_path:
            if (s:=file.toLocalFile()) not in self.list:
                self.add(QListWidgetItem(s))
                hasNewFiles = True
            else:
                print(f"{s} is in wad list")
        if hasNewFiles:
            saveConfig()

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GZLauncher")
        
        # WAD List
        self.wadListWidget = FileListWidget(self, wadList)
            
        # Mod List
        self.modListWidget = FileListWidget(self, modList)
        self.modListWidget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        # allows multiple mods to be selected
        
        # Other WAD-related widgets
        addWad = QPushButton("Add WAD")
        removeWad = QPushButton("Remove WAD")
        wadSelectLabel = QLabel("Select a WAD:")
        
        # Other Mod-related widgets
        addMod = QPushButton("Add Mod")
        removeMod = QPushButton("Remove Mod")
        modSelectLabel = QLabel("Select Mod(s):")
        
        # GZDoom path selection
        gzPathLabel = QLabel("Path to GZDoom executable:")
        self.gzPath = QLineEdit()
        if gzExecutablePath:
            self.gzPath.setText(gzExecutablePath)
        if pth:=shutil.which("gzdoom"):
            assert pth is not None, "What"
            print(f"gzdoom found at {pth}")
            self.gzPath.setPlaceholderText(pth)
        
        gzPathSelect = QPushButton("Choose Path")
        
        # Launch GZDoom button
        launchButton = QPushButton("Launch")
        noModLaunchButton = QPushButton("Launch without mods")
        
        self.cfgDropDown = QComboBox()
        self.cfgDropDown.addItems(configs)
        if self.cfgDropDown.findText(previousCfg) != -1:
            self.cfgDropDown.setCurrentText(previousCfg)
        
        # Launcher layout
        launcherLayout = QGridLayout(self)
        
        # WAD list in layout
        launcherLayout.addWidget(wadSelectLabel, 0, 0, 1, 2)
        launcherLayout.addWidget(self.wadListWidget, 1, 0, 1, 2)
        launcherLayout.addWidget(addWad, 2, 0, 1, 1)
        launcherLayout.addWidget(removeWad, 2, 1, 1, 1)
        
        # Mod list in layout
        launcherLayout.addWidget(modSelectLabel, 3, 0, 1, 2)
        launcherLayout.addWidget(self.modListWidget, 4, 0, 1, 2)
        launcherLayout.addWidget(addMod, 5, 0, 1, 1)
        launcherLayout.addWidget(removeMod, 5, 1, 1, 1)
        
        # GZDoom path selection in layout
        launcherLayout.addWidget(gzPathLabel, 6, 0, 1, 2)
        launcherLayout.addWidget(self.gzPath, 7, 0, 1, 1)
        launcherLayout.addWidget(gzPathSelect, 7, 1, 1, 1)
        
        # Launch button and configs dropdown
        launcherLayout.addWidget(launchButton, 8, 0, 1, 1)
        launcherLayout.addWidget(self.cfgDropDown, 8, 1, 1, 1)
        launcherLayout.addWidget(noModLaunchButton, 9, 0, 1, 2)
        
        # Button connections
        addWad.clicked.connect(self.addWadFunction)
        removeWad.clicked.connect(self.removeWadFunction)
        
        addMod.clicked.connect(self.addModFunction)
        removeMod.clicked.connect(self.removeModFunction)
        
        self.gzPath.textChanged.connect(self.gzPath_changed)
        gzPathSelect.clicked.connect(self.selectGzPath)
        
        launchButton.clicked.connect(self.launch)
        noModLaunchButton.clicked.connect(self.launchNoPk)
        
        self.wadListWidget.itemDoubleClicked.connect(self.launch)

    # abstract Function for adding items to a list
    def adderFunction(self, listwidget: FileListWidget, *select_args, **select_kwargs):
        select: str = SelectFile.getOpenFileName(self, *select_args, **select_kwargs)[0]
        if select:
            listwidget.add(QListWidgetItem(select))
            saveConfig()

    # abstract function for removing items from a list
    def removerFunction(self, listwidget: FileListWidget):
        toRemove = listwidget.selectedItems()
        for item in toRemove:
            listwidget.remove(item)
        saveConfig()

    def addWadFunction(self):
        self.adderFunction(self.wadListWidget, 'Select WAD', filter='WAD files (*.wad, *.WAD)')

    def addModFunction(self):
        self.adderFunction(self.modListWidget, 'Select mod (*.wad, *.WAD, *.pk3, *.PK3)')

    def removeWadFunction(self):
        self.removerFunction(self.wadListWidget)

    def removeModFunction(self):
        self.removerFunction(self.modListWidget)

    # Function for selecting GZDoom executable
    def selectGzPath(self):
        gzExeLoc = SelectFile.getOpenFileName(self, 'Select gzdoom exectuable')[0]
        self.gzPath.setText(str(gzExeLoc))

    def gzPath_changed(self, text):
        cfg["gzdoom_path"] = text
        saveConfig()

    # Function for launching into GZDoom
    def launch(self):
        usedConfig = self.cfgDropDown.currentText()
        launchWad = self.wadListWidget.currentItem().text()
        launchMod = [item.text() for item in self.modListWidget.selectedItems()]
        exePath = self.gzPath.text() or self.gzPath.placeholderText()
        command = [exePath, *launchMod, "-iwad", launchWad, "-config", f"./cfg/{usedConfig}"]
        print(f"launching: {command}")
        
        cfg['last_used_cfg'] = usedConfig
        saveConfig()

        subprocess.Popen(command)

    def launchNoPk(self):
        usedConfig = self.cfgDropDown.currentText()
        launchWad = self.wadListWidget.currentItem().text()
        exePath = self.gzPath.text() or self.gzPath.placeholderText()
        command = [exePath, "-iwad", launchWad, "-config", f"./cfg/{usedConfig}"]
        
        cfg['last_used_cfg'] = usedConfig
        saveConfig()
        
        subprocess.Popen(command)
        
# File selection box window
class SelectFile(QFileDialog):
    def __init__(self):
        self.setWindowTitle("Choose a file")
        
app = QApplication(sys.argv)
l = Launcher()
l.resize(320, 550)
l.show()
sys.exit(app.exec())