"""
Video downloader module using yt-dlp
"""
import yt_dlp
from pathlib import Path
from src.config import Config
import threading

class VideoDownloader:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.downloaded_file = None

    def download_progress_hook(self, d):
        """Hook for yt-dlp to report download progress"""
        if d['status'] == 'downloading':
            if self.progress_callback:
                # Extract percentage
                percent_str = d.get('_percent_str', '0%').strip('%')
                try:
                    percent = float(percent_str)
                    self.progress_callback(percent)
                except:
                    pass

            if self.status_callback:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)

                status_text = f"Downloading: {self._format_bytes(downloaded)} / {self._format_bytes(total)}"
                if speed:
                    status_text += f" | Speed: {self._format_bytes(speed)}/s"
                if eta:
                    status_text += f" | ETA: {eta}s"

                self.status_callback(status_text)

        elif d['status'] == 'finished':
            self.downloaded_file = d['filename']
            if self.status_callback:
                self.status_callback("Download completed! Processing...")
            if self.progress_callback:
                self.progress_callback(100)

    def _format_bytes(self, bytes_count):
        """Format bytes to human-readable format"""
        if bytes_count == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.2f} TB"

    def download(self, url, custom_format=None):
        """
        Download video from URL

        Args:
            url: Video URL
            custom_format: Optional custom format string (overrides config)

        Returns:
            Path to downloaded file
        """
        if self.status_callback:
            self.status_callback("Starting download...")

        Config.setup_directories()

        ydl_opts = {
            'format': custom_format or Config.YTDLP_FORMAT,
            'merge_output_format': Config.YTDLP_MERGE_FORMAT,
            'outtmpl': str(Config.DOWNLOADS_DIR / '%(title)s.%(ext)s'),
            'progress_hooks': [self.download_progress_hook],
            'quiet': False,
            'no_warnings': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if self.status_callback:
                self.status_callback("Download successful!")

            if not self.downloaded_file:
                raise RuntimeError("Download failed: No file path returned by yt-dlp.")
            return Path(self.downloaded_file)


        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Download error: {str(e)}")
            raise

    def download_async(self, url, custom_format=None, completion_callback=None):
        """
        Download video in a separate thread

        Args:
            url: Video URL
            custom_format: Optional custom format string
            completion_callback: Callback function(success, result) when download completes
        """
        def download_thread():
            try:
                result = self.download(url, custom_format)
                if completion_callback:
                    completion_callback(True, result)
            except Exception as e:
                if completion_callback:
                    completion_callback(False, str(e))

        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        return thread
