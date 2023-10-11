import pathlib
import sys
import time

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6 import QtCore, QtWidgets


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        self.addToolBar(NavigationToolbar(static_canvas, self))
        layout.addWidget(static_canvas)

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        bottom = QtCore.Qt.ToolBarArea.BottomToolBarArea
        self.addToolBar(bottom, NavigationToolbar(dynamic_canvas, self))

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0., 10., 501)
        self._static_ax.plot(t, np.tan(t), ".")

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        t = np.linspace(0., 10., 1024)
        # Set up a Line2D.
        y = np.sin(t + np.pi * time.time() / 30.)
        self._line, = self._dynamic_ax.plot(t, y)

        # Set up a file watcher to update plot
        self._watcher = QtCore.QFileSystemWatcher(
            [str(pathlib.Path(__file__).parent / 'samples')],
            self)
        self._watcher.directoryChanged.connect(self._update_canvas)

    def _update_canvas(self, watched_dir):
        t = np.linspace(0., 10., 1024)
        path = pathlib.Path(watched_dir)
        npy_files = sorted(
            [npy for npy in path.iterdir()],
            key=lambda f: f.stat().st_mtime)
        latest_npy = npy_files[-1]
        # Account for partially written files
        try:
            with open(latest_npy, 'rb') as npy_file:
                y = np.load(npy_file)
            self._line.set_data(t, y)
            self._line.figure.canvas.draw()
        except EOFError:
            pass


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
