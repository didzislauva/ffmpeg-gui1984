import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox,
    QTextEdit, QHBoxLayout
)
from ffmpeg_utils import FFmpegRunner

class MuxAudioTab(QWidget):

    def __init__(self):
        super().__init__()

        self.video_file = None
        self.audio_file = None
        self.runner = FFmpegRunner()

        self.init_ui()
        self.setup_signals()

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

        self.setLayout(layout)

    def setup_signals(self):
        self.runner.command_started.connect(self.on_command_started)
        self.runner.output_signal.connect(self.output_console.append)
        self.runner.command_finished.connect(self.on_command_finished)

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
                f'ffmpeg -i "{self.video_file}" -i "{self.audio_file}" -map 0 -map 1:a '
                f'-c copy -metadata:s:a:1 language={lang_code} "{output_file}"'
            )
            self.runner.run_command(ffmpeg_cmd)

    def on_command_started(self, cmd):
        self.output_console.append(f"Running command:\n{cmd}\n{'-'*60}")

    def on_command_finished(self, returncode):
        status = "successfully completed." if returncode == 0 else f"finished with errors (code {returncode})."
        self.output_console.append(f"\nFFmpeg process {status}\n{'-'*60}")
