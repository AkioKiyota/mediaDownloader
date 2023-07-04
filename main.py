import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
from tkinter.messagebox import showinfo

from pytube import YouTube

class App(tk.Tk):
  def __init__(self):
    super().__init__()

    self.title('My Awesome App')
    self.geometry('500x300')

    self.label = ttk.Label(self, text='Hello, Tkinter!')
    self.label.pack()

    self.url_variable = tk.StringVar()
    self.url_entry = ttk.Entry(self, textvariable=self.url_variable, width=40)
    self.url_entry.pack()

    self.button = ttk.Button(self, text='Click Me')
    self.button['command'] = self.download_video
    self.button.pack()

  def download_video(self):
    yt = YouTube(self.url_variable.get())
    dir = fd.askdirectory()
    yt.streams.first().download(dir)

    showinfo(title='Information', message=yt.title + ' has been downloaded successfully!')

if __name__ == "__main__":
  app = App()
  app.mainloop()