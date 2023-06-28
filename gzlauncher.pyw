import json
import os
import shutil
import sys
from pathlib import Path

from PySide6.QtWidgets import (
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



class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GZLauncher")
        
        # WAD List
        self.wadListWidget = QListWidget(self)
        for entry in wadList:
            QListWidgetItem(entry, self.wadListWidget)
            
        # PK3 List
        self.pk3ListWidget = QListWidget(self)
        for entry in pk3List:
            QListWidgetItem(entry, self.pk3ListWidget)
            
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
        
    # Function for adding WADs to the list
    def addWadFunction(self):
        wadSelect = SelectFile.getOpenFileName(self, 'Select WAD', filter='WAD files (*.wad, *.WAD)')[0]
        if wadSelect:
            
            addWad = QListWidgetItem()
            addWad.setText(wadSelect)
            
            self.wadListWidget.addItem(addWad)
            wadList.append(wadSelect)
            
            saveConfig()
            
    def addPk3Function(self):
        pk3select = SelectFile.getOpenFileName(self, 'Select PK3')[0]
        if pk3select:
            
            addPk3 = QListWidgetItem()
            addPk3.setText(pk3select)
            
            self.pk3ListWidget.addItem(addPk3)
            pk3List.append(pk3select)
            
            saveConfig()

    def removeWadFunction(self):
               
        wadToRemove = self.wadListWidget.selectedItems()
        
        for item in wadToRemove:
            self.wadListWidget.takeItem(self.wadListWidget.row(item))
            
        wadRemoveIndex = self.wadListWidget.currentRow()
        wadList.pop(wadRemoveIndex)
        
        saveConfig()
        
    def removePk3Function(self):
        
        pk3ToRemove = self.pk3ListWidget.selectedItems()
        
        for item in pk3ToRemove:
            self.pk3ListWidget.takeItem(self.pk3ListWidget.row(item))
            
        wadRemoveIndex = self.pk3ListWidget.currentRow()
        wadList.pop(wadRemoveIndex)
            
        saveConfig()
        
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
        launchPk3 = self.pk3ListWidget.currentItem().text()
        os.popen(f"{gzPath} {launchPk3} -iwad {launchWad}")
        
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