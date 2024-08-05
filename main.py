# ***** IMPORTS *****
import time
import customtkinter
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



motivation_thought_time = 50 
focus_session_1_time = 27     # 45 min
rest_time = 3                 # 5 min
focus_session_2_time = 27     # 45 min

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


# seconds_total indicates number of seconds timer should count
seconds_total = 0

# this variable is used to iterate over sections
i = 0

# default volume value 
volume = 0.5

# indicates if timer is running or not
timer_running = False

# initiating sound mixer and default noise Sound object
pygame.mixer.init()
noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[NOISE_LIST[0]])

# Channel objects used to control noise   
channel1 = pygame.mixer.Channel(1)

#  and end section sound separately
channel2 = pygame.mixer.Channel(2)

# ***** FUNCTIONS *****


# change_noise is opening sound file choosen in option_noise.
def change_noise(choice):                        
    global noise_sound 

    if pygame.mixer.get_busy():
        stop_playback()
        noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[choice])
        noise_sound.set_volume(volume)
        start_playback()
    else:
        noise_sound = pygame.mixer.Sound(file=NOISE_PATH_DICT[choice])
        noise_sound.set_volume(volume)


# Sets noise volume according to volume_slider.            
def volume_control(volume_sl):      
    global volume
    volume = volume_sl                 
    noise_sound.set_volume(volume_sl)

# Starts playing choosen noise sound.
def start_playback():
    print("start_playback;")
    channel1.play(noise_sound, loops=-1) 

# Stops playing choosen noise sound. 
def stop_playback():
    print("stop_playback;")
    channel1.stop()

# Plays given end section sound                              
def end_section_sound(path):
    end_section_sound = pygame.mixer.Sound(file=path)
    channel2.play(end_section_sound)

# starts updating timer status
# used after pause, continues counting
def start():                           
    global timer_running
    if not timer_running:
        update_timer()
        timer_running = True

# pauses timer
def pause():
    global timer_running
    if timer_running:
        label_timer.after_cancel(update_time) 
        timer_running = False

# This function changes displayed text of the labels (label_timer, label)
#    - updates timer display in label_timer
#    - updates text in label_header with section name/comment
#    - plays end section sound
#    - stops noise sound in Rest section
# All based on data from TIMER_SECTION_DATA_LIST.  
def update_timer():                 
    global seconds_total, i
    
    # When changing sections, loading another title and timer  
    if seconds_total <= 0 and i < len(TIMER_SECTIONS_DATA_LIST):
        end_section_sound(TIMER_SECTIONS_DATA_LIST[i][2])
        seconds_total = TIMER_SECTIONS_DATA_LIST[i][1]
        section_name = TIMER_SECTIONS_DATA_LIST[i][0]

        # Stop sound while rest section and play again while 2nd focus session.
        if pygame.mixer.get_busy():
            if section_name == TIMER_SECTIONS_DATA_LIST[2][0]: # Rest                
                channel1.pause()
            elif section_name == TIMER_SECTIONS_DATA_LIST[3][0]: # 2nd focus session
                channel1.unpause()

        label_header.configure(text=section_name)
        i += 1

    # End of session
    if seconds_total <= 0:
        channel1.stop()
        end_section_sound(FINISH_SOUND_PATH)
        reward_message = random.choice(END_MESSAGES_LIST)
        label_timer.configure(text=reward_message, font=('Arial', 35))
        # leave only ending text in the frame
        label_header.pack_forget()
        play_button.pack_forget()
        stop_button.pack_forget()
        volume_slider.pack_forget()
        volume_control_label.pack_forget()
        option_noise.pack_forget()
        button_start.pack_forget()
        button_pause.pack_forget()

    # Updating timer 
    else:
        mins, secs = divmod(seconds_total, 60)
        hs, mins = divmod(mins, 60)
        timeformat = '{:02d}:{:02d}:{:02d}'.format(hs, mins, secs)
        label_timer.configure(text=timeformat)
        seconds_total -= 1

        # this global variable will be used in pause and start timer
        global update_time
        update_time = label_timer.after(1000, update_timer)

         
# ***** WIDGETS *****
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()

root.geometry("700x500")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)
# Title label:
label_header = customtkinter.CTkLabel(master=frame, text="Press START")
label_header.pack(pady=12, padx=10)

# Label that displays timer:

label_timer = customtkinter.CTkLabel(master=frame, font=('Arial', 20), text="00:00:00")
label_timer.pack(pady=12, padx=10)

# Start and Pause buttons:

button_start = customtkinter.CTkButton(master=frame, text="START", command=start)
button_start.pack(pady=5, padx=10)

button_pause = customtkinter.CTkButton(master=frame, text="PAUSE", command=pause)
button_pause.pack(pady=5, padx=10)

# You can choose sound in background to your work from option menu:
#     - binaural beats
#     - white noise
#     - pink noise
#     - brown noise    
checked_noise = customtkinter.StringVar(value=NOISE_LIST[0])
option_noise = customtkinter.CTkOptionMenu(frame, values=NOISE_LIST, variable=checked_noise, command=change_noise)
option_noise.pack(pady=20, padx=15)
option_noise.set("Choose background noise")


# Audio control slider:
volume_control_label = customtkinter.CTkLabel(master=frame, text="Volume", font=("Arial", 12))
volume_control_label.pack(pady=5)

volume_var = customtkinter.DoubleVar()
volume_slider = customtkinter.CTkSlider(master=frame, command=volume_control, from_=0, to=1, variable=volume_var)
volume_slider.pack(pady=5)
volume_slider.set(0.5)

# Play and Stop button
# Buttons that plays or stops choosen sound from a list.

stop_button = customtkinter.CTkButton(
    master=frame,
    text="Stop",
    command=stop_playback
)
stop_button.pack(pady=5, anchor='s')

play_button = customtkinter.CTkButton(
    master=frame, 
    text="Play",
    command=start_playback
)
play_button.pack(pady=5, anchor='s')

# ***** MAINLOOP *****
root.mainloop()