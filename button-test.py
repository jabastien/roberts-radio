from gpiozero import Button
from time import sleep
from signal import pause

button1_up = Button(4)
button1_down = Button(17)

button2_up = Button(27)
button2_down = Button(22)

button3_up = Button(5)
button3_down = Button(6)

button4_up = Button(13)
button4_down = Button(19)

def button_press(pin):
    print(pin)
    sleep(0.3)

button1_up.when_pressed =  button_press
button1_down.when_pressed = button_press
button2_up.when_pressed = button_press
button2_down.when_pressed = button_press
button3_up.when_pressed = button_press
button3_down.when_pressed = button_press
button4_up.when_pressed = button_press
button4_down.when_pressed = button_press

pause()
