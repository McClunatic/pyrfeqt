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

        signal_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar(signal_canvas, self))
        layout.addWidget(signal_canvas)

        spectro_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(spectro_canvas)
        bottom = QtCore.Qt.ToolBarArea.BottomToolBarArea
        self.addToolBar(bottom, NavigationToolbar(spectro_canvas, self))

        # Set up a Line2D.
        self._signal_ax = signal_canvas.figure.subplots()
        t = np.linspace(0., 10., 1024)
        y = np.sin(t + np.pi * time.time() / 30.)
        self._line, = self._signal_ax.plot(t, y)

        self._spectro_ax = spectro_canvas.figure.subplots()
        m = self._spectro_data = np.empty((300, 1024))
        for dt in range(300):
            m[dt, :] = np.sin(t + np.pi * (time.time() + 0.1 * dt) / 30.)
        self._image = self._spectro_ax.imshow(m)

        # Set up a file watcher to update plots
        self._watcher = QtCore.QFileSystemWatcher(
            [str(pathlib.Path(__file__).parent / 'samples')],
            self)
        self._watcher.directoryChanged.connect(self._update_canvases)

    def _update_canvases(self, watched_dir):
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
            m = self._spectro_data = np.roll(self._spectro_data, -1, 0)
            m[-1, :] = y
            self._image.set_data(m)
            self._image.figure.canvas.draw()

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
