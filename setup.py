from cx_Freeze import setup, Executable
import os
import sys

# Define paths to include
ffmpeg_path = os.path.join("ffmpeg-7.0.1", "bin", "ffmpeg.exe")
tesseract_path = os.path.join("Tesseract-OCR", "tesseract.exe")
tessdata_path = os.path.join("Tesseract-OCR", "tessdata")
config_toml_path = os.path.join(".streamlit", "config.toml")  # Path to config.toml

# Ensure paths exist
assert os.path.exists(ffmpeg_path), f"FFmpeg path does not exist: {ffmpeg_path}"
assert os.path.exists(tesseract_path), f"Tesseract path does not exist: {tesseract_path}"
assert os.path.exists(tessdata_path), f"Tessdata path does not exist: {tessdata_path}"
assert os.path.exists(config_toml_path), f"config.toml path does not exist: {config_toml_path}"

# Build options
build_exe_options = {
    "packages": ["streamlit", "pandas", "cv2", "pytesseract"],
    "excludes": [],
    "include_files": [
        (ffmpeg_path, os.path.join("ffmpeg", "bin", "ffmpeg.exe")),
        (tesseract_path, os.path.join("Tesseract-OCR", "tesseract.exe")),
        (tessdata_path, os.path.join("Tesseract-OCR", "tessdata")),
        (config_toml_path, os.path.join(".streamlit", "config.toml")) 
    ],
}

base = None
if sys.platform == "win32":
    base = "Console"

setup(
    name="StreamlitApp",
    version="1.0",
    description="A simple Streamlit app",
    options={"build_exe": build_exe_options},
    executables=[Executable("launcher.py", base=base)],
)
