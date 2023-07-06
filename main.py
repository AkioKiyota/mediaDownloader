import tkinter as tk
import tkinter.filedialog as fd
from tkinter.messagebox import showinfo

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from pytube import YouTube
from pytube.cli import on_progress

from threading import Thread
from moviepy.editor import *
from pyperclip import paste
from proglog import ProgressBarLogger

# IMPORTANT
# https://stackoverflow.com/questions/69423410/moviepy-getting-progress-bar-values

class MyBarLogger(ProgressBarLogger):
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

        self.title('Media Downloader')
        self.geometry('600x450')

        self.label = ttk.Label(self, text='Download Youtube videos')
        self.label.pack()

        self.url_variable = tk.StringVar()
        self.url_entry = ttk.Entry(self, textvariable=self.url_variable, width=60)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=434pz9XIf_U")
        self.url_entry.pack(padx=10)

        self.paste_btn = ttk.Button(self, text='Paste', command=self.paste_string, bootstyle=(SECONDARY, OUTLINE))
        self.paste_btn.pack(padx=10, pady=10)

        self.get_video_btn = ttk.Button(self, text='Get the video', command=lambda: self.get_video_thread(self.url_variable.get()), bootstyle=(INFO, OUTLINE))
        self.get_video_btn.pack(padx=10, pady=10)


    def get_video_thread(self, url):
        get_video_thread = Thread(target=lambda: self.get_video(url))
        get_video_thread.start()

    def download_video_thread(self, url):
        download_video_thread = Thread(target=lambda: self.download_video(url))
        download_video_thread.start()


    def paste_string(self):
        self.url_entry.insert(0, paste())


    def get_video(self, url):
        yt = YouTube(url)
        self.title = ttk.Label(self, text=yt.title)
        self.title.pack(padx=10, pady=10)

        values = [stream.resolution for stream in yt.streams.filter(file_extension='mp4', adaptive=True).order_by('resolution').desc()]

        self.streams = ttk.Combobox(self, values=values, state='readonly')
        self.streams.current(0)
        self.streams.pack(padx=10, pady=10)

        self.download_video_btn = ttk.Button(self, text='Download', command=lambda: self.download_video_thread(url), bootstyle=(SUCCESS, OUTLINE))
        self.download_video_btn.pack(padx=10, pady=10)


    def download_video(self, url):
        
        progress_bar = ttk.Progressbar(self, 
                                            mode='determinate',
                                            orient='horizontal',
                                            length=280,)
        progress_bar.pack(padx=10, pady=10)
        progress_label = ttk.Label(self, text=str(progress_bar['value']))
        progress_label.pack(padx=10, pady=10)

        logger = MyBarLogger(progress_bar, progress_label)


        yt = YouTube(url)
        dir = fd.askdirectory()

        temp = os.path.join(os.getcwd(), 'media_Downlaoder_temp')

        video_stream = yt.streams.filter(resolution=self.streams.get(), adaptive=True, file_extension="mp4").first()
        video = video_stream.download(filename=f"video_of_{video_stream.title}.mp4", output_path=temp)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio = audio_stream.download(filename=f"audio_of_{audio_stream.title}.mp3", output_path=temp)

        video = VideoFileClip(video)
        audio = AudioFileClip(audio)

        final_video = video.set_audio(audio)
        final_video.write_videofile(os.path.join(dir, yt.title + ".mp4"), logger=logger)

        os.remove(temp) # PERMISSION ERROR

        showinfo(title='Information', message=yt.title + ' has been downloaded successfully!')

if __name__ == "__main__":
    app = App()
    app.mainloop()