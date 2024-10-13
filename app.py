import sys
import os

from PySide6 import QtCore, QtWidgets


from SortImageWidget import SortImageWidget
from VideoToFramesWidget import VideoToFramesWidget
from DataAugmentorWidget import DataAugmentorWidget

class TabWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('CVHelper')
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #e6f0dc; color:black;")
        # Create a QLabel for the header and set alignment to center
        self.header_label = QtWidgets.QLabel("CVHelper", self)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 25px; font-weight: bold; color:#55883b;")
        # Create a QTabWidget instance
        self.tab_widget = QtWidgets.QTabWidget()
       
       
        # to highlight color on tab selected
        self.tab_widget.tabBar().setStyleSheet("""
        QTabBar::tab {
        
            color: black;  /* Default tab title color */
           
        }
        QTabBar::tab:selected {
            
            color: #3b8848;    /* Selected tab title color */
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
        main_layout.addWidget(self.header_label)
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TabWidget()
    window.show()

    sys.exit(app.exec())
