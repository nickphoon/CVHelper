import os
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path

class DataAugmentorWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_folder_clicked = False
        self.folder_clicked = False

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Shortened description at the top
        description = QtWidgets.QLabel("Augment images in a folder using image augmentation techniques with Keras ImageDataGenerator.")
        description.setStyleSheet("font-size: 16px; text-align: center;")
        description.setContentsMargins(0, 10, 0, 20)
        description.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)

        # Create a QFormLayout for parameters in the center
        param_layout = QtWidgets.QFormLayout()
        param_layout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Initialize lists to store the input fields and corresponding warning labels
        self.param_inputs = []
        self.warning_labels = []

        # Parameters for ImageDataGenerator with descriptions and ranges
        param_info = [
            ("Rotation (Degrees)", "Rotation amount", "0-180", QtGui.QIntValidator(0, 180)),
            ("Flip Left-Right", "Flip image horizontally", "yes/no", None),
            ("Flip Top-Bottom", "Flip image vertically", "yes/no", None),
            ("Zoom (Range)", "Zoom range", "0.0-1.0", QtGui.QDoubleValidator(0.0, 1.0, 2)),
            ("Shear (Degrees)", "Shear range", "0-45", QtGui.QIntValidator(0, 45))
        ]

        # Add the parameters with validators and descriptions to the form layout
        for i, (title, desc, range_text, validator) in enumerate(param_info):
            label = QtWidgets.QLabel(f"{title}:")
            label.setStyleSheet("font-size: 14px;")
            
            if i == 1 or i == 2:  # Drop-down menus for flip options
                combo_box = QtWidgets.QComboBox(self)
                combo_box.setFixedWidth(50)
                combo_box.addItems(["No", "Yes"])  # Default to "No"
                combo_box.setCurrentText("No")
                combo_box.currentTextChanged.connect(self.validate_inputs)  # Connect validation function
                param_layout.addRow(label, combo_box)
                self.param_inputs.append(combo_box)

                # Add warning label (hidden by default)
                warning_label = QtWidgets.QLabel("")
                warning_label.setStyleSheet("font-size: 12px; color: red;")
                warning_label.setVisible(False)
                param_layout.addRow(warning_label)
                self.warning_labels.append(warning_label)

            else:  # QLineEdit for number inputs
                line_edit = QtWidgets.QLineEdit(self)
                line_edit.setFixedWidth(50)
                line_edit.setText("0")  # Set default value to 0
                if validator:
                    line_edit.setValidator(validator)  # Apply validator to ensure input is within range
                    line_edit.textChanged.connect(self.validate_inputs)  # Connect validation function

                param_layout.addRow(label, line_edit)
                self.param_inputs.append(line_edit)

                # Add a warning label for each input
                warning_label = QtWidgets.QLabel("")
                warning_label.setStyleSheet("font-size: 12px; color: red;")
                warning_label.setVisible(False)  # Initially hidden
                param_layout.addRow(warning_label)
                self.warning_labels.append(warning_label)

            # Add a description and range label for guidance
            desc_label = QtWidgets.QLabel(f"{desc} ({range_text})")
            desc_label.setStyleSheet("font-size: 12px; color: grey;")
            param_layout.addRow(desc_label)

        # Center the parameters layout in the main layout
        main_layout.addLayout(param_layout)

        # Folder Path
        folder_path_label = QtWidgets.QLabel("Folder Path:")
        folder_path_label.setStyleSheet("font-size: 16px;")
        folder_layout = QtWidgets.QHBoxLayout()
        folder_browser_btn = QtWidgets.QPushButton('Select Image Folder')
        folder_browser_btn.setStyleSheet("font-size: 16px;")
        folder_browser_btn.clicked.connect(self.open_folder_dialog)
        folder_layout.addWidget(folder_browser_btn)
        self.foldername = QtWidgets.QLabel("")
        self.foldername.setStyleSheet("font-size: 16px;")
        folder_layout.addWidget(self.foldername)
        main_layout.addLayout(folder_layout)

        # Output Folder Path
        output_path_layout = QtWidgets.QHBoxLayout()
        output_folder_label = QtWidgets.QLabel("Output Folder Path:")
        output_folder_label.setStyleSheet("font-size: 16px;")
        output_browser_btn = QtWidgets.QPushButton('Select Output folder')
        output_browser_btn.setStyleSheet("font-size: 16px;")
        output_browser_btn.clicked.connect(self.open_output_folder_dialog)
        output_path_layout.addWidget(output_browser_btn)
        self.output_foldername = QtWidgets.QLabel("")
        self.output_foldername.setStyleSheet("font-size: 16px;")
        output_path_layout.addWidget(self.output_foldername)
        main_layout.addLayout(output_path_layout)

        # Button to start augmentation
        self.augment_button = QtWidgets.QPushButton('Augment Images')
        self.augment_button.setEnabled(False)  # Disable by default until validation passes
        self.augment_button.setStyleSheet("font-size: 16px;")
        self.augment_button.clicked.connect(self.process_augmentation_pipeline)
        main_layout.addWidget(self.augment_button)

        # Output log for showing progress (QTextEdit)
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)  # Make it read-only
        self.log_output.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.log_output)

    def validate_inputs(self):
        """Validate each input and show warnings specific to each one."""
        valid = True

        for i, input_widget in enumerate(self.param_inputs):
            if isinstance(input_widget, QtWidgets.QLineEdit):
                validator = input_widget.validator()
                state = validator.validate(input_widget.text(), 0)[0] if validator else QtGui.QValidator.Acceptable
                if state != QtGui.QValidator.Acceptable:
                    valid = False
                    self.warning_labels[i].setText("Not in range")
                    self.warning_labels[i].setVisible(True)  # Show warning
                else:
                    self.warning_labels[i].setVisible(False)  # Hide warning if input is valid
            else:
                self.warning_labels[i].setVisible(False)

        self.augment_button.setEnabled(valid)

    def open_folder_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a Folder of images", "C:")
        if folder:
            path = Path(folder)
            self.foldername.setText(str(path))
            self.folder_clicked = True
            self.check_if_ready()

    def open_output_folder_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select an Output Folder", "C:")
        if folder:
            path = Path(folder)
            self.output_foldername.setText(str(path))
            self.output_folder_clicked = True
            self.check_if_ready()

    def check_if_ready(self):
        if self.folder_clicked and self.output_folder_clicked:
            self.augment_button.setEnabled(True)

    def process_augmentation_pipeline(self):
        from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img, array_to_img  # Lazy import here
        self.log_output.clear()
        folder_path = self.foldername.text()
        output_path = self.output_foldername.text()

        # Read augmentation parameters from input fields
        rotation_range = int(self.param_inputs[0].text())
        flip_lr = self.param_inputs[1].currentText()
        flip_tb = self.param_inputs[2].currentText()
        zoom_range = float(self.param_inputs[3].text())
        shear_range = int(self.param_inputs[4].text())
        if(rotation_range ==0 and flip_lr == "No" and flip_tb =="No" and zoom_range==0 and shear_range==0):
            self.append_log("No augmentations were applied to any images.")
            return
        # Configure ImageDataGenerator
        datagen = ImageDataGenerator(
            rotation_range=rotation_range,
            horizontal_flip=flip_lr,
            vertical_flip=flip_tb,
            zoom_range=zoom_range,
            shear_range=shear_range / 100  # Shear range is a fraction
        )

        # Iterate over the images in the selected folder
        for image_file in os.listdir(folder_path):
            if image_file.endswith(".jpg") or image_file.endswith(".png"):
                img = load_img(os.path.join(folder_path, image_file))
                x = img_to_array(img)
                x = x.reshape((1,) + x.shape)  # Reshape image for the generator

              

                # Generate augmented images and save them
                i = 0
                for batch in datagen.flow(x, batch_size=1, save_to_dir=output_path, save_prefix="aug", save_format="jpg"):
                    i += 1
                    if i >= 2:  # Generate 10 augmented images per file
                        break

                self.append_log(f"Processed {image_file}")

        self.append_log("Augmentation completed for all images.")

    def append_log(self, message):
        """Append log message to the QTextEdit and process events to display it immediately."""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
        QtCore.QCoreApplication.processEvents()
