from gpiozero import Button
from time import sleep
from signal import pause
import vlc

# Define buttons
button1_up = Button(4)
button1_down = Button(17)

button2_up = Button(27)
button2_down = Button(22)

button3_up = Button(5)
button3_down = Button(6)

button4_up = Button(13)
button4_down = Button(19)

# Play something gentle to start with, just in case it goes wrong, at least it's short!
player = vlc.MediaPlayer("/home/pi/roberts-radio/media/guitar.mp3")
player_is_playing = True
vlc.libvlc_audio_set_volume(player, 30)

exit(0)

def play_radio_2():
    global player_is_playing
    global player

    if player_is_playing:
        player.stop()
        player_is_playing = False

    print("Playing BBC Radio 2")
    player = vlc.MediaPlayer("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p")
    vlc.libvlc_audio_set_volume(player, 30)
    player_is_playing = True
    player.play()

def stop_radio_2():
    global player_is_playing
    global player

    if player_is_playing:
        print("Stopping BBC Radio 2")
        player.stop()
        player_is_playing = False

try:
    button1_down.when_pressed = play_radio_2
    button1_up.when_pressed = stop_radio_2

    print("Radio ready for button press")

    pause()

finally:
    try:
        if player_is_playing:
            player.stop()
            player_is_playing = False

    except:
        pass

