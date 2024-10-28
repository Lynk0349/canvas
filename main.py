import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor with OpenCV")

        # Initialize variables
        self.image = None
        self.original_image = None
        self.paint_size = 5  # Default paint size
        self.alpha_value = 255  # Default alpha channel value (fully opaque)
        self.is_drawing = False  # To track if drawing is in progress
        self.last_x, self.last_y = None, None  # Track the last mouse position

        # Create a frame to hold the canvas and scrollbars
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create main canvas for the image
        self.canvas = tk.Canvas(self.frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create vertical scrollbar for canvas
        self.v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar for canvas
        self.h_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(fill=tk.X)

        # Configure canvas to use scrollbars
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Add buttons
        btn_load = tk.Button(root, text="Load Image", command=self.load_image)
        btn_load.pack(side=tk.LEFT)

        btn_save = tk.Button(root, text="Save Mask", command=self.save_image)
        btn_save.pack(side=tk.LEFT)

        # Create a scrollbar for paint size
        self.size_scroll = tk.Scale(root, from_=1, to=50, orient=tk.VERTICAL, label="Paint Size", command=self.change_paint_size)
        self.size_scroll.set(self.paint_size)  # Set default paint size
        self.size_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # # Create a scrollbar for alpha channel
        # self.alpha_scroll = tk.Scale(root, from_=0, to=255, orient=tk.VERTICAL, label="Alpha Channel", command=self.change_alpha)
        # self.alpha_scroll.set(self.alpha_value)  # Set default alpha value
        # self.alpha_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # Load the image using OpenCV
            self.original_image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if self.original_image.shape[2] == 3:  # If it's a BGR image, convert to RGBA
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGBA)
            elif self.original_image.shape[2] == 4:  # If it's already RGBA
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGRA2RGBA)

            self.image = self.original_image.copy()  # Copy for drawing
            # self.update_transparency()  # Update transparency based on alpha value
            self.display_image()

    # def update_transparency(self):
    #     if self.image is not None:
    #         alpha_channel = np.full(self.image.shape[:2], self.alpha_value, dtype=np.uint8)
    #         self.image[:, :, 3] = alpha_channel  # Update the alpha channel

    def display_image(self):
        if self.image is not None:
            # Convert RGBA (OpenCV format) to RGB (Tkinter format)
            # rgb_image = cv2.cvtColor(self.image, cv2.COLOR_RGBA2RGB)
            self.tk_image = ImageTk.PhotoImage(image=Image.fromarray(self.image))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))  # Set scroll region to the size of the image

    def save_image(self):
        if self.image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG files", "*.png")])
            if file_path:
                # Calculate the difference between the original and modified image
                diff_image = cv2.absdiff(self.original_image, self.image)

                # Create a binary difference image
                difference = np.zeros_like(diff_image[:, :, 0])  # Initialize a single channel for differences
                difference[(diff_image[:, :, 0] != 0) | (diff_image[:, :, 1] != 0) | (diff_image[:, :, 2] != 0)] = 255  # Set different pixels to 255

                # self.image = cv2.cvtColor(self.image, cv2.COLOR_RGBA2BGR)
                cv2.imwrite(file_path, difference)

    def start_drawing(self, event):
        self.is_drawing = True  # Set drawing flag to True
        self.last_x, self.last_y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))  # Store the start position

    def paint(self, event):
        if self.image is not None and self.is_drawing:
            # Get the current position
            x = int(self.canvas.canvasx(event.x))
            y = int(self.canvas.canvasy(event.y))
            radius = self.paint_size // 2  # Calculate radius for the circle

            # Draw a circle on the image
            cv2.circle(self.image, (x, y), radius, (0, 0, 0, self.alpha_value), -1)  # Fill with black color and set alpha

            # Draw a line between the last position and the current position
            if self.last_x is not None and self.last_y is not None:
                cv2.line(self.image, (self.last_x, self.last_y), (x, y), (0, 0, 0, self.alpha_value), self.paint_size)

            # Refresh the image on the canvas
            self.display_image()
            self.last_x, self.last_y = x, y  # Update last position

    def stop_drawing(self, event):
        self.is_drawing = False  # Set drawing flag to False
        self.last_x, self.last_y = None, None  # Reset last position

    def change_paint_size(self, size):
        self.paint_size = int(size)

    # def change_alpha(self, value):
    #     self.alpha_value = int(value)
    #     self.update_transparency()  # Update transparency in the image
    #     self.display_image()  # Refresh image with new alpha value

if __name__ == "__main__":
    root = tk.Tk()
    editor = ImageEditor(root)
    root.mainloop()
