import tkinter as tk
from tkinter import filedialog
import threading
import time


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.count = 0
        self.updatethread = threading.Thread(target=self.updater)
        self.updatethread.start()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.cbutton = tk.Button(self)
        self.cbutton['text'] = 'green'
        self.cbutton['activeforeground'] = 'green'

        self.cbutton.bind("<Enter>", self.turn_red)
        self.cbutton.bind("<Leave>", self.turn_green)
        self.cbutton.pack(side='left')

        self.s = tk.Scale(self, from_=0, to=10,
                          orient=tk.HORIZONTAL, length=200,
                          showvalue=0)
        self.s.pack()

        self.quit = tk.Button(self, text="QUIT", fg="red", bg='black',
                              command=self.onClose)
        self.quit.pack(side="bottom")

        self.stop_flag = threading.Event()

    def turn_red(self, event):
        event.widget["text"] = "red"
        event.widget["fg"] = "red"

    def turn_green(self, event):
        event.widget["text"] = "green"
        event.widget["fg"] = "green"

    def onClose(self):
        self.stop_flag.set()
        self.updatethread.join()
        root.destroy()

    def updater(self):
        count = 0
        while not self.stop_flag.is_set():
            self.s.set(count)
            count = (count+1) % 10
            time.sleep(1)

    def say_hi(self):
        print("hi there, everyone!")
        self.count += 1
        if self.count == 5:
            self.hi_there['text'] = 'Stop it now'
            self.hi_there["command"] = lambda: None


root = tk.Tk()
# path = filedialog.askopenfilename()
# print(path)
app = Application(master=root)
root.title("Test app")
# root.minsize(1000, 400)
app.mainloop()
