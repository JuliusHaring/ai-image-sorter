import sys
import shutil
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QCheckBox, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt

class ImageAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.analysisDone = False  # Flag to indicate if analysis is done
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.importFolderLabel = QLabel("Import Folder: None")
        self.targetFolderLabel = QLabel("Target Folder: None")
        self.includeOutputFolderCheckbox = QCheckBox("Include Output Folder in Analysis")
        self.overwriteCheckbox = QCheckBox("Overwrite existing files")

        self.fileTypeList = QListWidget()
        file_types = ["jpg", "jpeg", "tiff", "nef", "cr2", "arw", "raf"]  # Add more file types or RAW formats as needed
        for file_type in file_types:
            item = QListWidgetItem(file_type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.fileTypeList.addItem(item)

        self.importFolderButton = QPushButton("Select Import Folder")
        self.importFolderButton.clicked.connect(self.selectImportFolder)

        self.targetFolderButton = QPushButton("Select Target Folder")
        self.targetFolderButton.clicked.connect(self.selectTargetFolder)

        self.analyzeButton = QPushButton("Start Analysis")
        self.analyzeButton.clicked.connect(self.startAnalysis)
        self.analyzeButton.setEnabled(False)  # Disabled initially

        self.copyButton = QPushButton("Copy Files")
        self.copyButton.clicked.connect(self.copyFiles)
        self.copyButton.setEnabled(False)  # Disabled initially

        layout.addWidget(self.importFolderLabel)
        layout.addWidget(self.importFolderButton)
        layout.addWidget(self.targetFolderLabel)
        layout.addWidget(self.targetFolderButton)
        layout.addWidget(self.includeOutputFolderCheckbox)
        layout.addWidget(self.analyzeButton)
        layout.addWidget(self.fileTypeList)
        layout.addWidget(self.overwriteCheckbox)
        layout.addWidget(self.copyButton)

        self.setLayout(layout)
        self.setWindowTitle('Image Analyzer')

    def updateButtons(self):
        # Enable analyzeButton if both folders are selected
        importFolder = self.importFolderLabel.text() != "Import Folder: None"
        targetFolder = self.targetFolderLabel.text() != "Target Folder: None"
        self.analyzeButton.setEnabled(importFolder and targetFolder and (importFolder != targetFolder))

        # Enable copyButton if analysis is done
        self.copyButton.setEnabled(self.analysisDone)

    def selectImportFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Import Folder")
        if folder:
            self.importFolderLabel.setText(f"Import Folder: {folder}")
            self.updateButtons()

    def selectTargetFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if folder:
            self.targetFolderLabel.setText(f"Target Folder: {folder}")
            self.updateButtons()

    def startAnalysis(self):
        # Placeholder for starting analysis
        print("Starting analysis...")
        # Implement analysis logic here

        self.analysisDone = True  # Set flag to True after analysis is completed
        self.updateButtons()

    def copyFiles(self):
        importFolder = self.importFolderLabel.text().replace("Import Folder: ", "")
        targetFolder = self.targetFolderLabel.text().replace("Target Folder: ", "")
        overwrite = self.overwriteCheckbox.isChecked()
        selectedFileType = self.fileTypeComboBox.currentText()

        if not os.path.isdir(importFolder) or not os.path.isdir(targetFolder):
            print("Invalid import or target folder.")
            return

        for root, dirs, files in os.walk(importFolder):
            for file in files:
                if not file.lower().endswith(selectedFileType.lower()):
                    continue
                src_file = os.path.join(root, file)
                dst_file = os.path.join(targetFolder, file)
                
                if overwrite or not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied {src_file} to {dst_file}")
                else:
                    print(f"File {dst_file} already exists. Skipping.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageAnalyzerApp()
    ex.show()
    sys.exit(app.exec_())
