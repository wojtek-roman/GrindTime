# ***** IMPORTS *****
import time
import customtkinter as ctk
import pygame
import random

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

motivation_thought_time = 1#50 
focus_session_1_time = 1#45 * 60     # 45 min
rest_time = 1#5* 60                  # 5 min
focus_session_2_time = 1#45 * 60     # 45 min

FINISH_SOUND_PATH = ".\\audio\\jingle3_finish.mp3"
START_SOUND_PATH = ".\\audio\\jingle2_start.mp3"
REST_SOUND_PATH = ".\\audio\\jingle1.mp3"

# list of tuples contain changing data for every section. It's passed to update_timer:
#    - timer label text
#    - time in seconds  
#    - path to end section sound file

TIMER_SECTIONS_DATA_LIST = [
    ("Take a minute to think about your motivation", motivation_thought_time, REST_SOUND_PATH),
    ("1st focus session", focus_session_1_time, START_SOUND_PATH),
    ("REST", rest_time, REST_SOUND_PATH),
    ("2nd focus session", focus_session_2_time, START_SOUND_PATH) 
]

root = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
         

class MainApp:
    # initiating sound mixer
    pygame.mixer.init()

    def __init__(self, root): 
    # ***** INSTANCE VARIABLES *****
        
        self.root = root
        self.root.title("Grind Timer")
        self.root.geometry("700x500")
        # Channel objects used to control noise   
        self.channel1 = pygame.mixer.Channel(1)
        # and end section sound separately
        self.channel2 = pygame.mixer.Channel(2)
        self.noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[NOISE_LIST[0]])
        # default volume value 
        self.volume = 0.5
        # indicates if timer is running or not
        self.timer_running = False
        # seconds_total indicates number of seconds timer should count
        self.seconds_total = 0
        # this variable is used to iterate over sections
        self.i = 0
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
            self.update_timer()
            self.timer_running = True

    def pause(self):
        if self.timer_running:
            self.label_timer.after_cancel(self.update_time) 
            self.timer_running = False
  
    def update_timer(self):                 
        self.seconds_total, self.i
        
        # When changing sections, loading another title and timer  
        if self.seconds_total <= 0 and self.i < len(TIMER_SECTIONS_DATA_LIST):
            self.end_section_sound(TIMER_SECTIONS_DATA_LIST[self.i][2])
            self.seconds_total = TIMER_SECTIONS_DATA_LIST[self.i][1]
            self.section_name = TIMER_SECTIONS_DATA_LIST[self.i][0]

            # Stop sound while rest section and play again while 2nd focus session.
            if pygame.mixer.get_busy():
                if self.section_name == TIMER_SECTIONS_DATA_LIST[2][0]: # Rest                
                    self.channel1.pause()
                elif self.section_name == TIMER_SECTIONS_DATA_LIST[3][0]: # 2nd focus session
                    self.channel1.unpause()

            self.label_header.configure(text=self.section_name)
            self.i += 1

        if self.seconds_total <= 0:
            self.channel1.stop()
            self.end_section_sound(FINISH_SOUND_PATH)##################################END
            EndApp(root)

            # leave only ending text in the self.frame
            # self.label_header.pack_forget()
            # self.play_button.pack_forget()
            # self.stop_button.pack_forget()
            # self.volume_slider.pack_forget()
            # self.volume_control_label.pack_forget()
            # self.option_noise.pack_forget()
            # self.button_start.pack_forget()
            # self.button_pause.pack_forget()
        else: # Updating timer
            mins, secs = divmod(self.seconds_total, 60)
            hs, mins = divmod(mins, 60)
            timeformat = '{:02d}:{:02d}:{:02d}'.format(hs, mins, secs)
            self.label_timer.configure(text=timeformat)
            self.seconds_total -= 1

            # variable will be used in pause and start timer            
            self.update_time = self.label_timer.after(1000, self.update_timer)

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
        print("restart function")
        for widget in self.root.winfo_children():
            widget.destroy()
        MainApp(self.root) 

# ***** MAINLOOP *****

if __name__ == "__main__":
    app = MainApp(root)
    root.mainloop()