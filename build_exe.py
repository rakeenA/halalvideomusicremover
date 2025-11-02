import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller with bundled FFmpeg"""
    
    print("🔨 Building executable with bundled FFmpeg...")
    print("This may take a few minutes...")
    
    # Clean previous builds
    print("Cleaning previous builds...")
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
    
    # Check if FFmpeg exists
    ffmpeg_path = 'bin/ffmpeg.exe' if os.name == 'nt' else 'bin/ffmpeg'
    if not os.path.exists(ffmpeg_path):
        print(f"\n⚠️  WARNING: FFmpeg not found at {ffmpeg_path}")
        print("App will try to use system FFmpeg as fallback.")
        print("To bundle FFmpeg, download it and place it in 'bin/' folder")
    
    # PyInstaller arguments
    pyinstaller_args = [
        'src/main.py',
        '--name=VideoMusicRemover',
        '--onefile',
        '--windowed',
        '--add-data=src:src',
        '--hidden-import=tkinter',
        '--hidden-import=torch',
        '--hidden-import=demucs',
        '--hidden-import=yt_dlp',
        '--hidden-import=ffmpeg',
        '--hidden-import=soundfile',
        '--collect-all=demucs',
        '--collect-all=torch',
        '--collect-all=torchaudio',
        '--noconsole',
    ]
    
    # Add FFmpeg if it exists
    if os.path.exists(ffmpeg_path):
        ffmpeg_binary = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        pyinstaller_args.append(f'--add-binary={ffmpeg_path};bin')
        print(f"✅ Including bundled FFmpeg: {ffmpeg_path}")
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n✅ Executable built successfully!")
        print("📁 Location: dist/VideoMusicRemover.exe (Windows) or dist/VideoMusicRemover (macOS/Linux)")
        print("\n💡 You can now:")
        print("   1. Test the executable")
        print("   2. Upload it to GitHub Releases")
        print("   3. Share with users!")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    build_executable()
