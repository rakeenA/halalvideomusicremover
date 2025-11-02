"""
Music removal module using Demucs
"""
import subprocess
import shutil
from pathlib import Path
from config import Config
import ffmpeg
import os

# Force torchaudio to use soundfile backend (avoids torchcodec issue)
os.environ['TORCHAUDIO_BACKEND'] = 'soundfile'

class MusicRemover:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback

    def remove_music(self, video_path):
        """
        Remove music from video, keeping only vocals and other sounds

        Args:
            video_path: Path to input video file

        Returns:
            Path to output video without music
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        Config.setup_directories()

        # Step 1: Extract audio from video
        if self.status_callback:
            self.status_callback("Step 1/4: Extracting audio from video...")
        if self.progress_callback:
            self.progress_callback(10)

        audio_path = self._extract_audio(video_path)

        # Step 2: Separate audio using Demucs
        if self.status_callback:
            self.status_callback("Step 2/4: Separating audio (this may take a while)...")
        if self.progress_callback:
            self.progress_callback(30)

        vocals_path = self._separate_audio(audio_path)

        # Step 3: Combine video with vocals-only audio
        if self.status_callback:
            self.status_callback("Step 3/4: Combining video with processed audio...")
        if self.progress_callback:
            self.progress_callback(70)

        output_path = self._combine_video_audio(video_path, vocals_path)

        # Step 4: Cleanup
        if self.status_callback:
            self.status_callback("Step 4/4: Cleaning up temporary files...")
        if self.progress_callback:
            self.progress_callback(90)

        self._cleanup(audio_path, vocals_path)

        if self.status_callback:
            self.status_callback("Music removal completed!")
        if self.progress_callback:
            self.progress_callback(100)

        return output_path

    def _extract_audio(self, video_path):
        """Extract audio from video using FFmpeg"""
        audio_path = Config.TEMP_DIR / f"{video_path.stem}_audio.wav"

        try:
            # Using ffmpeg-python
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='pcm_s16le', ac=2, ar='44100')
                .overwrite_output()
                .run(quiet=True, capture_stderr=True)
            )
        except Exception as e:
            # Fallback to subprocess
            command = [
                'ffmpeg', '-i', str(video_path),
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '44100', '-ac', '2',
                '-y', str(audio_path)
            ]
            subprocess.run(command, check=True, capture_output=True)

        return audio_path

    def _separate_audio(self, audio_path):
        """Separate audio using Demucs to isolate vocals"""
        # Run Demucs with MP3 output to avoid torchcodec issues
        command = [
            'python', '-m', 'demucs',
            '-n', Config.DEMUCS_MODEL,
            '--two-stems', Config.DEMUCS_TWO_STEMS,
            '--mp3',  # <--- ADD THIS LINE to output MP3 instead of WAV
            '--mp3-bitrate', '320',  # <--- ADD THIS LINE for quality
            '-o', str(Config.TEMP_DIR),
            str(audio_path)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Demucs error: {e.stderr}")

        # Find the vocals file - now it will be .mp3
        audio_name = audio_path.stem
        vocals_path = Config.TEMP_DIR / Config.DEMUCS_MODEL / audio_name / 'vocals.mp3'  # <--- Changed to .mp3

        if not vocals_path.exists():
            # Try alternative location
            vocals_path = Config.TEMP_DIR / Config.DEMUCS_MODEL / audio_name / 'no_vocals.mp3'  # <--- Changed to .mp3

        if not vocals_path.exists():
            raise FileNotFoundError(f"Demucs output not found. Expected at: {vocals_path}")

        return vocals_path

    def _combine_video_audio(self, video_path, audio_path):
        """Combine original video with new audio track"""
        output_path = Config.OUTPUT_DIR / f"{video_path.stem}_no_music.mp4"

        try:
            # Using ffmpeg-python
            video_stream = ffmpeg.input(str(video_path)).video
            audio_stream = ffmpeg.input(str(audio_path)).audio

            (
                ffmpeg
                .output(video_stream, audio_stream, str(output_path),
                       vcodec='copy', acodec='aac', audio_bitrate='192k')
                .overwrite_output()
                .run(quiet=True, capture_stderr=True)
            )
        except Exception as e:
            # Fallback to subprocess
            command = [
                'ffmpeg', '-i', str(video_path),
                '-i', str(audio_path),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-y', str(output_path)
            ]
            subprocess.run(command, check=True, capture_output=True)

        return output_path

    def _cleanup(self, audio_path, vocals_path):
        """Clean up temporary files"""
        try:
            # Remove extracted audio
            if audio_path.exists():
                audio_path.unlink()

            # Remove Demucs output directory
            demucs_output_dir = vocals_path.parent.parent
            if demucs_output_dir.exists():
                shutil.rmtree(demucs_output_dir)
        except Exception as e:
            print(f"Cleanup warning: {e}")
