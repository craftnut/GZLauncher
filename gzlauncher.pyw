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
    QWidget,
)

cfgPath = Path("config.json")
cfg = {
    "gzdoom_path": "",
    "wads": [],
    "pk3": [],
}


def saveConfig():
    with open(cfgPath, "w") as file:
        json.dump(cfg, file, indent=4)

def loadConfig():
    with open(cfgPath) as file:
        return json.load(file)

if not cfgPath.exists(): # autofill things
    if pth:=shutil.which("gzdoom"):
        assert pth is not None, "What"
        print(f"gzdoom found at {pth}")
        cfg["gzdoom_path"] = pth
    saveConfig()
else:
    cfg.update(loadConfig())

gzPath: str = cfg['gzdoom_path']
wadList: list[str] = cfg['wads']
pk3List: list[str] = cfg['pk3']


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
            
        # PK3 List
        self.pk3ListWidget = FileListWidget(self, pk3List)
        self.pk3ListWidget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        # allows multiple pk3's
        
        # Other WAD-related widgets
        addWad = QPushButton("Add WAD")
        removeWad = QPushButton("Remove WAD")
        wadSelectLabel = QLabel("Select a WAD:")
        
        # Other PK3-related widgets
        addPk3 = QPushButton("Add PK3")
        removePk3 = QPushButton("Remove PK3")
        pk3SelectLabel = QLabel("Select a PK3:")
        
        # GZDoom path selection
        gzPathLabel = QLabel("Path to GZDoom executable:")
        self.gzPath = QLineEdit()
        self.gzPath.setText(gzPath)
        gzPathSelect = QPushButton("Choose Path")
        
        # Launch GZDoom button
        launchButton = QPushButton("Launch")
        noPk3LaunchButton = QPushButton("Launch without PK3")
        
        # Launcher layout
        launcherLayout = QGridLayout(self)
        
        # WAD list in layout
        launcherLayout.addWidget(wadSelectLabel, 0, 0, 1, 2)
        launcherLayout.addWidget(self.wadListWidget, 1, 0, 1, 2)
        launcherLayout.addWidget(addWad, 2, 0, 1, 1)
        launcherLayout.addWidget(removeWad, 2, 1, 1, 1)
        
        # PK3 list in layout
        launcherLayout.addWidget(pk3SelectLabel, 3, 0, 1, 2)
        launcherLayout.addWidget(self.pk3ListWidget, 4, 0, 1, 2)
        launcherLayout.addWidget(addPk3, 5, 0, 1, 1)
        launcherLayout.addWidget(removePk3, 5, 1, 1, 1)
        
        # GZDoom path selection in layout
        launcherLayout.addWidget(gzPathLabel, 6, 0, 1, 2)
        launcherLayout.addWidget(self.gzPath, 7, 0, 1, 1)
        launcherLayout.addWidget(gzPathSelect, 7, 1, 1, 1)
        
        # Launch button
        launcherLayout.addWidget(launchButton, 8, 0, 1, 2)
        launcherLayout.addWidget(noPk3LaunchButton, 9, 0, 1, 2) # ADD FUNCTIONALITY!!!!
        
        # Button connections
        addWad.clicked.connect(self.addWadFunction)
        removeWad.clicked.connect(self.removeWadFunction)
        
        addPk3.clicked.connect(self.addPk3Function)
        removePk3.clicked.connect(self.removePk3Function)
        
        self.gzPath.textChanged.connect(self.gzPath_changed)
        gzPathSelect.clicked.connect(self.selectGzPath)
        
        launchButton.clicked.connect(self.launch)
        noPk3LaunchButton.clicked.connect(self.launchNoPk)
        
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

    def addPk3Function(self):
        self.adderFunction(self.pk3ListWidget, 'Select PK3')

    def removeWadFunction(self):
        self.removerFunction(self.wadListWidget)

    def removePk3Function(self):
        self.removerFunction(self.pk3ListWidget)

    # Function for selecting GZDoom executable
    def selectGzPath(self):
        gzExeLoc = SelectFile.getOpenFileName(self, 'Select gzdoom.exe', filter='GZDoom (gzdoom.exe)')[0]
        self.gzPath.setText(str(gzExeLoc))

    def gzPath_changed(self, text):
        cfg["gzdoom_path"] = text
        saveConfig()

    # Function for launching into GZDoom
    def launch(self):
        launchWad = self.wadListWidget.currentItem().text()
        launchPk3 = [item.text() for item in self.pk3ListWidget.selectedItems()]
        command = [gzPath, *launchPk3, "-iwad", launchWad]
        print(f"launching: {command}")

        subprocess.Popen(command)

    def launchNoPk(self):
        launchWad = self.wadListWidget.currentItem().text()
        os.popen(f"{gzPath} -iwad {launchWad}")
# File selection box window
class SelectFile(QFileDialog):
    def __init__(self):
        self.setWindowTitle("Choose a file")
        
app = QApplication(sys.argv)
l = Launcher()
l.resize(320, 550)
l.show()
sys.exit(app.exec())