from PySide6.QtWidgets import QFileDialog, QApplication, QPushButton, QLabel, QLineEdit, QGridLayout, QWidget, QListWidget, QListWidgetItem
import sys
import os

# Read/create text files initially
if not os.path.exists("./cfg"):
    os.mkdir("./cfg")
    open("./cfg/wads.txt", "a").close()
    open("./cfg/gzpath.txt", "a").close()
    
with open("./cfg/wads.txt", "r") as wads:
    wadList = wads.readlines()
    wadList = [i.strip("\n") for i in wadList]

with open("./cfg/gzpath.txt", "r") as gzPathTxt:
    gzPathTxt = gzPathTxt.readlines()


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
        if gzPathTxt:
            self.gzPath.setText(str(gzPathTxt[0]))
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
        
        with open("./cfg/wads.txt", "w") as wads:
            wads.write("\n".join(wadList))
            
    def removeWadFunction(self):
               
        wadToRemove = self.wadListWidget.selectedItems()
        for item in wadToRemove:
            self.wadListWidget.takeItem(self.wadListWidget.row(item))
            
        wadRemoveIndex = self.wadListWidget.currentRow()
        wadList.pop(wadRemoveIndex)
           
        with open("./cfg/wads.txt", "w") as wads:
            wads.write("\n".join(wadList))
        
    # Function for selecting GZDoom executable
    def selectGzPath(self):
        gzExeLoc = SelectFile.getOpenFileName(self, 'Select gzdoom.exe', filter='GZDoom (gzdoom.exe)')[0]
        self.gzPath.setText(str(gzExeLoc))
        
        with open("./cfg/gzpath.txt", "w") as gzPathTxt:
            gzPathTxt.write(str(gzExeLoc))
        
    # Function for launching into GZDoom
    def launch(self):
        launchWad = self.wadListWidget.currentItem().text()
        os.popen(f'"{gzPathTxt[0]}" -iwad "{launchWad}"')
        
# File selection box window
class SelectFile(QFileDialog):
    def __init__(self):
        self.setWindowTitle("Choose a file")
        
app = QApplication(sys.argv)
l = Launcher()
l.resize(320, 550)
l.show()
sys.exit(app.exec())