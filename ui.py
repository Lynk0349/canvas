import tkinter as tk

from abc import abstractmethod


class UITemplate(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('640x480')
        self.root.title("Image Editor")

        # initialize variables
        self.image = None
        self.original_image = None
        self.pen_size = 5 
        self.alpha_value = 255
        self.cursor_image = None
        self.update_cursor_image()

        # separate frames
        self.frame_btn = tk.LabelFrame(self.root, text="Control button")
        self.frame_btn.pack(side=tk.TOP, fill=tk.X)
        self.frame_scrollbar = tk.LabelFrame(self.root, text="Control scrollbar")
        self.frame_scrollbar.pack(side=tk.TOP, fill=tk.X)
        self.frame = tk.LabelFrame(self.root, text="Image")
        self.frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # buttons
        btn_load = tk.Button(self.frame_btn, text="Load Image", command=self.load_image)
        btn_load.grid(row=0, column=0, padx=5, pady=5)
        btn_save = tk.Button(self.frame_btn, text="Save Mask", command=self.save_image)
        btn_save.grid(row=0, column=1, padx=5, pady=5)
        btn_undo = tk.Button(self.frame_btn, text="Undo", command=self.undo_image)
        btn_undo.grid(row=0, column=2, padx=5, pady=5)
        btn_redo = tk.Button(self.frame_btn, text="Redo", command=self.redo_image)
        btn_redo.grid(row=0, column=3, padx=5, pady=5)


        # create a scrollbar for pen size
        self.label_pen_size = tk.Label(self.frame_scrollbar, text="Pen Size: ")
        self.label_pen_size.pack(side=tk.LEFT, fill=tk.Y)
        self.size_scroll = tk.Scale(self.frame_scrollbar, from_=1, to=50, orient=tk.HORIZONTAL, command=self.change_pen_size)
        self.size_scroll.set(self.pen_size)
        self.size_scroll.pack(side=tk.LEFT, fill=tk.X)
        # # create a scrollbar for alpha channel
        self.label_alpha_value = tk.Label(self.frame_scrollbar, text="Alpha value: ")
        self.label_alpha_value.pack(side=tk.LEFT, fill=tk.Y)
        self.alpha_scroll = tk.Scale(self.frame_scrollbar, from_=0, to=255, orient=tk.HORIZONTAL, command=self.change_alpha)
        self.alpha_scroll.set(self.alpha_value)
        self.alpha_scroll.pack(side=tk.LEFT, fill=tk.X)

        # canvas
        self.canvas = tk.Canvas(self.frame, bg="#a8a8a8")
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.v_scroll = tk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(self.canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

    def run(self):
        self.root.mainloop()
    
    @abstractmethod
    def update_cursor_image(self):
        pass

    @abstractmethod
    def load_image(self):
        pass

    @abstractmethod
    def save_image(self):
        pass
    
    @abstractmethod
    def undo_image(self):
        pass

    @abstractmethod
    def redo_image(self):
        pass

    @abstractmethod
    def change_pen_size(self):
        pass

    @abstractmethod
    def change_alpha(self):
        pass