import os
import subprocess
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox,
    QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

class MuxAudioTab(QWidget):
    output_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.video_file = None
        self.audio_file = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Video file selection
        self.video_label = QLabel("Select Video File:")
        layout.addWidget(self.video_label)

        self.video_btn = QPushButton("Browse Video")
        self.video_btn.clicked.connect(self.select_video)
        layout.addWidget(self.video_btn)

        # Audio file selection
        self.audio_label = QLabel("Select Audio File:")
        layout.addWidget(self.audio_label)

        self.audio_btn = QPushButton("Browse Audio")
        self.audio_btn.clicked.connect(self.select_audio)
        layout.addWidget(self.audio_btn)

        # Language selection
        language_layout = QHBoxLayout()
        language_label = QLabel("Audio Track Language:")
        language_layout.addWidget(language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "lav (Latvian)",
            "eng (English)",
            "rus (Russian)",
            "ger (German)",
            "fre (French)"
        ])
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)

        # Mux button
        self.mux_btn = QPushButton("Mux Audio into Video")
        self.mux_btn.clicked.connect(self.mux_audio_video)
        layout.addWidget(self.mux_btn)

        # FFmpeg output
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

        self.output_signal.connect(self.output_console.append)
        self.setLayout(layout)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv *.*)")
        if file_path:
            self.video_file = file_path
            self.video_label.setText(f"Video: {os.path.basename(file_path)}")

    def select_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio", "", "Audio Files (*.mp3 *.aac *.wav *.m4a *.*)")
        if file_path:
            self.audio_file = file_path
            self.audio_label.setText(f"Audio: {os.path.basename(file_path)}")

    def mux_audio_video(self):
        if not self.video_file or not self.audio_file:
            self.output_console.append("Please select both video and audio files.")
            return

        lang_code = self.language_combo.currentText().split(' ')[0]
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Muxed Video", os.path.splitext(self.video_file)[0] + "_muxed.mkv", "MKV Files (*.mkv)"
        )

        if output_file:
            ffmpeg_cmd = (
                f'ffmpeg -i "{self.video_file}" -i "{self.audio_file}" -map 0 -map 1:a -c copy -metadata:s:a:1 language={lang_code} "{output_file}"'
            )

            def run_ffmpeg():
                process = subprocess.Popen(
                    ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace'
                )
                for line in process.stdout:
                    self.output_signal.emit(line.strip())

            threading.Thread(target=run_ffmpeg).start()
