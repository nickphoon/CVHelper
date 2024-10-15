import sys
import os
import cv2
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path

class VideoToFramesWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.folder_clicked = False
        self.video_clicked = False
        self.total_frames = 0  # To store the total frames of the selected video
        self.frame_start = 0
        self.frame_end = 0
        self.fps = 1  # Default fps (to be updated when the video is loaded)
        self.video_capture = None  # To store the video capture object

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Shortened description at the top
        description = QtWidgets.QLabel("""
            Convert a video into individual frames and save them to the specified output folder.<br><br>
            <b>Video Path:</b> The path to the input video file.<br><br>
            <b>Output Path:</b> The folder where the extracted frames will be saved.<br><br>
        """)
        description.setMargin(5)
        description.setContentsMargins(10, 0, 0, 5)
        description.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(description)
        
        # Video Path layout
        file_layout = QtWidgets.QHBoxLayout()
        file_browser_btn = QtWidgets.QPushButton('Select Video')
        file_browser_btn.setStyleSheet("""
            font-size: 16px;
            border: 2px solid black;  /* Add a solid black border */
            padding: 5px;
            background-color: #c1E899;  /* Optional: Add a background color */
                                         
        """)
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
        # folder_layout.setSpacing(5)
        folder_browser_btn = QtWidgets.QPushButton('Select Image Folder')
        
        folder_browser_btn.setStyleSheet("""
            font-size: 16px;
            border: 2px solid black;  /* Add a solid black border */
            padding: 5px;
            background-color: #c1E899;  /* Optional: Add a background color */
                                         
        """)
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

        # Video Display Area (QLabel)
        self.video_label = QtWidgets.QLabel()
        self.video_label.setFixedSize(400, 300)  # Set a fixed size for the video display
        self.video_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")  # Background color for the video display
        main_layout.addWidget(self.video_label)

        # Slider for Start Frame
        self.start_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.start_slider.setEnabled(False)  # Disabled initially
        self.start_slider.setMinimum(0)
        self.start_slider.setMaximum(100)  # Placeholder value, updated when video is loaded
        self.start_slider.setStyleSheet("font-size: 16px;")
        self.start_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.start_slider.setTickInterval(10)
        self.start_slider.valueChanged.connect(self.update_start_slider_value)
        main_layout.addWidget(self.start_slider)
        # Set custom style for the slider
        self.start_slider.setStyleSheet("""
    QSlider::groove:horizontal {
        background: #d0d0d0;  /* Groove color */
        height: 10px;
        border-radius: 5px;
    }

    QSlider::handle:horizontal {
        background: #55883b;  /* Handle color */
        border: 1px solid #3b8848;
        width: 20px;
        height: 20px;
        margin: -5px 0;  /* Center the handle vertically */
        border-radius: 10px;
    }

    QSlider::sub-page:horizontal {
        background: #a0c39a;  /* Color before the handle */
    }

    QSlider::add-page:horizontal {
        background: #c0c0c0;  /* Color after the handle */
    }

    QSlider::tick:horizontal {
        background: black;  /* Tick color */
    }
""")
        # Slider for End Frame
        self.end_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.end_slider.setEnabled(False)  # Disabled initially
        self.end_slider.setMinimum(0)
        self.end_slider.setMaximum(100)  # Placeholder value, updated when video is loaded
        self.end_slider.setStyleSheet("font-size: 16px;")
        self.end_slider.setStyleSheet("""
    QSlider::groove:horizontal {
        background: #d0d0d0;  /* Groove color */
        height: 10px;
        border-radius: 5px;
    }

    QSlider::handle:horizontal {
        background: #88483b;  /* Handle color */
        border: 1px solid #3b8848;
        width: 20px;
        height: 20px;
        margin: -5px 0;
        border-radius: 10px;
    }

    QSlider::sub-page:horizontal {
        background: #a0c39a;  /* Color before the handle */
    }

    QSlider::add-page:horizontal {
        background: #c0c0c0;  /* Color after the handle */
    }

    QSlider::tick:horizontal {
        background: black;  /* Tick color */
    }
""")
        self.end_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.end_slider.setTickInterval(10)
        self.end_slider.valueChanged.connect(self.update_end_slider_value)

        main_layout.addWidget(self.end_slider)

        # Slider Label
        self.slider_label = QtWidgets.QLabel("Use the sliders to select the portion of the video.")
        self.slider_label.setStyleSheet("font-size: 16px;")
        self.slider_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.slider_label)

        # Video to Frame button (disabled initially)
        self.sort_button = QtWidgets.QPushButton('Video to Frame')
        self.sort_button.setEnabled(False)
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
        self.sort_button.clicked.connect(self.process_all_videos_in_directory)
        main_layout.addWidget(self.sort_button)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
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
            self.load_video_frames(selected_path)
            self.check_both_buttons_clicked()

    def load_video_frames(self, video_path):
        if(self.video_capture):
            self.video_capture.release()
        self.video_capture = cv2.VideoCapture(video_path)
        
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)  # Get the frames per second

        # Set slider maximum to total frames
        self.start_slider.setEnabled(True)
        self.end_slider.setEnabled(True)
        self.start_slider.setMaximum(self.total_frames)
        self.end_slider.setMaximum(self.total_frames)
        self.end_slider.setValue(self.total_frames)  # Default is full video
        self.update_slider_label()
        self.show_frame(0)  # Show the first frame when the video is loaded

    def update_start_slider_value(self, value):
        self.frame_start = value
        if self.frame_start > self.frame_end:
            self.frame_start = self.frame_end
            self.start_slider.setValue(self.frame_start)
        self.update_slider_label()
        self.show_frame(self.frame_start)

    def update_end_slider_value(self, value):
        self.frame_end = value
        if self.frame_end < self.frame_start:
            self.frame_end = self.frame_start
            self.end_slider.setValue(self.frame_end)
        self.update_slider_label()
        self.show_frame(self.frame_end)

    def update_slider_label(self):
        # Convert frames to time in seconds
        start_seconds = self.frame_start / self.fps
        end_seconds = self.frame_end / self.fps
        self.slider_label.setText(f"Processing video length from {start_seconds:.2f} to {end_seconds:.2f} seconds.")

    def show_frame(self, frame_number):
        """Display a specific frame in the QLabel"""
        if self.video_capture is None:
            return

        # Set the video capture to the desired frame
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = self.video_capture.read()

        if success:
            # Convert the frame to RGB (since OpenCV uses BGR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to a QImage to display in the QLabel
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

            # Scale the image to fit the QLabel size
            pixmap = QtGui.QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio)

            # Update the QLabel with the pixmap
            self.video_label.setPixmap(pixmap)

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
        # Convert frame start and end to seconds
        start_seconds = int(self.frame_start // self.fps)
        
        end_seconds = int(self.frame_end // self.fps)

        # Create a subfolder using the video name and the start/end times
        subfolder_name = f"{video_name}_{start_seconds}s-{end_seconds}s"
        video_output_folder = os.path.join(output_folder, subfolder_name)
        self.create_folder(video_output_folder)

        self.video_capture = cv2.VideoCapture(video_path)
    
        # Move the video capture to the start frame
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.frame_start)
        total_frames = self.frame_end  # Use self.frame_end instead of total_frames
        self.log_output.append(f"Processing video: {video_name} (up to frame {total_frames})")

        # Set the progress bar range
        self.progress_bar.setMaximum(total_frames - self.frame_start)
        self.progress_bar.setValue(0)  # Reset the progress bar
        QtCore.QCoreApplication.processEvents()  # Update UI


        if(self.frame_start!=0):
            print_count = 0
        else:
            print_count = count
        print_total_frames = self.frame_end - self.frame_start
        count = self.frame_start
        print(count)
        while count < total_frames:
            success, image = self.video_capture.read()
            if not success:
                break
            if count >= self.frame_start:
                frame_filename = f"{video_name}_frame{count}.jpg"
                cv2.imwrite(os.path.join(video_output_folder, frame_filename), image)
                self.log_output.append(f"Extracting frame {print_count}/{print_total_frames}")
                self.progress_bar.setValue(count - self.frame_start + 1)
            count += 1
            print_count+=1
            QtCore.QCoreApplication.processEvents()  # Ensure real-time updates

        # self.video_capture.release()
        self.log_output.append(f"\n{self.frame_end-self.frame_start} images are extracted in {video_output_folder}.")
        QtCore.QCoreApplication.processEvents()  # Update UI
        self.show_frame(self.frame_start)
        self.reset_state()

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

    def reset_state(self):
        # self.show_frame(self.frame_start)
         # Optionally, clear the progress bar if you want to start from scratch:
        self.progress_bar.setValue(0)
        
        # Update the log output to indicate readiness for further frame extraction.
        self.log_output.append("\nProcessing complete. You can adjust the sliders to extract another range of frames.")

        # Disable the "Video to Frame" button until the user adjusts the sliders again.
        # self.sort_button.setEnabled(False)