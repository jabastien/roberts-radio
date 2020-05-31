from gpiozero import Button, MCP3008
import vlc
from time import sleep
from signal import pause
from math import ceil
import threading
from logzero import logger, logfile
import subprocess

# Initialise the log file
logfile("radio.log")
logger.info("Starting up the radio")

# Set GPIO inputs
volume_pot = MCP3008(0)
button1_up = Button(4)
button1_down = Button(17)
button2_up = Button(27)
button2_down = Button(22)
button3_up = Button(5)
button3_down = Button(6)
#button4_up = Button(13)
# DO NOT USE Button(19) as that is I2C and should not have been soldered onto!
# Bugger it. I'll need to de-solder from pin 19.

volume_thread_continue = True

def volume_thread(pot, player):
    global volume_thread_continue

    logger.debug("Started volume thread")

    volume_setting = 30
    vlc.libvlc_audio_set_volume(player, volume_setting)

    while volume_thread_continue:
        last_volume_setting = volume_setting

        pot_value = pot.value
        scaled_up_value = pot_value * 100
        volume_setting = int(ceil(100 - scaled_up_value))

        if volume_setting != last_volume_setting:
            logger.debug("Setting volume to " + str(volume_setting))
            vlc.libvlc_audio_set_volume(player, volume_setting)

        sleep(0.3)

    logger.info("Finishing volume thread")

logger.info("Playing intro")
player = vlc.MediaPlayer("/home/pi/roberts-radio/media/guitar.mp3")
vlc.libvlc_audio_set_volume(player, 30)
player.play()
sleep(3)
player.stop()

volume_thr = threading.Thread(target=volume_thread, args=(volume_pot, player), daemon=True)
volume_thr.start()

def play_stream(stream_url):
    global player
    global volume_thr
    global volume_thread_continue

    player = vlc.MediaPlayer(stream_url)
    vlc.libvlc_audio_set_volume(player, 30)
    player.play()

    logger.info("Telling volume thread to stop")
    volume_thread_continue = False
    logger.info("Joining volume_thr thread")
    volume_thr.join()
    logger.info("Volume thread has finished. Starting a new one")

    volume_thread_continue = True
    volume_thr = threading.Thread(target=volume_thread, args=(volume_pot, player), daemon=True)
    volume_thr.start()

def stop_stream():
    global player

    logger.info("Stopping current station")
    player.stop()

def play_radio_2():
    stop_stream()
    logger.info("Playing BBC Radio 2")
    play_stream("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p")

def play_radio_4():
    stop_stream()
    logger.info("Playing BBC Radio 4")
    play_stream("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p")

def play_radio_3cr():
    stop_stream()
    logger.info("Playing BBC Radio 3 Counties")
    play_stream("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_lr3cr_mf_p")

# Define button auto-threads
button1_down.when_pressed = play_radio_2
button1_up.when_pressed = stop_stream

button2_down.when_pressed = play_radio_4
button2_up.when_pressed = stop_stream

button3_down.when_pressed = play_radio_3cr
button3_up.when_pressed = stop_stream

while True:
    logger.debug("Heartbeat")

    if (button1_down.value == 1) and (button2_down.value == 1) and (button3_down.value == 1):
        logger.info("Shutting down")
        stop_stream()

        player = vlc.MediaPlayer("/home/pi/roberts-radio/media/shutdown.mp3")
        vlc.libvlc_audio_set_volume(player, 80)
        player.play()
        sleep(3)
        subprocess.call(["sudo", "halt"])
        exit()

    sleep(2)

pause()
