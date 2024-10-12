import os
import cv2
from PySide6 import QtWidgets, QtCore
from pathlib import Path

class VideoToFramesWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.folder_clicked = False
        self.video_clicked = False
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Shortened description at the top
        description = QtWidgets.QLabel("""
            Convert a video into individual frames and save them to the specified output folder.<br><br>
            <b>Video Path:</b> The path to the input video file.<br><br>
            <b>Output Path:</b> The folder where the extracted frames will be saved.<br><br>
        """)
        description.setMargin(10)
        description.setContentsMargins(20, 0, 0, 5)
        description.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(description)
        
        # Video Path layout
        file_layout = QtWidgets.QHBoxLayout()
        file_browser_btn = QtWidgets.QPushButton('Select Video')
        file_browser_btn.setStyleSheet("font-size: 16px;")
        file_browser_btn.clicked.connect(self.open_file_dialog)
        file_layout.addWidget(file_browser_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        video_path_label = QtWidgets.QLabel("Video Path:")
        video_path_label.setStyleSheet("font-size: 16px;")
        self.filename = QtWidgets.QLabel("")
        self.filename.setStyleSheet("font-size: 16px;")
        self.filename.setWordWrap(True)
        video_path_layout = QtWidgets.QHBoxLayout()
        video_path_layout.addWidget(video_path_label)
        video_path_layout.addWidget(self.filename)
        video_path_layout.setStretch(0, 1)  # Label gets smaller part
        video_path_layout.setStretch(1, 4)  # Filename gets larger part
        file_layout.addLayout(video_path_layout)
        main_layout.addLayout(file_layout)

        # Output Folder Path layout
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.setSpacing(5)
        folder_browser_btn = QtWidgets.QPushButton('Select Image Folder')
        folder_browser_btn.setStyleSheet("font-size: 16px;")
        folder_browser_btn.clicked.connect(self.open_video_dialog)
        folder_layout.addWidget(folder_browser_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        folder_path_label = QtWidgets.QLabel("Output Path:")
        folder_path_label.setStyleSheet("font-size: 16px;")
        self.foldername = QtWidgets.QLabel("")
        self.foldername.setStyleSheet("font-size: 16px;")
        self.foldername.setWordWrap(True)
        folder_path_layout = QtWidgets.QHBoxLayout()
        folder_path_layout.addWidget(folder_path_label)
        folder_path_layout.addWidget(self.foldername)
        folder_path_layout.setStretch(0, 1)  # Label gets smaller part
        folder_path_layout.setStretch(1, 4)  # Foldername gets larger part
        folder_layout.addLayout(folder_path_layout)
        main_layout.addLayout(folder_layout)

        # Video to Frame button (disabled initially)
        self.sort_button = QtWidgets.QPushButton('Video to Frame')
        self.sort_button.setEnabled(False)
        self.sort_button.setStyleSheet("font-size: 16px;")
        self.sort_button.clicked.connect(self.process_all_videos_in_directory)
        main_layout.addWidget(self.sort_button)

        # Output log for progress display
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.log_output)

    def open_file_dialog(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        if dialog.exec():
            selected_path = dialog.selectedFiles()[0]
            path = Path(selected_path)
            self.filename.setText(str(path))
            self.video_clicked = True
            self.check_both_buttons_clicked()
    
    def open_video_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a Folder to save images", "C:")
        if folder:
            path = Path(folder)
            self.foldername.setText(str(path))
            self.folder_clicked = True
            self.check_both_buttons_clicked()
    
    def check_both_buttons_clicked(self):
        if self.video_clicked and self.folder_clicked:
            self.sort_button.setEnabled(True)

    def create_folder(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def process_video(self, video_path, output_folder):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        video_output_folder = os.path.join(output_folder, video_name)
        self.create_folder(video_output_folder)
        vidcap = cv2.VideoCapture(video_path)
        total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.log_output.append(f"Processing video: {video_name} ({total_frames} frames)")
        QtCore.QCoreApplication.processEvents()  # Update UI
        
        count = 0
        while True:
            success, image = vidcap.read()
            if not success:
                break
            frame_filename = f"{video_name}_frame{count}.jpg"
            cv2.imwrite(os.path.join(video_output_folder, frame_filename), image)
            count += 1
            self.log_output.append(f"Extracting frame {count}/{total_frames}")
            QtCore.QCoreApplication.processEvents()  # Ensure real-time updates

        vidcap.release()
        self.log_output.append(f"\n{count} images are extracted in {video_output_folder}.")
        QtCore.QCoreApplication.processEvents()  # Update UI

    def process_all_videos_in_directory(self):
        output_folder = self.foldername.text()
        self.create_folder(output_folder)
        directory_path = self.filename.text()
        self.log_output.clear()  # Clear previous log output

        if directory_path.endswith((".mp4", ".avi", ".mov")):
            video_path = directory_path
            self.process_video(video_path, output_folder)
        else:
            for filename in os.listdir(directory_path):
                if filename.endswith((".mp4", ".avi", ".mov")):
                    video_path = os.path.join(directory_path, filename)
                    self.process_video(video_path, output_folder)
        
        self.log_output.append("Finish extracting video to frames.")
