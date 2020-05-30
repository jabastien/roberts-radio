import vlc
from time import sleep

player = vlc.MediaPlayer("/home/pi/media/guitar.mp3")
player.play()
sleep(2)
player.pause()
sleep(2)
player.play()
sleep(10)

