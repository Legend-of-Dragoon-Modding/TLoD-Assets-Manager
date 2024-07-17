"""

OpenGL Context Window:
Generate an OpenGL Context Window por PyQt.

Copyright (C) 2024 DooMMetaL

"""

import ctypes
import sys

from OpenGL.GL import glViewport, glClearColor, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
import OpenGL.wrapper
from PyQt6.QtCore import Qt
import numpy as np

import OpenGL
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat as QGLFormat
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f'OpenGL Window')
        self.setFixedSize(600,600)
        self.gl_widget = glWidget(self)
        self.gl_widget.setMaximumSize(600,600)
        self.gl_widget.format().setVersion(4, 2)
        self.gl_widget.format().setProfile(QGLFormat.OpenGLContextProfile.CoreProfile)
        self.setCentralWidget(self.gl_widget)
        self.show()

class glWidget(QOpenGLWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

    def initializeGL(self):
        pass

    def resizeGL(self, w: int, h: int) -> None:
        # override resizeGL method to handle screen resizing
        glViewport(0, 0, w, h)

    def paintGL(self):
        # override paintGL method to customize how to draw on screen
        glClearColor(0.0, 0.0, 0.5, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())