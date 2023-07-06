import tkinter as tk
import ttkbootstrap as ttk
import tkinter.filedialog as fd
from tkinter.messagebox import showinfo


from pytube import YouTube
from moviepy.editor import *
from pyperclip import paste
from proglog import ProgressBarLogger

from threading import Thread
import os
import shutil

# IMPORTANT
# https://stackoverflow.com/questions/69423410/moviepy-getting-progress-bar-values

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

        self.title('Media Downloader')
        self.geometry('600x450')

        self.label = ttk.Label(self, text='Download Youtube videos')
        self.label.pack()

        self.url_variable = tk.StringVar()
        self.url_entry = ttk.Entry(self, textvariable=self.url_variable, width=80)
        self.url_entry.pack(padx=5)

        self.paste_btn = ttk.Button(self, text='Paste', command=self.paste_string)
        self.paste_btn.pack(padx=5, pady=5)

        self.get_video_btn = ttk.Button(self, text='Get the video', command=lambda: self.get_video_thread(self.url_variable.get()))
        self.get_video_btn.pack(padx=5, pady=5)


    def get_video_thread(self, url):
        get_video_thread = Thread(target=lambda: self.get_video(url))
        get_video_thread.start()

    def download_video_thread(self, url):
        download_video_thread = Thread(target=lambda: self.download_video(url))
        download_video_thread.start()


    def paste_string(self):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, paste())


    def get_video(self, url):
        yt = YouTube(url)
        self.title = ttk.Label(self, text=yt.title)
        self.title.pack()

        values = [stream.resolution for stream in yt.streams.filter(file_extension='mp4', adaptive=True).order_by('resolution').desc()]

        self.streams = ttk.ComboBox(self, values=values, state='readonly')
        self.streams.current(0)
        self.streams.pack(padx=5, pady=5)

        self.download_video_btn = ttk.Button(self, text='Download', command=lambda: self.download_video_thread(url))
        self.download_video_btn.pack(padx=5, pady=5)


    def download_video(self, url):
        
        progress_bar = ttk.ProgressBar(self, 
                                            mode='determinate',
                                            orient='horizontal',
                                            length=280,)
        progress_bar.pack()
        progress_label = ttk.Label(self, text=str(progress_bar['value']))
        progress_label.pack()

        moviepy_progress_bar = MoviePyProgressBar(progress_bar, progress_label)

        def pytube_progress_bar(stream, chunk , bytes_remaining):
            percentage = 100 - (bytes_remaining / stream.filesize * 100)
            progress_bar['value'] = percentage
            progress_label['text'] = str(round(percentage, 2)) + '%'

        yt = YouTube(url, on_progress_callback=pytube_progress_bar)
        dir = fd.askdirectory()

        temp = os.path.join(os.getcwd(), 'media_Downlaoder_temp')

        video_stream = yt.streams.filter(resolution=self.streams.get(), adaptive=True, file_extension="mp4").first()
        video = video_stream.download(filename=f"video_of_{video_stream.title}.mp4", output_path=temp)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio = audio_stream.download(filename=f"audio_of_{audio_stream.title}.mp3", output_path=temp)

        video = VideoFileClip(video)
        audio = AudioFileClip(audio)

        final_video = video.set_audio(audio)
        final_video.write_videofile(os.path.join(dir, yt.title + ".mp4"), logger=moviepy_progress_bar, threads=4, fps=24)

        shutil.rmtree(temp, ignore_errors=True)
        progress_bar.destroy()
        progress_label.destroy()

        showinfo(title='Information', message=yt.title + ' has been downloaded successfully!')

if __name__ == "__main__":
    app = App()
    app.mainloop()