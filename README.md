# FFmpeg GUI

A user-friendly graphical interface for simplifying common video and audio processing tasks using **FFmpeg**. Built with **Python** and **PyQt6**, this application provides multiple tabs for video conversion, audio extraction, resizing videos, and reducing file sizes with GPU support detection.

## Features

### Tabs Included:

- **Convert Video:** Convert videos between various formats. Dummy tab for now.
- **Extract Audio:** Extract specific audio streams from video files in multiple formats (e.g., mp3, aac, wav). Quite useful for my personal work.
- **Resize Video:** Easily resize videos to custom dimensions. Dummy tab for now.
- **Reduce Video:** Convert videos to approximately 2GB, keep a single selected audio track, adjust video bitrate dynamically, and choose between CPU or GPU encoding with automatic GPU detection and bit depth selection. Quite useful for my personal work.

### Highlights:
- **Dynamic Bitrate Adjustment:** Use a slider to select the desired video bitrate (1500–4000 kbps), with real-time display of estimated output file size.
- **GPU/CPU Encoding:** Automatically detects available GPU encoders (NVIDIA, AMD) and lets users select the preferred encoding method.
- **Bit Depth Selection:** Optionally choose between 8-bit and 10-bit encoding depending on GPU support.
- **Live FFmpeg Output:** Displays live FFmpeg command output directly in the GUI.

## Installation

### Prerequisites
- [Python](https://www.python.org/) 3.10+
- [FFmpeg](https://ffmpeg.org/) installed and added to system PATH.

### Dependencies

Install the required Python libraries using pip:

```sh
pip install PyQt6
```

### Setup

Clone the repository and run the application:

```sh
git clone https://github.com/didzislauva/ffmpeg-gui1984.git
cd ffmpeg-gui1984
python main.py
```

## Usage

### Convert, Extract audio, Resize, Reduce video filesize

1. Launch the application.
2. Select the appropriate tab for the task you wish to perform.
3. Click **"Browse"** to select your video file.
4. Adjust parameters (e.g., bitrate, audio stream, encoding method).
5. Click **"Convert"** or **"Extract"** to start processing.

### Reduce Tab Special Usage

- **Bitrate Slider:** Move the slider to choose the bitrate, observing estimated output size.
- **Encoding Method:** Choose CPU or GPU (auto-detected).
- **Bit Depth:** Select between 8-bit or 10-bit encoding (GPU support dependent).

## Screenshots

![image](https://github.com/user-attachments/assets/70ac2e56-ba95-4227-a5e1-dc8d83da9610)


## Contributing

Contributions are welcome! Feel free to open issues and submit pull requests.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- [FFmpeg](https://ffmpeg.org/)
- [PyQt](https://www.riverbankcomputing.com/software/pyqt/)

