"""
Configuration file for Video Downloader & Music Remover
"""
import os
from pathlib import Path

class Config:
    # Base directories
    BASE_DIR = Path.cwd()
    DOWNLOADS_DIR = BASE_DIR / "downloads"
    TEMP_DIR = BASE_DIR / "temp"
    OUTPUT_DIR = BASE_DIR / "output"

    # yt-dlp settings
    YTDLP_FORMAT = '''--restrict-filenames -output "%(id)s.%(ext)s" [URL] --merge-output-format "mp4" bestvideo[height<=1080]+bestaudio/best[height<=1080]'''
    YTDLP_MERGE_FORMAT = "mp4"

    # Demucs settings
    DEMUCS_MODEL = "htdemucs"  # Can be changed to mdx_extra_q for faster processing
    DEMUCS_TWO_STEMS = "vocals"  # Only separate vocals, keeping other sounds

    # FFmpeg settings
    FFMPEG_PRESET = "medium"  # ultrafast, fast, medium, slow, veryslow

    # GUI settings
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 500

    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DOWNLOADS_DIR, cls.TEMP_DIR, cls.OUTPUT_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
