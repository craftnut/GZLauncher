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



class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GZLauncher")
        
        # WAD List
        self.wadListWidget = QListWidget(self)
        for entry in wadList:
            QListWidgetItem(entry, self.wadListWidget)
            
        # Add WADs to list button
        addWad = QPushButton("Add WAD")
        removeWad = QPushButton("Remove WAD")
        selectLabel = QLabel("Select a WAD:")
        
        # GZDoom path selection
        gzPathLabel = QLabel("Path to GZDoom executable:")
        self.gzPath = QLineEdit()
        self.gzPath.setText(gzPath)
        gzPathSelect = QPushButton("Choose Path")
        
        # Launch GZDoom button
        launchButton = QPushButton("Launch")
        
        # Launcher layout
        launcherLayout = QGridLayout(self)
        
        # WAD list in layout
        launcherLayout.addWidget(selectLabel, 0, 0, 1, 2)
        launcherLayout.addWidget(self.wadListWidget, 1, 0, 1, 2)
        launcherLayout.addWidget(addWad, 2, 0, 1, 1)
        launcherLayout.addWidget(removeWad, 2, 1, 1, 1)
        
        # GZDoom path selection in layout
        launcherLayout.addWidget(gzPathLabel, 3, 0, 1, 2)
        launcherLayout.addWidget(self.gzPath, 4, 0, 1, 1)
        launcherLayout.addWidget(gzPathSelect, 4, 1, 1, 1)
        
        # Launch button
        launcherLayout.addWidget(launchButton, 5, 0, 1, 2)
        
        # Button connections
        addWad.clicked.connect(self.addWadFunction)
        removeWad.clicked.connect(self.removeWadFunction)
        self.gzPath.textChanged.connect(self.gzPath_changed)
        gzPathSelect.clicked.connect(self.selectGzPath)
        launchButton.clicked.connect(self.launch)
        self.wadListWidget.itemDoubleClicked.connect(self.launch)
        
    # Function for adding WADs to the list
    def addWadFunction(self):
        wadSelect = SelectFile.getOpenFileName(self, 'Select WAD', filter='WAD files (*.wad)')[0]
        addWad = QListWidgetItem()
        addWad.setText(wadSelect)
        self.wadListWidget.addItem(addWad)
        wadList.append(wadSelect)
        saveConfig()

    def removeWadFunction(self):
               
        wadToRemove = self.wadListWidget.selectedItems()
        for item in wadToRemove:
            self.wadListWidget.takeItem(self.wadListWidget.row(item))
            
        wadRemoveIndex = self.wadListWidget.currentRow()
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
        os.popen(f'"{gzPath}" -iwad "{launchWad}"')
        
# File selection box window
class SelectFile(QFileDialog):
    def __init__(self):
        self.setWindowTitle("Choose a file")
        
app = QApplication(sys.argv)
l = Launcher()
l.resize(320, 550)
l.show()
sys.exit(app.exec())