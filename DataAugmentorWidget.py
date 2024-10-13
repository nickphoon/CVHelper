import os
import cv2
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path
from AugmentationWorker import AugmentationWorker

class DataAugmentorWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_folder_clicked = False
        self.folder_clicked = False
        self.current_image = None  # To store the currently loaded image

        main_layout = QtWidgets.QHBoxLayout()  # Change to horizontal layout for side-by-side view
        self.setLayout(main_layout)

        # Left-side layout for parameters
        param_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(param_layout)

        # Description at the top
        description = QtWidgets.QLabel("Augment images using OpenCV augmentation techniques.")
        description.setStyleSheet("font-size: 16px; text-align: center;")
        description.setContentsMargins(0, 10, 0, 20)
        description.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        param_layout.addWidget(description)

        # Form layout for augmentation parameters
        form_layout = QtWidgets.QFormLayout()
        param_layout.addLayout(form_layout)

        # Initialize lists to store the input fields and corresponding warning labels
        self.param_inputs = []
        self.sliders = []
        self.warning_labels = []

        # Parameters for augmentation with descriptions and ranges
        param_info = [
            ("Rotation (Degrees)", "Rotation amount", "0-180", QtGui.QIntValidator(0, 180)),
            ("Flip Left-Right", "Flip image horizontally", "yes/no", None),
            ("Flip Top-Bottom", "Flip image vertically", "yes/no", None),
            ("Zoom (Range)", "Zoom range", "0.0-1.0", QtGui.QDoubleValidator(0.0, 1.0, 2)),
            ("Shear (Degrees)", "Shear range", "0-45", QtGui.QIntValidator(0, 45))
        ]

        # Add the parameters with sliders, validators, and descriptions to the form layout
        for i, (title, desc, range_text, validator) in enumerate(param_info):
            label = QtWidgets.QLabel(f"{title}:")
            label.setStyleSheet("font-size: 14px;")

            if i == 1 or i == 2:  # Drop-down menus for flip options
                combo_box = QtWidgets.QComboBox(self)
                combo_box.setFixedWidth(50)
                combo_box.addItems(["No", "Yes"])  # Default to "No"
                combo_box.setCurrentText("No")
                combo_box.currentTextChanged.connect(self.update_live_sample)  # Connect to update live sample
                form_layout.addRow(label, combo_box)
                self.param_inputs.append(combo_box)
            else:
                # Create layout with line edit and slider
                slider_layout = QtWidgets.QHBoxLayout()

                # QLineEdit for number input
                line_edit = QtWidgets.QLineEdit(self)
                line_edit.setFixedWidth(50)
                line_edit.setText("0")  # Set default value to 0
                if validator:
                    line_edit.setValidator(validator) 
                     # Apply validator to ensure input is within range
                    line_edit.textChanged.connect(self.sync_slider_with_line_edit(i))  # Connect to update slider

                # QSlider
                slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
                slider.setFixedWidth(150)

                if i == 0:  # Rotation slider (0-180)
                    slider.setRange(0, 180)
                elif i == 3:  # Zoom slider (0-100, represents 0.0-1.0)
                    slider.setRange(0, 99)
                elif i == 4:  # Shear slider (0-45)
                    slider.setRange(0, 45)

                slider.valueChanged.connect(self.sync_line_edit_with_slider(i))  # Sync line edit when slider changes
                slider_layout.addWidget(line_edit)
                slider_layout.addWidget(slider)

                # Add layout to form
                form_layout.addRow(label, slider_layout)
                self.param_inputs.append(line_edit)
                self.sliders.append(slider)
            
            # Add a description and range label for guidance
            desc_label = QtWidgets.QLabel(f"{desc} ({range_text})")
            desc_label.setStyleSheet("font-size: 12px; color: grey;")
            form_layout.addRow(desc_label)

            # Add a warning label for each input
            warning_label = QtWidgets.QLabel("")
            warning_label.setStyleSheet("font-size: 12px; color: red;")
            warning_label.setVisible(False)  # Initially hidden
            form_layout.addRow(warning_label)
            self.warning_labels.append(warning_label)

        # Folder Path
        folder_layout = QtWidgets.QHBoxLayout()
        param_layout.addLayout(folder_layout)
        folder_browser_btn = QtWidgets.QPushButton('Select Image Folder')
        folder_browser_btn.clicked.connect(self.open_folder_dialog)
        folder_layout.addWidget(folder_browser_btn)
        self.foldername = QtWidgets.QLabel("")
        folder_layout.addWidget(self.foldername)

        # Output Folder Path
        output_layout = QtWidgets.QHBoxLayout()
        param_layout.addLayout(output_layout)
        output_browser_btn = QtWidgets.QPushButton('Select Output Folder')
        output_browser_btn.clicked.connect(self.open_output_folder_dialog)
        output_layout.addWidget(output_browser_btn)
        self.output_foldername = QtWidgets.QLabel("")
        output_layout.addWidget(self.output_foldername)

        # Augment Images button
        self.augment_button = QtWidgets.QPushButton('Augment Images')
        self.augment_button.setEnabled(False)
        self.augment_button.clicked.connect(self.process_augmentation_pipeline)
        param_layout.addWidget(self.augment_button)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(0)
        param_layout.addWidget(self.progress_bar)

        # Right-side layout for live image sample
        right_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(right_layout)

        # QLabel to show the live image
        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(300, 300)  # Fixed size for the live preview
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")  # Set a background color
        right_layout.addWidget(self.image_label)

        # Output log for showing progress
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        right_layout.addWidget(self.log_output)

    def sync_slider_with_line_edit(self, index):
        
        
        """Synchronize slider with QLineEdit when the QLineEdit value changes."""
        def update_slider():
            if self.param_inputs[index].text():
                if index ==3:  # Zoom
                    value = float(self.param_inputs[index].text()) * 100  # Convert zoom (0.0-1.0) to (0-100) for slider
                    self.sliders[index - 2].setValue(int(value)) 
                elif(index == 4):# Adjust index for slider (since no slider for flip)
                    value = int(self.param_inputs[index].text())
                    self.sliders[index - 2].setValue(value)
                elif(index==0):  # Rotation and Shear
                    value = int(self.param_inputs[index].text())
                    self.sliders[index].setValue(value)  # Adjust index for slider (since no slider for flip)
            self.update_live_sample()  # Update the live sample image
        return update_slider

    def sync_line_edit_with_slider(self, index):
        """Synchronize QLineEdit with slider when the slider value changes."""
        def update_line_edit(value):
            if index == 3:  # Zoom
                self.param_inputs[index].setText(f"{value / 100:.2f}")  # Convert slider (0-100) to float (0.0-1.0)
            else:  # Rotation and Shear
                self.param_inputs[index].setText(str(value))
            self.update_live_sample()  # Update the live sample image
        return update_line_edit

    def open_folder_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a Folder of images", "C:")
        if folder:
            path = Path(folder)
            self.foldername.setText(str(path))
            self.folder_clicked = True
            self.load_first_image(folder)  # Load the first image to preview

    def open_output_folder_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select an Output Folder", "C:")
        if folder:
            path = Path(folder)
            self.output_foldername.setText(str(path))
            self.output_folder_clicked = True
            self.check_if_ready()

    def check_if_ready(self):
        if(self.output_folder_clicked and self.folder_clicked):
            self.augment_button.setEnabled(True)
    def load_first_image(self, folder_path):
        """Load the first image from the folder to use for live preview."""
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                img_path = os.path.join(folder_path, file_name)
                self.current_image = cv2.imread(img_path)  # Read image using OpenCV
                self.update_live_sample()  # Display the image
                break

    def update_live_sample(self):
        """Update the live sample image preview based on the current augmentation parameters."""
        if self.current_image is None:
            return

        valid = True  # Track whether all inputs are valid

        # Get augmentation parameters from inputs, with default values if the inputs are empty
        try:
            rotation = int(self.param_inputs[0].text()) if self.param_inputs[0].text() else 0
            flip_lr = self.param_inputs[1].currentText()
            flip_tb = self.param_inputs[2].currentText()
            zoom = float(self.param_inputs[3].text()) if self.param_inputs[3].text() else 0.0
            shear = int(self.param_inputs[4].text()) if self.param_inputs[4].text() else 0
        except ValueError as e:
            self.append_log(f"Invalid input: {e}")
            return

        # Apply augmentations
        augmented_img = self.apply_augmentation(self.current_image.copy(), rotation, flip_lr, flip_tb, zoom, shear)
        # Convert the augmented image from BGR to RGB before displaying
        augmented_img_rgb = cv2.cvtColor(augmented_img, cv2.COLOR_BGR2RGB)
        # Convert the augmented image to QPixmap and display it in the QLabel
        height, width, channel = augmented_img_rgb.shape
        bytes_per_line = 3 * width
        q_img = QtGui.QImage(augmented_img_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(q_img)
        pixmap = pixmap.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)

    def apply_augmentation(self, img, rotation, flip_lr, flip_tb, zoom, shear):
        """Apply OpenCV-based augmentations."""
        height, width = img.shape[:2]

        # 1. Rotation
        M_rotate = cv2.getRotationMatrix2D((width / 2, height / 2), rotation, 1)
        img = cv2.warpAffine(img, M_rotate, (width, height))

        # 2. Horizontal flip
        if flip_lr == "Yes":
            img = cv2.flip(img, 1)

        # 3. Vertical flip
        if flip_tb == "Yes":
            img = cv2.flip(img, 0)

        # 4. Zoom (crop and resize)
        zoom_factor = 1 - zoom  # Zoom factor (less than 1 for zooming in)
        new_height, new_width = int(height * zoom_factor), int(width * zoom_factor)
        crop_img = img[int((height - new_height) / 2):int((height + new_height) / 2),
                       int((width - new_width) / 2):int((width + new_width) / 2)]
        img = cv2.resize(crop_img, (width, height))

        # 5. Shear (apply horizontal shear)
        shear_factor = shear / 100.0
        M_shear = np.array([[1, shear_factor, 0], [0, 1, 0]], dtype=np.float32)
        img = cv2.warpAffine(img, M_shear, (width, height))

        return img

    def process_augmentation_pipeline(self):
        self.log_output.clear()
        self.progress_bar.setValue(0)
        folder_path = self.foldername.text()

        # Get the total number of images in the folder
        total_images = len([f for f in os.listdir(folder_path) if f.endswith((".jpg", ".png"))])
        self.progress_bar.setMaximum(total_images)
        """Start augmentation in a separate thread."""
        # Get current parameter values
        rotation, flip_lr, flip_tb, zoom, shear = self.get_augmentation_parameters()
        # Check if all parameters are still at their default values
        if (rotation == 0 and
            flip_lr == "No" and
            flip_tb == "No" and
            zoom == 0.0 and
            shear == 0):
            self.append_log("No augment parameters selected. Please tweak the parameters and try again.")
            return
       # Create and start the worker thread
        self.worker = AugmentationWorker(self.foldername.text(), self.output_foldername.text(),
                                         (rotation, flip_lr, flip_tb, zoom, shear), total_images)

        # Connect signals to update the log and handle completion
        self.worker.log_signal.connect(self.append_log)
        self.worker.progress_signal.connect(self.update_progress_bar)
        self.worker.finished_signal.connect(lambda: self.append_log("Augmentation completed for all images."))

        # Start the worker thread
        self.worker.start()
    def update_progress_bar(self, value):
        """Update the progress bar with the given value."""
        self.progress_bar.setValue(value)

    def get_augmentation_parameters(self):
        """Get the current augmentation parameters."""
        rotation = int(self.param_inputs[0].text())
        flip_lr = self.param_inputs[1].currentText()
        flip_tb = self.param_inputs[2].currentText()
        zoom = float(self.param_inputs[3].text())
        shear = int(self.param_inputs[4].text())
        return rotation, flip_lr, flip_tb, zoom, shear

    def append_log(self, message):
        """Append log message to the QTextEdit."""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
