import tkinter as tk
from tkinter.messagebox import showinfo
from ttkbootstrap import ttk
from tkinter import filedialog as fd

from pytube import YouTube
from moviepy.editor import *

import os
import shutil
from pyperclip import paste
from threading import Thread
from proglog import ProgressBarLogger


# IMPORTANT
# https://stackoverflow.com/questions/69423410/moviepy-getting-progress-bar-values

BANNED_CHARACTERS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

class MoviePyProgressBar(ProgressBarLogger):
    def __init__(self, pb, pb_label, init_state=None, bars=None, ignored_bars=None, logged_bars='all', min_time_interval=0, ignore_bars_under=0):
        super().__init__(init_state, bars, ignored_bars, logged_bars, min_time_interval, ignore_bars_under)
        self.pb = pb
        self.pb_label = pb_label

    def callback(self, **changes):
        # Every time the logger message is updated, this function is called with
        # the `changes` dictionary of the form `parameter: new value`.
        for (parameter, value) in changes.items():
            print ('Parameter %s is now %s' % (parameter, value))
    
    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time the logger progress is updated, this function is called        
        percentage = (value / self.bars[bar]['total']) * 100
        # print(bar,attr,percentage)
        self.pb['value'] = percentage
        self.pb_label['text'] = str(round(percentage, 2)) + '%'


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("My App")
        self.geometry("850x425")
        self.iconbitmap("star.ico")
        self.resizable(False, False)
        
        # LAYOUT
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure(0, weight=1)

        # FRAMES
        self.main_frame = Main_Frame(self)
        self.side_frame = Side_Frame(self)
        self.main_frame.grid_propagate(False)
        self.side_frame.grid_propagate(False)

        # WIDGETS
        self.url_entry = Url_Entry(self.main_frame)
        self.paste_button = Paste_Button(self.main_frame, command=self.paste_button_func)
        self.get_video_button = Get_Video_Button(self.main_frame, command=lambda: self.get_video_thread(self.url_entry.get()))

        self.mainloop()

    # THREADS
    def get_video_thread(self, url):
        thread = Thread(target=lambda: self.get_video_button_func(url))
        thread.start()

    def download_video_thread(self, url, resolution):
        thread = Thread(target=lambda: self.download_video_button_func(url, resolution))
        thread.start()

    # BUTTON FUNCTIONS
    def paste_button_func(self):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, paste())
    
    def get_video_button_func(self, url):
        yt = YouTube(url)
        title = Video_Name_Label(self.main_frame, yt.title)

        streams_list = [stream.resolution for stream in yt.streams.order_by('resolution').desc()]
        streams_list = [*set(streams_list)]
        values = []
        for i in streams_list:
            i = i[0:-1]
            values.append(int(i))
        
        values.sort(reverse=True)
        values = [str(i) + 'p' for i in values]


        streams = Resolution_ComboBox(self.main_frame, values)
        core_count_label = Core_Count_Label(self.main_frame)
        core_count_entry = Core_Count_Entry(self.main_frame)
        download_video_btn = Download_Video_Button(self.main_frame, command=lambda: self.download_video_thread(url, streams.get()))
    
    def download_video_button_func(self, url, resolution):
        progress_bar = ProgressBar(self.side_frame, mode='determinate')

        progress_label = ttk.Label(self.side_frame, text=str(progress_bar['value']))
        progress_label.grid(pady=5)

        moviepy_progress_bar = MoviePyProgressBar(progress_bar, progress_label)

        def pytube_progress_bar(stream, chunk , bytes_remaining):
            percentage = 100 - (bytes_remaining / stream.filesize * 100)
            progress_bar['value'] = percentage
            progress_label['text'] = str(round(percentage, 2)) + '%'

        yt = YouTube(url, on_progress_callback=pytube_progress_bar)
        dir = fd.askdirectory()
        temp = os.path.join(os.getcwd(), 'media_Downlaoder_temp')

        raw_streams = yt.streams.filter(resolution=resolution).desc()
        if len(raw_streams) == 1:
            stream = raw_streams.first()
            if stream.default_filename.endswith(".webm"):
                stream.download(output_path=dir, filename=stream.title.replace(BANNED_CHARACTERS, '')+'.webm')
            elif stream.default_filename.endswith(".mp4"):
                if stream.is_progressive:
                    stream.download(output_path=dir, filename=stream.title.replace(BANNED_CHARACTERS, '')+'.mp4')
                else:

                    video_stream = yt.streams.filter(file_extension='mp4', adaptive=True, resolution=resolution).first()
                    video = video_stream.download(filename=f"video_of_{video_stream.title.replace(BANNED_CHARACTERS, '')}.mp4", output_path=temp)
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    audio = audio_stream.download(filename=f"audio_of_{audio_stream.title.replace(BANNED_CHARACTERS, '')}.mp4", output_path=temp)

                    video = VideoFileClip(video)
                    audio = AudioFileClip(audio)

                    final_video = video.set_audio(audio)
                    final_video.write_videofile(os.path.join(dir, f"{video_stream.title.replace(BANNED_CHARACTERS, '')}.mp4"))

                    shutil.rmtree(temp, ignore_errors=True)
                    progress_bar.destroy()
                    progress_label.destroy()
                    showinfo(title='Information', message=yt.title + ' has been downloaded successfully!')
        
        if len(raw_streams) > 1:
            stream = raw_streams.order_by('fps').desc().first()
            if stream.default_filename.endswith(".webm"):
                stream.download(output_path=dir, filename=stream.title.replace(BANNED_CHARACTERS, '')+'.webm')
            elif stream.default_filename.endswith(".mp4"):
                if stream.is_progressive:
                    stream.download(output_path=dir, filename=stream.title.replace(BANNED_CHARACTERS, '')+'.mp4')
                else:

                    video_stream = yt.streams.filter(file_extension='mp4', adaptive=True, resolution=resolution).first()
                    video = video_stream.download(filename=f"video_of_{video_stream.title.replace(BANNED_CHARACTERS, '')}.mp4", output_path=temp)
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    audio = audio_stream.download(filename=f"audio_of_{audio_stream.title.replace(BANNED_CHARACTERS, '')}.mp4", output_path=temp)

                    video = VideoFileClip(video)
                    audio = AudioFileClip(audio)

                    final_video = video.set_audio(audio)
                    final_video.write_videofile(os.path.join(dir, f"{video_stream.title.replace(BANNED_CHARACTERS, '')}.mp4"))

                    shutil.rmtree(temp, ignore_errors=True)
                    progress_bar.destroy()
                    progress_label.destroy()
                    showinfo(title='Information', message=yt.title + ' has been downloaded successfully!')


