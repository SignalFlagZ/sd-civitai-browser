from colorama import Fore, Back, Style
try:
    import tkinter as tk
except ImportError:
    tk = None
    print(Fore.LIGHTYELLOW_EX + f'Civitai-Browser: tkinter not found. Limited functionality.' + Style.RESET_ALL)
else:
    from tkinter import messagebox

class guitk:
    def __init__(self):
        if tk is not None:
            self.mainWindow  = tk.Tk()
        else:
            self.mainWindow = None
               
    def msg(self, title, text):
        if tk is not None:
            self.mainWindow.attributes('-topmost', True)
            self.mainWindow.bell()
            self.mainWindow.withdraw()
            ret = messagebox.askyesno(title=title, message=text)
            self.mainWindow.quit()
            self.mainWindow.destroy()
            return ret
        else:
            return True
    def tk(self):
        return True if tk is not None else False