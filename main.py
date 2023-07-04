import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.filedialog as fd
from tkinter.messagebox import showinfo

from pytube import YouTube


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Media Downloader')
        self.geometry('500x300')

        self.label = ttk.Label(self, text='Download Youtube videos')
        self.label.pack()

        self.url_variable = tk.StringVar()
        self.url_entry = ttk.Entry(self, textvariable=self.url_variable, width=60)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=434pz9XIf_U")
        self.url_entry.pack(padx=10, pady=10)

        self.get_video = ttk.Button(self, text='Get the video', command=self.get_video, bootstyle=(INFO, OUTLINE))
        self.get_video.pack(padx=10, pady=10)


    def get_video(self):
        yt = YouTube(self.url_variable.get())
        self.title = ttk.Label(self, text=yt.title)
        self.title.pack(padx=10, pady=10)

        # add a combo box wich contains all the available streams
        values = [stream.resolution for stream in yt.streams.filter(file_extension="mp4")]
        for value in values:
            if value == 'None' or value == None or value == "144p":
                values.remove(value)
            
        values = values[::-1]

        self.streams = ttk.Combobox(self, values=values, state='readonly')
        self.streams.pack()

        self.download_video = ttk.Button(self, text='Download', command=self.download_video)
        self.download_video.pack()

    def download_video(self):
        yt = YouTube(self.url_variable.get())
        dir = fd.askdirectory()
        yt.streams.filter(resolution=self.streams.get()).first().download(dir)

        showinfo(title='Information', message=yt.title + ' has been downloaded successfully!')

if __name__ == "__main__":
    app = App()
    app.mainloop()