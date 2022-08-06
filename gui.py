import tkinter as tk
import tkinter.font as font
import tkinter.messagebox as mb


class Widget(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CopyTranslator")
        self.root.geometry("1000x670")
        ft = font.Font(size=20)
        self.copied = tk.Text(self.root, width=70, height=12, font=ft)
        self.copied.pack()

        self.translated = tk.Text(self.root, width=70, height=12, font=ft)
        self.translated.pack()

    def open(self):
        self.root.mainloop()

    def setCopied(self, target: str):
        if target is None:
            return
        self.copied.delete(0.0, tk.END)
        self.copied.insert(tk.INSERT, target)

    def setTranslated(self, target: str):
        if target is None:
            return
        self.translated.delete(0.0, tk.END)
        self.translated.insert(tk.INSERT, target)

    @staticmethod
    def info(title: str, content: str):
        mb.showinfo(title, content)

    @staticmethod
    def warning(title: str, content: str):
        mb.showwarning(title, content)

    @staticmethod
    def error(title: str, content: str):
        mb.showerror(title, content)
