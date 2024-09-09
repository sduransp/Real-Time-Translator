# C:\Users\DURANAS\Coding\real-time-translator\src\frontend\app.py
import tkinter
import tkinter.messagebox
import customtkinter
import threading
import os
import time
import sys
print(os.path.join(os.path.dirname(os.path.abspath(__file__)),"backend"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"backend"))
from user_translation import RealTimeTranslator
from screen_transcript import ScreenCapture

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.translator_thread = None
        self.translator_running = False

        self.screen_capture = ScreenCapture()

        # configure window
        self.title("Real-Time MS Teams translator")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="MS Teams translator", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Voice Translation", command=self.toggle_translation)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Transcript", command=self.sidebar_button_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, rowspan=3, padx=(20, 0), pady=(20, 20), sticky="nsew")

        # create radiobutton frame
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Voice Language:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")

        # Add radio buttons for the most spoken languages
        languages = ["English", "German", "French", "Italian", "Chinese", "Spanish", "Hindi", "Arabic", "Portuguese", "Bengali", "Russian", "Japanese"]
        self.language_map = {index: language for index, language in enumerate(languages)}
        for index, language in enumerate(languages):
            radio_button = customtkinter.CTkRadioButton(master=self.radiobutton_frame, text=language, variable=self.radio_var, value=index)
            if language not in ["English", "German"]:
                radio_button.configure(state="disabled")
            radio_button.grid(row=index+1, column=2, pady=10, padx=20, sticky="n")

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)

        self.update_textbox()

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        if self.screen_capture.running:
            self.screen_capture.stop_capture()
        else:
            self.start_screen_capture()
    
    def start_screen_capture(self):
        # Iniciar la captura de pantalla en un hilo separado
        capture_thread = threading.Thread(target=self.run_screen_capture)
        capture_thread.start()

    def run_screen_capture(self):
        # Iniciar la captura y luego imprimir formatted_buffer periódicamente
        self.screen_capture.start_capture()

    def update_textbox(self):
        # Verifica si formatted_buffer tiene contenido y lo inserta en el textbox
        print(f"El formatted text: {self.screen_capture.formatted_buffer}")
        if self.screen_capture.formatted_buffer.strip():
            print(f"formatted_buffer (hilo principal): {self.screen_capture.formatted_buffer}")
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", self.screen_capture.formatted_buffer)
        else:
            print("formatted_buffer está vacío.")
        
        # Continuar llamando a esta función cada 2 segundos para actualizar el textbox
        self.after(2000, self.update_textbox)

    def toggle_translation(self):
        if self.translator_running:
            self.translator_running = False
            self.translator_thread.join()
            self.sidebar_button_1.configure(text="Voice Translation", fg_color=None)
        else:
            selected_language_index = self.radio_var.get()
            output_language = self.language_map.get(selected_language_index, "German")
            self.translator_running = True
            self.translator_thread = threading.Thread(target=self.start_translation, args=(output_language,))
            self.translator_thread.start()
            self.sidebar_button_1.configure(text="Stop Translation", fg_color="green")

    def start_translation(self, output_language):
        translator = RealTimeTranslator(output_language=output_language)
        translator.run()


if __name__ == "__main__":
    app = App()
    app.mainloop()
