__author__ = 'didzis'
import os
import subprocess
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class MuxAudioTab(QWidget):
    output_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.selected_video = None
        self.selected_audio = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Video selection
        self.video_label = QLabel("Select Video File:")
        layout.addWidget(self.video_label)

        self.video_btn = QPushButton("Browse Video")
        self.video_btn.clicked.connect(self.select_video)
        layout.addWidget(self.video_btn)

        # Audio selection
        self.audio_label = QLabel("Select Audio File:")
        layout.addWidget(self.audio_label)

        self.audio_btn = QPushButton("Browse Audio")
        self.audio_btn.clicked.connect(self.select_audio)
        layout.addWidget(self.audio_btn)

        # Mux button
        self.mux_btn = QPushButton("Mux Audio to Video")
        self.mux_btn.clicked.connect(self.mux_audio)
        layout.addWidget(self.mux_btn)

        # FFmpeg output display
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

        self.output_signal.connect(self.output_console.append)
        self.setLayout(layout)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv *.*)")
        if file_path:
            self.selected_video = file_path
            self.video_label.setText(f"Video: {os.path.basename(file_path)}")

    def select_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.aac *.wav *.flac *.*)")
        if file_path:
            self.selected_audio = file_path
            self.audio_label.setText(f"Audio: {os.path.basename(file_path)}")

    def mux_audio(self):
        if not self.selected_video or not self.selected_audio:
            QMessageBox.warning(self, "Warning", "Please select both video and audio files.")
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Save Muxed Video", os.path.splitext(self.selected_video)[0] + "_muxed.mkv", "Video Files (*.mkv)")
        if output_file:
            ffmpeg_cmd = f'ffmpeg -i "{self.selected_video}" -i "{self.selected_audio}" -c copy "{output_file}"'

            def run_ffmpeg():
                process = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
                for line in process.stdout:
                    self.output_signal.emit(line.strip())

            thread = threading.Thread(target=run_ffmpeg)
            thread.start()
