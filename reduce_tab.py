import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox,
    QSlider, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from ffmpeg_utils import FFmpegRunner

class ReduceTab(QWidget):

    def __init__(self):
        super().__init__()

        self.selected_file = None
        self.audio_streams = []
        self.gpu_encoder = None
        self.runner = FFmpegRunner()

        self.init_ui()
        self.setup_signals()
        self.check_gpu_support()

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = QLabel("Select Video File:")
        layout.addWidget(self.file_label)

        self.select_btn = QPushButton("Browse")
        self.select_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_btn)

        self.stream_label = QLabel("Select Audio Stream (only this will be left):")
        layout.addWidget(self.stream_label)

        self.stream_combo = QComboBox()
        layout.addWidget(self.stream_combo)

        bitrate_layout = QHBoxLayout()
        self.bitrate_label = QLabel("Bitrate (kbps):")
        bitrate_layout.addWidget(self.bitrate_label)

        self.bitrate_slider = QSlider(Qt.Orientation.Horizontal)
        self.bitrate_slider.setRange(1500, 4000)
        self.bitrate_slider.setValue(2500)
        self.bitrate_slider.valueChanged.connect(self.update_filesize)
        bitrate_layout.addWidget(self.bitrate_slider)

        self.bitrate_value = QLabel("2500")
        bitrate_layout.addWidget(self.bitrate_value)
        layout.addLayout(bitrate_layout)

        self.filesize_label = QLabel("Estimated Size: 0 MB")
        layout.addWidget(self.filesize_label)

        encoding_layout = QHBoxLayout()
        self.encoding_label = QLabel("Encoding Method:")
        encoding_layout.addWidget(self.encoding_label)

        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["CPU", "GPU"])
        self.encoding_combo.currentTextChanged.connect(self.update_presets)
        encoding_layout.addWidget(self.encoding_combo)

        self.bit_depth_label = QLabel("Bit Depth:")
        encoding_layout.addWidget(self.bit_depth_label)

        self.bit_depth_combo = QComboBox()
        self.bit_depth_combo.addItems(["8-bit", "10-bit"])
        encoding_layout.addWidget(self.bit_depth_combo)
        layout.addLayout(encoding_layout)

        preset_layout = QHBoxLayout()
        self.preset_label = QLabel("Quality Preset:")
        preset_layout.addWidget(self.preset_label)

        self.preset_combo = QComboBox()
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)

        self.update_presets()

        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.convert_video)
        layout.addWidget(self.convert_btn)

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

        self.setLayout(layout)

    def setup_signals(self):
        self.runner.command_started.connect(self.on_command_started)
        self.runner.output_signal.connect(self.output_console.append)
        self.runner.command_finished.connect(self.on_command_finished)

    def update_presets(self):
        method = self.encoding_combo.currentText()
        self.preset_combo.clear()
        presets = (["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow", "placebo"]
                   if method == "CPU" else
                   ["slow", "medium", "fast", "hp", "hq", "bd", "ll", "llhq", "llhp", "lossless", "losslesshp"])
        self.preset_combo.addItems(presets)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv *.*)")
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"File: {os.path.basename(file_path)}")
            self.get_audio_streams()
            self.update_filesize()

    def get_audio_streams(self):
        self.audio_streams.clear()
        self.stream_combo.clear()

        ffprobe_cmd = f'ffprobe -v error -select_streams a -show_streams -of json "{self.selected_file}"'
        result = subprocess.run(ffprobe_cmd, shell=True, capture_output=True, text=True)
        streams_info = json.loads(result.stdout)

        for index, stream in enumerate(streams_info.get("streams", [])):
            codec = stream.get("codec_name", "unknown")
            language = stream.get("tags", {}).get("language", "unknown")
            desc = f"Stream {index} - {codec} ({language})"
            self.audio_streams.append(index)
            self.stream_combo.addItem(desc, index)

    def update_filesize(self):
        bitrate = self.bitrate_slider.value()
        self.bitrate_value.setText(str(bitrate))

        if self.selected_file:
            duration = self.get_video_duration(self.selected_file)
            size_mb = ((bitrate * duration) / 8) / 1024
            self.filesize_label.setText(f"Estimated Size: {size_mb:.2f} MB")

    def get_video_duration(self, file):
        cmd = f'ffprobe -v error -show_entries format=duration -of json "{file}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        duration = json.loads(result.stdout)['format']['duration']
        return float(duration)

    def check_gpu_support(self):
        self.gpu_encoder = ('h264_nvenc' if subprocess.run('ffmpeg -h encoder=h264_nvenc', shell=True, capture_output=True).returncode == 0 else
                            'h264_amf' if subprocess.run('ffmpeg -h encoder=h264_amf', shell=True, capture_output=True).returncode == 0 else None)

    def convert_video(self):
        encoding_method = self.encoding_combo.currentText()
        codec = self.gpu_encoder if encoding_method == "GPU" and self.gpu_encoder else "libx264"
        filters = '-vf "format=yuv420p"' if self.bit_depth_combo.currentText() == "8-bit" else ""

        output_file, _ = QFileDialog.getSaveFileName(self, "Save Video", os.path.splitext(self.selected_file)[0] + "_converted.mkv", "Video Files (*.mkv)")
        if output_file:
            ffmpeg_cmd = f'ffmpeg -i "{self.selected_file}" -map 0:v:0 -map 0:a:{self.stream_combo.currentData()} -c:v {codec} {filters} -preset {self.preset_combo.currentText()} -b:v {self.bitrate_slider.value()}k -c:a copy "{output_file}"'
            self.runner.run_command(ffmpeg_cmd)

    def on_command_started(self, cmd):
        self.output_console.append(f"Running command:\n{cmd}\n{'-'*60}")

    def on_command_finished(self, returncode):
        status = "successfully completed." if returncode == 0 else f"finished with errors (code {returncode})."
        self.output_console.append(f"\nFFmpeg process {status}\n{'-'*60}")
