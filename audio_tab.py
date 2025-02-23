import os
import subprocess
import json
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QTextEdit
)
from PyQt6.QtCore import pyqtSignal

class AudioTab(QWidget):
    output_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.selected_file = None
        self.audio_streams = []  # List of detected audio streams
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = QLabel("Select Video File:")
        layout.addWidget(self.file_label)

        self.select_btn = QPushButton("Browse")
        self.select_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_btn)

        self.stream_label = QLabel("Select Audio Stream:")
        layout.addWidget(self.stream_label)

        self.stream_combo = QComboBox()
        self.stream_combo.currentIndexChanged.connect(self.sync_output_format)
        layout.addWidget(self.stream_combo)

        self.audio_format_label = QLabel("Output Format:")
        layout.addWidget(self.audio_format_label)

        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "aac", "wav", "ac3", "flac", "opus"])
        layout.addWidget(self.audio_format_combo)

        self.extract_btn = QPushButton("Extract Audio")
        self.extract_btn.clicked.connect(self.run_ffmpeg_audio_extract)
        layout.addWidget(self.extract_btn)

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

        self.output_signal.connect(self.update_console)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv *.*)")
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"File: {os.path.basename(file_path)}")
            self.get_audio_streams()

    def get_audio_streams(self):
        self.audio_streams.clear()
        self.stream_combo.clear()

        cmd = f'ffprobe -v error -select_streams a -show_streams -of json "{self.selected_file}"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            streams_info = json.loads(result.stdout)

            if "streams" in streams_info:
                for index, stream in enumerate(streams_info["streams"]):
                    codec = stream.get("codec_name", "unknown")
                    language = stream.get("tags", {}).get("language", "unknown")
                    description = f"Stream {index} - {codec} ({language})"
                    self.audio_streams.append((index, codec))
                    self.stream_combo.addItem(description, (index, codec))

            if not self.audio_streams:
                self.stream_combo.addItem("No audio streams found")

        except Exception as e:
            self.output_console.setText(f"Error retrieving streams: {e}")

    def sync_output_format(self):
        if self.stream_combo.count() > 0:
            _, codec = self.stream_combo.currentData()
            current_formats = [self.audio_format_combo.itemText(i) for i in range(self.audio_format_combo.count())]

            if codec not in current_formats:
                self.audio_format_combo.addItem(codec)

            self.audio_format_combo.setCurrentText(codec)

    def run_ffmpeg_audio_extract(self):
        if not self.selected_file:
            self.output_console.setText("Please select a file first.")
            return

        if not self.audio_streams:
            self.output_console.setText("No audio streams found.")
            return

        stream_index, original_codec = self.stream_combo.currentData()
        chosen_format = self.audio_format_combo.currentText()
        output_file = os.path.splitext(self.selected_file)[0] + f"_stream{stream_index}." + chosen_format

        # Choose codec copy only if formats match, otherwise convert
        codec_option = "-c:a copy" if original_codec == chosen_format else f"-c:a {self.get_audio_codec(chosen_format)}"

        cmd = f'ffmpeg -i "{self.selected_file}" -map 0:a:{stream_index} {codec_option} "{output_file}"'

        threading.Thread(target=self.run_command, args=(cmd,)).start()
    def get_audio_codec(self, format):
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "wav": "pcm_s16le",
            "ac3": "ac3",
            "flac": "flac",
            "opus": "libopus"
        }
        return codec_map.get(format, "copy")
        
    def run_command(self, cmd):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            self.output_signal.emit(line.strip())

    def update_console(self, text):
        self.output_console.append(text)
