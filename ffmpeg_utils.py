# ffmpeg_utils.py to standartize output console info
import subprocess
import threading
from PyQt6.QtCore import pyqtSignal, QObject

class FFmpegRunner(QObject):
    command_started = pyqtSignal(str)
    output_signal = pyqtSignal(str)
    command_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run_command(self, cmd):
        thread = threading.Thread(target=self._execute_command, args=(cmd,), daemon=True)
        thread.start()

    def _execute_command(self, cmd):
        self.command_started.emit(cmd)
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in process.stdout:
            self.output_signal.emit(line.strip())
        process.wait()
        self.command_finished.emit(process.returncode)
