import sys
import os

from PySide6 import QtCore, QtWidgets


from SortImageWidget import SortImageWidget
from VideoToFramesWidget import VideoToFramesWidget
from DataAugmentorWidget import DataAugmentorWidget

class TabWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Data Transformer')
        self.setGeometry(100, 100, 500, 400)

        # Create a QTabWidget instance
        self.tab_widget = QtWidgets.QTabWidget()
       
        # to highlight color on tab selected
        self.tab_widget.tabBar().setStyleSheet("""
        QTabBar::tab {
            color: black;  /* Default tab title color */
        }
        QTabBar::tab:selected {
            color: green;    /* Selected tab title color */
        }
    """)
        self.tab_widget.setStyleSheet("font-size: 20px;")

        # Sort Image Tab
        self.sort_images_tab = SortImageWidget()
        self.tab_widget.addTab(self.sort_images_tab, "Sort Images by class")

   
        # Data Augmentation Tab
        self.tab2 = DataAugmentorWidget()
        self.tab_widget.addTab(self.tab2, "Data Augmentation")
        
        self.vidToFramesWidget = VideoToFramesWidget()
        self.tab_widget.addTab(self.vidToFramesWidget, "Video To Frames" )

        # VideoToFrames Tab
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TabWidget()
    window.show()

    sys.exit(app.exec())
