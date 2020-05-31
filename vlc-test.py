import vlc
from time import sleep

player = vlc.MediaPlayer("/home/pi/roberts-radio/media/guitar.mp3")
player.play()
sleep(10)

