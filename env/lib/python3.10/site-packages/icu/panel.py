import tkinter as tk

#TODO remove - unused?
class Panel(tk.Frame):

    def __init__(self, parent, width=200, height=200):
        super(Panel, self).__init__(parent)
        self.canvas = tk.Canvas(self, width=width, height=height, 
                                bd=0, highlightthickness=0)
        self.canvas.pack()

    def draw_rect(self, *rect, border='black', fill='white'):
        assert len(rect) == 4 #x1,y1,x2,y2
        self.canvas.create_rectangle(*rect, fill=fill, outline=border)
