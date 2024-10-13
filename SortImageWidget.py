import os
import shutil
import pandas as pd
from PySide6 import QtWidgets, QtCore
from pathlib import Path
class SortImageWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
       
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        
        # check if both buttons are clicked
        self.folder_clicked = False
        main_layout.setSpacing(1)
        
        # Create an HBoxLayout for folder button and folder path label + folder name
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.setSpacing(5)
        # Folder browser button aligned center-left
        folder_browser_btn = QtWidgets.QPushButton('Select Image Folder')
        folder_browser_btn.setStyleSheet("font-size: 16px;")
        folder_browser_btn.setStyleSheet("""
            font-size: 16px;
            border: 2px solid black;  /* Add a solid black border */
            padding: 5px;
            background-color: #c1E899;  /* Optional: Add a background color */
                                         
        """)
        folder_layout.addWidget(folder_browser_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        description = QtWidgets.QLabel("""
    Sort a folder of images based on their class found in <i>_annotations.csv</i> file in the folder.<br><br>
    <b>Folder Directory:</b>
    <pre>
    folder/
        train/
            001.jpg
            002.jpg
            _annotations.csv
        test/
            003.jpg
            004.jpg
            _annotations.csv
    </pre>
""")
        description.setMargin(5)
        description.setContentsMargins(10,0,0,5)
        description.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(description)
        # Folder path label and folder name aligned center-right
        folder_path_label = QtWidgets.QLabel("Folder Path:")
        folder_path_label.setStyleSheet("font-size: 16px;")
        folder_browser_btn.clicked.connect(self.open_folder_dialog)
        self.foldername = QtWidgets.QLabel("")
        self.foldername.setStyleSheet("font-size: 16px;")
        folder_path_layout = QtWidgets.QHBoxLayout()
        folder_path_layout.addWidget(folder_path_label)
        folder_path_layout.addWidget(self.foldername)
        folder_layout.addLayout(folder_path_layout)
        # folder_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Add the folder layout to the main layout
        main_layout.addLayout(folder_layout)
        # Sort button
        
        # Third button that is disabled initially
        self.sort_button = QtWidgets.QPushButton('Sort Images')
        self.sort_button.setEnabled(False)  # Disable by default
        self.sort_button.setStyleSheet("""
    QPushButton {
        font-size: 16px;
        border: 2px solid black;
        padding: 5px;
        background-color: #c1E899;
        color: black;
    }

    QPushButton:disabled {
        background-color: #d3d3d3;  /* Greyed-out background */
        color: #a0a0a0;  /* Greyed-out text */
        border: 2px solid #a0a0a0;  /* Greyed-out border */
    }
""")
        self.sort_button.clicked.connect(self.sort_images_by_class)
        main_layout.addWidget(self.sort_button)

        # Output log for showing progress (QTextEdit)
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)  # Make it read-only
        self.log_output.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.log_output)

    
    
    def open_folder_dialog(self):
        folder= QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a Folder of images",
            "C:"
        )
        if folder:
            path = Path(folder)
            self.foldername.setText(str(path))
            self.folder_clicked = True  # Mark as clicked
            self.check_both_buttons_clicked()
    
    def check_both_buttons_clicked(self):
        # Enable the third button only if both the CSV and folder buttons are clicked
        if self.folder_clicked:
            self.sort_button.setEnabled(True)

    def sort_images_by_class(self, folderPath):
        folderPath = self.foldername.text()
        check = os.listdir(folderPath)
        self.log_output.clear()
        self.log_output.append(f"Sorting Images from <b>{folderPath}</b><br>")
        if(check[0].endswith(".jpg") or check[0].endswith(".png")):
            folders = [folderPath]
        else:
            folders = [folder for folder in check if not "." in folder] 

        for folder in folders:
            csvPath = os.path.join(folderPath, folder, '_annotations.csv')
            
            if os.path.exists(csvPath):
                df = pd.read_csv(csvPath)
                self.log_output.append(f'Processing folder: {folder}')  # Log progress
                QtWidgets.QApplication.processEvents()
                for index, row in df.iterrows():
                    filename = row['filename']
                    class_name = row['class']
                    
                    # Create class folder (e.g., P4) if it doesn't exist
                    class_folder = f'P{class_name}'
                    class_folder_path = os.path.join(folderPath, folder, class_folder)
                    if not os.path.exists(class_folder_path):
                        os.makedirs(class_folder_path)
                    
                    # Source and destination paths
                    src_file = os.path.join(folderPath, folder, filename)
                    dest_file = os.path.join(class_folder_path, filename)
                    
                    if os.path.exists(src_file):
                        shutil.move(src_file, dest_file)
                
                self.log_output.append(f"Images in {folder} have been sorted.")
                QtWidgets.QApplication.processEvents()  # Log sorted message
                self.log_output.append("All folders have been processed.")  # Final message
            else:
                self.log_output.append(f"No annotations file found in {folder}")
                QtWidgets.QApplication.processEvents()

        
        QtWidgets.QApplication.processEvents()