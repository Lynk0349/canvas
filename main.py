import os
import cv2
import numpy as np
import tkinter as tk

from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from ui import UITemplate

class ImageEditor(UITemplate):
    def __init__(self):
        super().__init__()
        # initialize the APP
        self.root.geometry('640x480')
        self.root.title("Mask Drawer")

        # initialize variables
        self.is_drawing = False
        self.last_x, self.last_y = None, None
        self.image_dir = None
        self.image_name = None
        self.undo_stack = []
        self.redo_stack = []

        # mouse events
        self.canvas.bind("<Enter>", self.set_custom_cursor)
        self.canvas.bind("<Leave>", self.reset_cursor)
        self.canvas.bind("<Motion>", self.update_custom_cursor)
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def undo_image(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.display_image()

    def redo_image(self):
         if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.display_image()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        self.undo_stack.clear()
        self.redo_stack.clear()
        if file_path:
            self.original_image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            self.image_dir = os.path.dirname(file_path)
            self.image_name = os.path.splitext(os.path.basename(file_path))[0]

            if self.original_image.shape[2] == 3:
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGBA)
            elif self.original_image.shape[2] == 4:
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGRA2RGBA)

            self.image = self.original_image.copy()
            self.display_image()

    def update_transparency(self):
        if self.image is not None:
            alpha_channel = np.full(self.image.shape[:2], self.alpha_value, dtype=np.uint8)
            self.image[:, :, 3] = alpha_channel

    def display_image(self):
        if self.image is not None:
            # the image format of Tkinter is RGB
            self.tk_image = ImageTk.PhotoImage(image=Image.fromarray(self.image))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def save_image(self):
        if self.image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG files", "*.png")])
            # file_path = os.path.join(self.image_dir, self.image_name + "_mask.png")
            if file_path:
                # diff_image = cv2.absdiff(self.original_image, self.image)
                # difference = np.zeros_like(diff_image[:, :, 0])
                # difference[(diff_image[:, :, 0] != 0) | (diff_image[:, :, 1] != 0) | (diff_image[:, :, 2] != 0)] = 255

                # save mask only
                self.image_cv = cv2.cvtColor(self.image, cv2.COLOR_RGBA2BGR)
                # cv2.imwrite(file_path, difference)
                cv2.imwrite(file_path, self.image_cv)
                print(f"Save a mask: {file_path}")

    def start_drawing(self, event):
        if self.image is not None:
            self.undo_stack.append(self.image.copy())
            self.redo_stack.clear()

        self.is_drawing = True
        self.last_x, self.last_y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))  # Store the start position

    def paint(self, event):
        if self.image is not None and self.is_drawing:
            x = int(self.canvas.canvasx(event.x))
            y = int(self.canvas.canvasy(event.y))
            radius = self.pen_size // 2

            cv2.circle(self.image, (x, y), radius, (0, 0, 0, self.alpha_value), -1)
            if self.last_x is not None and self.last_y is not None:
                cv2.line(self.image, (self.last_x, self.last_y), (x, y), (0, 0, 0, self.alpha_value), self.pen_size)

            self.display_image()
            self.last_x, self.last_y = x, y

    def stop_drawing(self, event):
        self.is_drawing = False
        self.last_x, self.last_y = None, None

    def change_pen_size(self, size):
        self.pen_size = int(size)
        self.update_cursor_image()

    def change_alpha(self, value):
        self.alpha_value = int(value)
        self.update_transparency()
        self.display_image()

    def update_cursor_image(self):
        cursor_img = np.zeros((self.pen_size, self.pen_size, 4), dtype=np.uint8)
        center = (self.pen_size // 2, self.pen_size // 2)
        radius = self.pen_size // 2
        cv2.circle(cursor_img, center, radius, (0, 0, 0, 255), -1)
        self.cursor_image = ImageTk.PhotoImage(image=Image.fromarray(cursor_img))

    def set_custom_cursor(self, event):
        if self.cursor_image:
            self.canvas.config(cursor="none")
            self.canvas.create_image(event.x, event.y, image=self.cursor_image, anchor=tk.CENTER, tag="cursor")

    def reset_cursor(self, event):
        self.canvas.config(cursor="")
        self.canvas.delete("cursor")

    def update_custom_cursor(self, event):
        if self.cursor_image:
            x_offset, y_offset = self.get_scroll_offset()
            self.canvas.delete("cursor")
            self.canvas.create_image(event.x+x_offset, event.y+y_offset, image=self.cursor_image, anchor=tk.CENTER, tag="cursor")

    def get_scroll_offset(self):
        x_start, x_end = self.canvas.xview()
        y_start, y_end = self.canvas.yview()
        x_offset = x_start * self.canvas.bbox(tk.ALL)[2]
        y_offset = y_start * self.canvas.bbox(tk.ALL)[3]
        return int(x_offset), int(y_offset)

if __name__ == "__main__":
    editor = ImageEditor()
    editor.run()