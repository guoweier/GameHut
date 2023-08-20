from tkinter import *
from time import *
import threading
import random

GAME_WIDTH = 500
GAME_HEIGHT = 500
BACKGROUND_COLOR = "#000000"
TIME = 30

def hole_initial_config(hole):
    hole.config(state='disabled', text='【x】_【x】', bg='red', fg='black')

def onwhack():
    global hole
    if hole == 1:
        hole_initial_config(hole1)
    elif hole == 2:
        hole_initial_config(hole2)
    elif hole == 3:
        hole_initial_config(hole3)
    elif hole == 4:
        hole_initial_config(hole4)
    elif hole == 5:
        hole_initial_config(hole5)
    elif hole == 6:
        hole_initial_config(hole6)
    elif hole == 7:
        hole_initial_config(hole7)
    elif hole == 8:
        hole_initial_config(hole8)
    elif hole == 9:
        hole_initial_config(hole9)
    global whack
    whack += 1
    scorelabel.config(text="Score:{}".format(whack))

def hole_button():
    hole = Button(width=6, height=3, bg="black", state="disabled", command=onwhack)
    return hole

def hole_mouse_config(hole):
    hole.config(state='normal', text='【.】v【.】', bg='pink', fg='black')
    sleep(1)
    hole.config(state='disabled', text='', bg='black')

def whac_a_mole():
    ready_set_whack()
    global hole
    for i in range(0, TIME):
        hole = random.randint(1,9)
        if hole == 1:
            hole_mouse_config(hole1)
        elif hole == 2:
            hole_mouse_config(hole2)
        elif hole == 3:
            hole_mouse_config(hole3)
        elif hole == 4:
            hole_mouse_config(hole4)
        elif hole == 5:
            hole_mouse_config(hole5)
        elif hole == 6:
            hole_mouse_config(hole6)
        elif hole == 7:
            hole_mouse_config(hole7)
        elif hole == 8:
            hole_mouse_config(hole8)
        elif hole == 9:
            hole_mouse_config(hole9)
    global whack
    remark.config(text="You whack {} mice!".format(whack))


def ready_set_whack():
    sleep(1)
    scorelabel.config(text="Ready")
    sleep(1)
    scorelabel.config(text="Set")
    sleep(1)
    scorelabel.config(text="WHACK!!")
    sleep(1)
    scorelabel.config(text="0") 

window = Tk()
window.title("WHACK-A-MOLE")
window.resizable(False, False)

whack = 0
hole = 0

scorelabel = Label(window, text="Score:{}".format(whack), font=("consolas", 30), fg = "black")
scorelabel.pack()

remark = Label(text="")
remark.place(x=130, y=107)

canvas = Canvas(window, bg = BACKGROUND_COLOR, height = GAME_HEIGHT, width = GAME_WIDTH)
canvas.pack()

window.update()

window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width/2)-(window_width/2))
y = int((screen_height/2)-(window_height/2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

hole1 = hole_button()
hole1.place(x=20, y=150)
hole2 = hole_button()
hole2.place(x=20, y=290)
hole3 = hole_button()
hole3.place(x=20, y=420)
hole4 = hole_button()
hole4.place(x=210, y=150)
hole5 = hole_button()
hole5.place(x=210, y=290)
hole6 = hole_button()
hole6.place(x=210, y=420)
hole7 = hole_button()
hole7.place(x=400, y=150)
hole8 = hole_button()
hole8.place(x=400, y=290)
hole9 = hole_button()
hole9.place(x=400, y=420)

whac_a_mole()

window.mainloop()
