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

player = vlc.MediaPlayer("")

def play_radio_2():
    player = vlc.MediaPlayer("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p")
    player.play()

def stop_radio_2(player):
    player.stop()

button1_down.when_pressed = play_radio_2()
button1_up.when_pressed = stop_radio_2()

pause()