# FRAMES
class Main_Frame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        self.grid(row=0, column=0, columnspan=2, sticky="nsew")

class Side_Frame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, bootstyle="secondary")
        self.master = master
        self.configure()
        self.grid(row=0, column=2, columnspan=1, sticky="nsew")


# WIDGETS
class Url_Entry(ttk.Entry):
    def __init__(self, master):
        super().__init__(master, width=75)
        self.master = master
        self.grid(row=0, column=0, columnspan=5)

class Paste_Button(ttk.Button):
    def __init__(self, master, command):
        super().__init__(master, text="Paste", command=command)
        self.master = master
        self.grid(row=0, column=5, columnspan=3)

class Get_Video_Button(ttk.Button):
    def __init__(self, master, command):
        super().__init__(master, text="Get Video", command=command, width=15)
        self.master = master
        self.grid(row=1, column=0, columnspan=8, sticky="w", padx=15)

class Video_Name_Label(ttk.Label):
    def __init__(self, master, text):
        super().__init__(master, text=text)
        self.master = master
        self.grid(row=2, column=0, columnspan=8, sticky="w", padx=15)

class Resolution_ComboBox(ttk.Combobox):
    def __init__(self, master, values):
        super().__init__(master, values=values, state="readonly")
        self.master = master
        self.current(0)
        self.grid(row=3, column=0, columnspan=2, sticky="w", padx=15)

class Core_Count_Label(ttk.Label):
    def __init__(self, master):
        super().__init__(master, text="Core Count:\n(improves download speed \non progressive videos)", anchor="center")
        self.master = master
        self.grid(row=3, column=2, columnspan=3, sticky="e", padx=15)

class Core_Count_Entry(ttk.Entry):
    def __init__(self, master):
        super().__init__(master, width=10)
        self.master = master
        self.insert(0, "1")
        self.grid(row=3, column=5, columnspan=3, sticky="w", padx=15)

class Download_Video_Button(ttk.Button):
    def __init__(self, master, command):
        super().__init__(master, text="Download", command=command, width=15)
        self.master = master
        self.grid(row=4, column=0, columnspan=8, sticky="w", padx=15)

class ProgressBar(ttk.Progressbar):
    def __init__(self, master, mode):
        super().__init__(master, mode=mode, length=260)
        self.master = master
        self.grid(padx=15, pady=5)

if __name__ == "__main__":
    app = App()
