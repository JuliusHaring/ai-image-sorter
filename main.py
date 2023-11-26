import sys
import shutil
import os
import dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QCheckBox, QListWidget, QListWidgetItem, QTextEdit
from PyQt5.QtCore import Qt

from image_analysis import analyze_images_in_folder

dotenv.load_dotenv()

class ImageAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.analysisDone = False
        self.analysisResult = []  # Store analysis results
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.importFolderLabel = QLabel("Import Folder: None")
        self.targetFolderLabel = QLabel("Target Folder: None")
        self.multipleOutputFoldersCheckbox = QCheckBox("Output multiple folders")
        self.multipleOutputFoldersCheckbox.setChecked(True)
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

        self.analysisOverview = QTextEdit()  # Text display for analysis overview
        self.analysisOverview.setReadOnly(True)

        layout.addWidget(self.importFolderLabel)
        layout.addWidget(self.importFolderButton)
        layout.addWidget(self.targetFolderLabel)
        layout.addWidget(self.targetFolderButton)
        layout.addWidget(self.multipleOutputFoldersCheckbox)
        layout.addWidget(self.analyzeButton)
        layout.addWidget(self.fileTypeList)
        layout.addWidget(self.analysisOverview)
        layout.addWidget(self.overwriteCheckbox)
        layout.addWidget(self.copyButton)

        self.setLayout(layout)
        self.setWindowTitle('Image Analyzer')

    def updateButtons(self):
        # Enable analyzeButton if both folders are selected
        importFolder = self.importFolderLabel.text() != "Import Folder: None"
        targetFolder = self.targetFolderLabel.text() != "Target Folder: None"
        self.analyzeButton.setEnabled(importFolder and targetFolder)

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
        importFolder = self.importFolderLabel.text().replace("Import Folder: ", "")
        targetFolder = self.targetFolderLabel.text().replace("Target Folder: ", "")
        multipleFolders = self.multipleOutputFoldersCheckbox.isChecked()

        if not os.path.isdir(importFolder) or not os.path.isdir(targetFolder):
            print("Invalid import or target folder.")
            return

        print("Starting analysis...")
        self.analysisResult = analyze_images_in_folder(importFolder, targetFolder, multipleFolders)

        # Update the analysis overview with the results
        analysis_summary = '\n'.join([f"{result['input_image_path']} -> {result['output_image_path']}" for result in self.analysisResult])
        self.analysisOverview.setText(analysis_summary)

        self.analysisDone = True
        self.updateButtons()

    def copyFiles(self):
        overwrite = self.overwriteCheckbox.isChecked()

        for result in self.analysisResult:
            src_file = result['input_image_path']
            dst_file = result['output_image_path']

            # Create directories if they do not exist
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

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
