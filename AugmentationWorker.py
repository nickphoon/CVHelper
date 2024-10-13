import os
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal

class AugmentationWorker(QThread):
    log_signal = Signal(str)  # Signal to emit log messages
    finished_signal = Signal()  # Signal to emit when the process is finished
    progress_signal = Signal(int)  # Signal to emit progress updates

    def __init__(self, folder_path, output_path, params, total_images):
        super().__init__()
        self.folder_path = folder_path
        self.output_path = output_path
        self.params = params
        self.total_images = total_images

    def run(self):
        rotation, flip_lr, flip_tb, zoom, shear = self.params

        # Counter for processed images
        processed_images = 0

        # Iterate over the images in the selected folder
        for image_file in os.listdir(self.folder_path):
            if image_file.endswith(".jpg") or image_file.endswith(".png"):
                img = cv2.imread(os.path.join(self.folder_path, image_file))
                augmented_img = self.apply_augmentation(img, rotation, flip_lr, flip_tb, zoom, shear)

                # Save the augmented image
                output_file = os.path.join(self.output_path, f"aug_{image_file}")
                cv2.imwrite(output_file, augmented_img)

                # Increment the processed images count
                processed_images += 1

                # Emit log message for each processed image
                self.log_signal.emit(f"Processed {image_file}")

                # Emit progress signal (processed_images / total_images * 100)
                self.progress_signal.emit(processed_images)

        # Emit finished signal when done
        self.finished_signal.emit()

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
