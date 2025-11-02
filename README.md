# Halal Video Music Remover

**Easily download videos and remove haram background music using AI.**


[<img width="1640" height="664" alt="New Project (3)" src="https://github.com/user-attachments/assets/5f521e46-f4ec-46a6-9bba-a1d9453579d5" />](https://www.patreon.com/cw/rakeenalmuslim)

---

## 🚀 Features

- Download videos from YouTube and _many many_ other platforms
- Remove background music with Demucs (AI model)
- Works on Windows—just double-click and run
- No technical setup required

---

## ⚡ Quick Start (Windows)

0. Install Python while **making sure to ADD TO PATH**

<img width="670" height="430" alt="Screenshot 2025-11-02 213757" src="https://github.com/user-attachments/assets/c9233c22-ff9f-4b99-9651-a524cbf60a23" />


1. [Download the ZIP from Releases](https://github.com/rakeenA/halalvideomusicremover/releases)
2. Extract all files to a folder
3. Double-click `RUN.bat`

**On first run:**  
- The AI Demucs model (~300MB) will download automatically (only once)
- Make sure you have an internet connection

---

### 💡 Mac/Linux Users

1. Install Python 3.8+ and FFmpeg (`brew install ffmpeg` or `sudo apt install ffmpeg`)
2. Open terminal, run:
    ```
    pip install -r requirements.txt
    python -m src.main
    ```

---

## 📝 Troubleshooting

- **Demucs or FFmpeg error:**  
    - Make sure `ffmpeg.exe` and `ffprobe.exe` are in the main project folder
    - If you see TorchCodec errors, try:
      ```
      pip install --force-reinstall -r requirements.txt
      ```
- **yt-dlp YouTube download issues:**  
    - Run:
      ```
      pip install --upgrade yt-dlp
      ```
    - Sometimes YouTube updates break downloading—yt-dlp fixes this quickly.

---

## 💡 FAQ

**Q: Can I use this on Mac/Linux?**  
A: Yes! Install Python and FFmpeg yourself, then run as above. You can contact me for help.

**Q: Why does it say “FFmpeg not found”?**  
A: Make sure `ffmpeg.exe` and `ffprobe.exe` are present in the project folder OR FFmpeg is in your system PATH.

**Q: Is music 100% removed?**  
A: AI removes background music, but small artifacts or non-music sounds may remain.

---

## 🧑‍💻 About

- Project by [rakeenA](https://github.com/rakeenA)
- Music remover powered by [demucs](https://github.com/facebookresearch/demucs)
- Report issues or request features in [GitHub Issues](https://github.com/rakeenA/halalvideomusicremover/issues)

---

## ✨ License

Attribution-NonCommercial 4.0 International
Demucs model and code belong to Facebook Research
Please don't use my code for profit

---

**Enjoy easy, music-free video downloads!**
