# ***** IMPORTS *****

import customtkinter as ctk
import pygame
import random
from enum import Enum

# ***** VARIABLES *****

# randomly selected messages printed at the end of work
END_MESSAGES_LIST = [
    "Congratulations!\n You deserved a reward.\n🏆", 
    "Nice work!👍🏻\n Get some rest 🧘🏿\nand keep up good work!"
    ]

# background sounds names used in menu option_noise
NOISE_LIST = [
    "Binaural beats",
    "White noise",
    "Pink noise",
    "Brown noise"
    ]

# used to transform name of noise sound (key) to sound path (value) in change_noise
NOISE_PATH_DICT = {
    NOISE_LIST[0]: ".\\audio\\binaural-beats.mp3",
    NOISE_LIST[1]: ".\\audio\\white-noise.mp3",
    NOISE_LIST[2]: ".\\audio\\pink-noise.mp3",
    NOISE_LIST[3]: ".\\audio\\brown-noise.mp3"
}

motivation_thought_time = 50 
focus_session_1_time = 45 * 60     
rest_time = 5* 60                  
focus_session_2_time = 45 * 60     

FINISH_SOUND_PATH = ".\\audio\\jingle3_finish.mp3"
START_SOUND_PATH = ".\\audio\\jingle2_start.mp3"
REST_SOUND_PATH = ".\\audio\\jingle1.mp3"

SECTIONS_DATA_LIST = [
    ("Take a minute to think about your motivation", motivation_thought_time, REST_SOUND_PATH),
    ("1st focus session", focus_session_1_time, START_SOUND_PATH),
    ("REST", rest_time, REST_SOUND_PATH),
    ("2nd focus session", focus_session_2_time, START_SOUND_PATH) 
]

class SDLIndex(Enum):
    MESSAGE = 0
    TIME = 1
    SOUND_PATH = 2

    REFLECTION = 0
    SESSION_1 = 1
    REST = 2
    SESSION_2 = 3

root = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
         
class MainApp:
    pygame.mixer.init()

    def __init__(self, root): 
    # ***** INSTANCE VARIABLES *****
        
        self.root = root
        self.root.title("Grind Timer")
        self.root.geometry("700x500")
        self.channel1 = pygame.mixer.Channel(1)
        self.channel2 = pygame.mixer.Channel(2)
        self.noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[NOISE_LIST[0]])
        self.volume = 0.5
        self.timer_running = False
        self.updated_section_index = 0
        
        self.time_left = 0
        self.section_message = None

        self.update_time = lambda *args, **kwargs: None

    # ***** WIDGETS *****

        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)
        
        self.label_header = ctk.CTkLabel(master=self.frame, text="Press START")
        self.label_header.pack(pady=12, padx=10)

        self.label_timer = ctk.CTkLabel(master=self.frame, font=('Arial', 20), text="00:00:00")
        self.label_timer.pack(pady=12, padx=10)

        self.button_start = ctk.CTkButton(master=self.frame, text="START", command=self.start)
        self.button_start.pack(pady=5, padx=10)

        self.button_pause = ctk.CTkButton(master=self.frame, text="PAUSE", command=self.pause)
        self.button_pause.pack(pady=5, padx=10)
        
        self.checked_noise = ctk.StringVar(value=NOISE_LIST[0])
        self.option_noise = ctk.CTkOptionMenu(self.frame, values=NOISE_LIST, variable=self.checked_noise, command=self.change_noise)
        self.option_noise.pack(pady=20, padx=15)
        self.option_noise.set("Choose background noise")

        self.volume_control_label = ctk.CTkLabel(master=self.frame, text="Volume", font=("Arial", 12))
        self.volume_control_label.pack(pady=5)

        self.volume_var = ctk.DoubleVar()
        self.volume_slider = ctk.CTkSlider(master=self.frame, command=self.volume_control, from_=0, to=1, variable=self.volume_var)
        self.volume_slider.pack(pady=5)
        self.volume_slider.set(0.5)

        self.stop_button = ctk.CTkButton(
            master=self.frame,
            text="Stop",
            command=self.stop_playback
        )
        self.stop_button.pack(pady=5, anchor='s')

        self.play_button = ctk.CTkButton(
            master=self.frame, 
            text="Play",
            command=self.start_playback
        )
        self.play_button.pack(pady=5, anchor='s')

    # ***** FUNCTIONS ****

    def change_noise(self, choice):                         
        if pygame.mixer.get_busy():
            self.stop_playback()
            self.noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[choice])
            self.noise_sound.set_volume(self.volume)
            self.start_playback()
        else:
            self.noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[choice])
            self.noise_sound.set_volume(self.volume)

    def volume_control(self, volume_sl):      
        self.volume = volume_sl                 
        self.noise_sound.set_volume(volume_sl)

    def start_playback(self):
        self.channel1.play(self.noise_sound, loops=-1) 

    def stop_playback(self):
        self.channel1.stop()

    def end_section_sound(self, path):
        play_end_section_sound = pygame.mixer.Sound(file=path)
        self.channel2.play(play_end_section_sound)

    def start(self):                           
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

        
    def pause(self):
        if self.timer_running:
            self.label_timer.after_cancel(self.update_time) 
            self.timer_running = False
  
    def update_timer(self):           
        
        if self.time_left <= 0 and self.updated_section_index < len(SECTIONS_DATA_LIST):
            self.next_section()
        
        if self.time_left <= 0 and self.updated_section_index >= len(SECTIONS_DATA_LIST):
            self.end_mainapp()
        else:
            mins, secs = divmod(self.time_left, 60)
            hs, mins = divmod(mins, 60)
            timeformat = '{:02d}:{:02d}:{:02d}'.format(hs, mins, secs)
            self.label_timer.configure(text=timeformat)
            self.time_left -= 1
            self.update_time = self.label_timer.after(1000, self.update_timer)

    def next_section(self):
        self.end_section_sound(SECTIONS_DATA_LIST[self.updated_section_index][SDLIndex.SOUND_PATH.value])
        self.time_left = SECTIONS_DATA_LIST[self.updated_section_index][SDLIndex.TIME.value]
        self.section_message = SECTIONS_DATA_LIST[self.updated_section_index][SDLIndex.MESSAGE.value]
        
        if pygame.mixer.get_busy():
            if self.section_message == SECTIONS_DATA_LIST[SDLIndex.REST.value][SDLIndex.MESSAGE.value]:               
                self.channel1.pause()
            elif self.section_message == SECTIONS_DATA_LIST[SDLIndex.SESSION_2.value][SDLIndex.MESSAGE.value]: 
                self.channel1.unpause()
        
        self.label_header.configure(text=self.section_message)
        self.updated_section_index += 1

    def end_mainapp(self):
            self.channel1.stop()
            self.end_section_sound(FINISH_SOUND_PATH)
            EndApp(root)

class EndApp:
    
    def __init__(self, root):
        self.root = root
        self.build_end_screen()

    def build_end_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=60, padx=60, fill="both", expand=True)

        self.reward_message_str = random.choice(END_MESSAGES_LIST)

        self.reward_message_widget = ctk.CTkLabel(master=self.frame, text=self.reward_message_str, font=('Arial', 35))
        self.reward_message_widget.pack(pady=50, padx=10)

        self.button_restart = ctk.CTkButton(master=self.frame, text="RESTART", command=self.restart)
        self.button_restart.pack(side="bottom")

    def restart(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MainApp(self.root) 

# ***** MAINLOOP *****

if __name__ == "__main__":
    app = MainApp(root)
    root.mainloop()