import tkinter as tk
import pyautogui
import time
import threading
from io import BytesIO
import easyocr
from PIL import Image
import numpy as np
from translation import organise_transcript, organise_buffer, format_transcript_markdown
import queue

class ScreenCapture:
    def __init__(self):
        self.region = None
        self.running = False
        self.thread = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.root = None
        self.canvas = None
        self.reader = easyocr.Reader(['en'])  # Initialize OCR reader
        self.word_buffer = []
        self.max_words = 100
        self.processed_buffer_words = 300
        self.formatted_buffer = ' '

    def select_region(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Make the window transparent
        self.root.bind('<ButtonPress-1>', self.on_mouse_down)
        self.root.bind('<B1-Motion>', self.on_mouse_drag)
        self.root.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.mainloop()

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.canvas.delete("selection_rectangle")
        self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2, tags="selection_rectangle")

    def on_mouse_drag(self, event):
        self.canvas.coords("selection_rectangle", self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.root.destroy()
        self.region = (min(self.start_x, self.end_x), min(self.start_y, self.end_y), abs(self.start_x - self.end_x), abs(self.start_y - self.end_y))

    def capture_screen(self):
        while self.running:
            screenshot = pyautogui.screenshot(region=self.region)
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)
            self.process_image(buffer)
            time.sleep(2)

    def process_image(self, image_buffer: BytesIO):
        image = Image.open(image_buffer)
        image_np = np.array(image)
        result = self.reader.readtext(image_np)
        new_text = ' '.join([text for (bbox, text, prob) in result])
        new_words = new_text.split()
        self.word_buffer.extend(new_words)

        # Limit the buffer to the most recent 100 words
        if len(self.word_buffer) > self.max_words:
            self.word_buffer = self.word_buffer[-self.max_words:]

        buffer_text = ' '.join(self.word_buffer)
        translated_text = organise_transcript(buffer_text)
        
        # Update word buffer
        self.word_buffer = self.update_buffer(self.word_buffer, translated_text.split())
        buffer_string = ' '.join(self.word_buffer)
        self.formatted_buffer = format_transcript_markdown(buffer_string)
        print("Buffer formateado:", self.formatted_buffer)
        return self.formatted_buffer

    def update_buffer(self, current_words: list, new_words: list) -> list:
        new_buffer = organise_buffer(' '.join(current_words), ' '.join(new_words))
        new_buffer_words = new_buffer.split()

        if len(new_buffer_words) > self.max_words:
            new_buffer_words = new_buffer_words[-self.max_words:]
        
        return new_buffer_words

    def start_capture(self):
        if not self.region:
            self.select_region()
        self.running = True
        self.thread = threading.Thread(target=self.capture_screen)
        self.thread.start()
        print("Started screen capture...")

    def stop_capture(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("Stopped screen capture.")

if __name__ == "__main__":
    sc = ScreenCapture()
    sc.start_capture()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sc.stop_capture()
