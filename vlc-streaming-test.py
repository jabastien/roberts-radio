import vlc
from time import sleep

player = vlc.MediaPlayer("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p")
vlc.libvlc_audio_set_volume(player, 60)
player.play()
sleep(10)
player.stop()
