"""
Video Downloader & Music Remover - Main GUI Application
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import webbrowser
import threading
import queue
import os
import sys
import random
import time
import subprocess

# Check for FFmpeg in same directory as .exe
def setup_ffmpeg():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running from source
        app_dir = os.path.dirname(__file__)
    
    ffmpeg_path = os.path.join(app_dir, 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        os.environ['PATH'] = app_dir + os.pathsep + os.environ.get('PATH', '')

setup_ffmpeg()


# ===== NEW: Setup bundled FFmpeg path =====
def setup_ffmpeg_path():
    """Setup FFmpeg path for bundled or system installation"""
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        ffmpeg_dir = os.path.join(sys._MEIPASS, 'bin')
    else:
        # Running from source
        ffmpeg_dir = os.path.join(os.path.dirname(__file__), '..', 'bin')
    
    # Add to PATH so subprocess can find it
    if os.path.exists(ffmpeg_dir):
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
        return True
    return False

# Call this at startup
setup_ffmpeg_path()
# ===== END NEW =====

from src.config import Config
from src.downloader import VideoDownloader
from src.music_remover import MusicRemover

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader & Music Remover")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # Theme settings
        self.dark_mode = False
        self.apply_light_theme()
        
        # Setup directories
        Config.setup_directories()

        # Processing state
        self.is_processing = False
        self.current_video_path = None

        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()

        # Create GUI
        self.create_widgets()

        # Start queue processor
        self.process_queue()

    def apply_light_theme(self):
        """Apply light theme colors"""
        self.bg_color = "#f0f0f0"
        self.accent_color = "#2196F3"
        self.success_color = "#4CAF50"
        self.error_color = "#f44336"
        self.text_color = "#333333"
        self.secondary_text = "#666666"
        self.log_bg = "#ffffff"
        self.log_text_color = "#333333"
        self.button_bg = "white"
        self.button_hover = "#e0e0e0"
        self.dark_mode = False

    def apply_dark_theme(self):
        """Apply dark theme colors"""
        self.bg_color = "#1e1e1e"
        self.accent_color = "#64B5F6"
        self.success_color = "#66BB6A"
        self.error_color = "#EF5350"
        self.text_color = "#ffffff"
        self.secondary_text = "#b0bec5"
        self.log_bg = "#2d2d2d"
        self.log_text_color = "#ffffff"
        self.button_bg = "#2d2d2d"
        self.button_hover = "#3d3d3d"
        self.dark_mode = True

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.dark_mode:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()
        
        self.root.configure(bg=self.bg_color)
        self.recreate_widgets()

    def recreate_widgets(self):
        """Recreate all widgets with new theme"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets with modern styling"""
        self.root.configure(bg=self.bg_color)
        
        # Top bar with theme toggle and donate button
        top_bar = tk.Frame(self.root, bg=self.bg_color)
        top_bar.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        # Theme toggle button (left side)
        theme_btn = tk.Button(
            top_bar,
            text="🌙 Dark Mode" if not self.dark_mode else "☀️ Light Mode",
            command=self.toggle_theme,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.text_color,
            activebackground=self.button_hover,
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            bd=1,
            highlightthickness=1,
            highlightbackground="#cccccc" if not self.dark_mode else "#444444"
        )
        theme_btn.pack(side=tk.LEFT)
        
        # Spacer
        spacer = tk.Frame(top_bar, bg=self.bg_color)
        spacer.pack(side=tk.LEFT, expand=True)
        
        # Donate button (right side)
        donate_btn = tk.Button(
            top_bar,
            text="❤️ Support Developer",
            command=self.open_donate_link,
            font=("Segoe UI", 9, "bold"),
            bg="#FF6B6B",
            fg="white",
            activebackground="#FF5252",
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0
        )
        donate_btn.pack(side=tk.RIGHT)

        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Title
        title_frame = tk.Frame(main_container, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = tk.Label(
            title_frame,
            text="Video Downloader & Music Remover",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Download videos and remove background music using AI",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        subtitle_label.pack()
        
        # Developer credit
        credit_label = tk.Label(
            title_frame,
            text="Run by a student living in Bangladesh 🇧🇩",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        credit_label.pack(pady=(3, 0))

        # Separator
        separator = ttk.Separator(main_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=12)

        # URL Frame
        url_frame = tk.Frame(main_container, bg=self.bg_color)
        url_frame.pack(fill=tk.X, pady=10)

        url_label = tk.Label(
            url_frame,
            text="📎 Video URL:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        url_label.pack(anchor=tk.W)

        self.url_entry = tk.Entry(
            url_frame,
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground="#cccccc" if not self.dark_mode else "#444444",
            highlightcolor=self.accent_color,
            bg=self.log_bg,
            fg=self.log_text_color
        )
        self.url_entry.pack(fill=tk.X, pady=5, ipady=5)
        self.url_entry.bind('<Return>', lambda e: self.start_processing())

        # Format Frame
        format_frame = tk.Frame(main_container, bg=self.bg_color)
        format_frame.pack(fill=tk.X, pady=5)

        format_label = tk.Label(
            format_frame,
            text="⚙️ Download Format (optional):",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.secondary_text
        )
        format_label.pack(anchor=tk.W)

        self.format_entry = tk.Entry(
            format_frame,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground="#cccccc" if not self.dark_mode else "#444444",
            highlightcolor=self.accent_color,
            bg=self.log_bg,
            fg=self.log_text_color
        )
        self.format_entry.pack(fill=tk.X, pady=5, ipady=3)
        self.format_entry.insert(0, Config.YTDLP_FORMAT)

        # Buttons Frame
        button_frame = tk.Frame(main_container, bg=self.bg_color)
        button_frame.pack(pady=12)

        self.process_btn = tk.Button(
            button_frame,
            text="▶ Download & Remove Music",
            command=self.start_processing,
            font=("Segoe UI", 11, "bold"),
            bg=self.success_color,
            fg="white",
            activebackground="#45a049" if not self.dark_mode else "#5fb85f",
            activeforeground="white",
            padx=25,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.open_output_btn = tk.Button(
            button_frame,
            text="📁 Open Output Folder",
            command=self.open_output_folder,
            font=("Segoe UI", 10),
            bg=self.button_bg,
            fg=self.text_color,
            activebackground=self.button_hover,
            padx=20,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            bd=1,
            highlightthickness=1,
            highlightbackground="#cccccc" if not self.dark_mode else "#444444"
        )
        self.open_output_btn.pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = tk.Frame(main_container, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=10)

        progress_label_top = tk.Label(
            progress_frame,
            text="📊 Progress:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        progress_label_top.pack(anchor=tk.W)

        # Style for progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#cccccc' if not self.dark_mode else '#444444',
            background=self.accent_color,
            bordercolor='#cccccc' if not self.dark_mode else '#444444',
            lightcolor=self.accent_color,
            darkcolor=self.accent_color
        )

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_label = tk.Label(
            progress_frame,
            text="Ready to start",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.progress_label.pack(anchor=tk.W, pady=(2, 0))

        # Log Frame
        log_frame = tk.Frame(main_container, bg=self.bg_color)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        log_label = tk.Label(
            log_frame,
            text="📋 Activity Log:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        log_label.pack(anchor=tk.W)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground="#cccccc" if not self.dark_mode else "#444444",
            bg=self.log_bg,
            fg=self.log_text_color,
            insertbackground=self.accent_color
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def log(self, message):
        """Thread-safe logging to GUI"""
        self.message_queue.put(('log', message))

    def update_progress(self, value):
        """Thread-safe progress update"""
        self.message_queue.put(('progress', value))

    def update_status(self, status):
        """Thread-safe status update"""
        self.message_queue.put(('status', status))

    def process_queue(self):
        """Process messages from background threads"""
        try:
            while True:
                msg_type, msg_data = self.message_queue.get_nowait()

                if msg_type == 'log':
                    try:
                        self.log_text.config(state=tk.NORMAL)
                        self.log_text.insert(tk.END, f"{msg_data}\n")
                        self.log_text.see(tk.END)
                        self.root.update_idletasks()
                    except tk.TclError:
                        pass

                elif msg_type == 'progress':
                    try:
                        self.progress_bar['value'] = msg_data
                        self.root.update_idletasks()
                    except tk.TclError:
                        pass

                elif msg_type == 'status':
                    try:
                        self.progress_label.config(text=msg_data)
                        self.root.update_idletasks()
                    except tk.TclError:
                        pass

                elif msg_type == 'complete':
                    self.on_processing_complete(msg_data)

                elif msg_type == 'error':
                    self.on_processing_error(msg_data)

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self.process_queue)

    def start_processing(self):
        """Start the download and music removal process"""
        if self.is_processing:
            messagebox.showwarning("Processing", "A video is already being processed!")
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return

        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED, text="⏳ Processing...")
        self.progress_bar['value'] = 0
        
        # Clear previous logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        self.log("="*60)
        self.log(f"Starting process for URL: {url}")
        self.log("="*60)

        # Get custom format if specified
        custom_format = self.format_entry.get().strip()
        if custom_format == Config.YTDLP_FORMAT:
            custom_format = None

        # Start processing in background thread
        thread = threading.Thread(
            target=self.process_video,
            args=(url, custom_format),
            daemon=True
        )
        thread.start()

    def process_video(self, url, custom_format):
        """Process video: download and remove music (runs in background thread)"""
        try:
            # Phase 1: Download video
            self.log("\n[PHASE 1] DOWNLOADING VIDEO")
            self.log("-" * 60)

            downloader = VideoDownloader(
                progress_callback=lambda p: self.update_progress(p * 0.5),
                status_callback=lambda s: self.update_status(s)
            )

            video_path = downloader.download(url, custom_format)
            self.current_video_path = video_path

            self.log(f"Downloaded: {video_path}")

            # Rename to safe ASCII filename
            video_path = Path(video_path)
            safe_name = f"video_{int(time.time())}_{random.randint(1000,9999)}{video_path.suffix}"
            safe_path = video_path.parent / safe_name
            
            video_path.rename(safe_path)
            video_path = safe_path
            
            self.log(f"Renamed to safe filename: {video_path.name}")

            # Phase 2: Remove music
            self.log("\n[PHASE 2] REMOVING MUSIC")
            self.log("-" * 60)

            remover = MusicRemover(
                progress_callback=lambda p: self.update_progress(50 + p * 0.5),
                status_callback=lambda s: self.update_status(s)
            )

            output_path = remover.remove_music(video_path)

            self.log(f"Output saved: {output_path}")
            self.log("\n" + "="*60)
            self.log("✅ PROCESS COMPLETED SUCCESSFULLY!")
            self.log("="*60)

            # Send completion message
            self.message_queue.put(('complete', output_path))

        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}"
            full_trace = traceback.format_exc()
            
            self.log(f"\n{'='*60}")
            self.log(f"❌ ERROR: {error_msg}")
            self.log(f"\nFull traceback:")
            self.log(full_trace)
            self.log("="*60)
            self.message_queue.put(('error', error_msg))

    def on_processing_complete(self, output_path):
        """Handle successful completion"""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL, text="▶ Download & Remove Music")
        self.progress_bar['value'] = 100
        self.update_status("✅ Completed successfully!")

        response = messagebox.askyesno(
            "Success!",
            f"Video processed successfully!\n\nOutput: {Path(output_path).name}\n\nDo you want to open the output folder?",
            icon='info'
        )

        if response:
            self.open_output_folder()

    def on_processing_error(self, error_msg):
        """Handle processing error"""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL, text="▶ Download & Remove Music")
        self.update_status("❌ Error occurred")

        messagebox.showerror("Error", f"Processing failed:\n\n{error_msg}")

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_dir = Config.OUTPUT_DIR

        if not output_dir.exists():
            messagebox.showinfo("Info", "Output folder is empty")
            return

        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':
            subprocess.run(['open', output_dir])
        else:
            subprocess.run(['xdg-open', output_dir])

    def open_donate_link(self):
        """Open donate link"""
        # Replace this URL with your actual donation link
        donation_url = "https://www.patreon.com/cw/rakeenalmuslim"
        
        try:
            webbrowser.open(donation_url)
        except:
            messagebox.showinfo(
                "Support",
                f"You can support the developer at:\n\n{donation_url}"
            )

def main():
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
