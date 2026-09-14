from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lesson_converter_app.converter import convert_file, detect_csv_format


class DropConvertWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Lesson Converter")
        self.resize(700, 420)
        self.setAcceptDrops(True)

        self.drop_box = QLabel("Drag a CSV file here\n\nor\nclick to choose a file")
        self.drop_box.setAlignment(Qt.AlignCenter)
        self.drop_box.setWordWrap(True)
        self.drop_box.setFixedHeight(220)
        self.drop_box.setStyleSheet(
            "QLabel { background: #f0f4ff; border: 3px dashed #4a6bf3; border-radius: 18px; font-size: 22px; color: #1f2937; }"
        )
        self.drop_box.mousePressEvent = self._handle_box_click

        self.choose_button = QPushButton("Choose CSV")
        self.choose_button.clicked.connect(self._choose_file)

        self.status_label = QLabel("Waiting for a FACTS or Planbook CSV file.")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.drop_box)
        layout.addWidget(self.choose_button)
        layout.addWidget(self.status_label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        file_url = urls[0].toLocalFile()
        if file_url:
            self.process_file(Path(file_url))
        event.acceptProposedAction()

    def _handle_box_click(self, event) -> None:  # type: ignore[no-untyped-def]
        self._choose_file()

    def _choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose CSV file", str(Path.home()), "CSV Files (*.csv)")
        if path:
            self.process_file(Path(path))

    def process_file(self, file_path: Path) -> None:
        if file_path.suffix.lower() != ".csv":
            self.status_label.setText("Only CSV files are supported.")
            return

        try:
            detected_format = detect_csv_format(file_path)
            output_path, target_format = convert_file(file_path)
            self.status_label.setText(
                f"Detected {detected_format} format. Created {target_format} file at:\n{output_path}"
            )
        except ValueError as exc:
            self.status_label.setText(str(exc))
            QMessageBox.critical(self, "CSV Error", str(exc))
        except Exception as exc:  # pragma: no cover
            self.status_label.setText(f"Could not process the file: {exc}")
            QMessageBox.critical(self, "Unexpected Error", str(exc))


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Lesson Converter")
    window = DropConvertWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
