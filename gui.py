import tkinter as tk
import tkinter.font as tkFont


class Widget(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CopyTranslator")
        self.root.geometry("1000x670")
        ft = tkFont.Font(size=20)
        self.copied = tk.Text(self.root, width=70, height=12, font=ft)
        self.copied.pack()

        self.translated = tk.Text(self.root, width=70, height=12, font=ft)
        self.translated.pack()

    def open(self):
        self.root.mainloop()

    def setCopied(self, target: str):
        self.copied.delete(0.0, tk.END)
        self.copied.insert(tk.INSERT, target)

    def setTranslated(self, target: str):
        self.translated.delete(0.0, tk.END)
        self.translated.insert(tk.INSERT, target)
