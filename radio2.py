from gpiozero import Button, MCP3008
import vlc
from time import sleep
from signal import pause
from math import ceil
import threading
from logzero import logger, logfile
import subprocess
import os

# Initialise the log file if wanted
#logfile("radio.log")

# Initial start-up log
logger.info("Starting up the radio")

# Set GPIO inputs
volume_pot = MCP3008(0)
tuning_pot = MCP3008(1)
button1_up = Button(4)
button1_down = Button(17)
button2_up = Button(27)
button2_down = Button(22)
button3_up = Button(5)
button3_down = Button(6)
button4_up = Button(13)
button4_down = Button(26)

# Thread variable to keep you in the loop
volume_thread_continue = True

# Specify speech synthesizer
speech_engine = "pico" # espeak or pico

# Function to get absolute value from potentiometer device
# The pots operate "backwards" - turn it all the way to the left = 1,
# all the way to the right = 0. So we need to reverse it as well as
# scale it up. Defined as a function as we have two pots
def get_abs_from_pot(pot):
    pot_value = pot.value
    scaled_up_value = pot_value * 100
    abs_value = int(ceil(100 - scaled_up_value))

    return abs_value

# Generic thread to control a player's volume according to a pot value
def volume_thread(pot, player):
    global volume_thread_continue

    logger.debug("Started volume thread")

    # Default volume setting
    volume_setting = 30
    vlc.libvlc_audio_set_volume(player, volume_setting)

    # Keep re-setting the volume according to pot value unless you haven't moved the dial
    while volume_thread_continue:
        last_volume_setting = volume_setting

        volume_setting = get_abs_from_pot(pot)

        if volume_setting != last_volume_setting:
            logger.debug("Setting volume to " + str(volume_setting))
            vlc.libvlc_audio_set_volume(player, volume_setting)

        # Shutdown control section
        # If volume is 0 and remains so for 5 seconds, shutdown with a countdown
        if volume_setting == 0:
            shutdown_setting = True
            shutdown_counter = 5

            while shutdown_setting:
                volume_setting = get_abs_from_pot(pot)

                # If volume changes, abort the shutdown sequence
                if volume_setting != 0:
                    shutdown_setting = False
                else:
                    say("Shut down in " + str(shutdown_counter) + " seconds")
                    shutdown_counter = shutdown_counter - 1
                    sleep(1)

                    # If you've reached zero, shutdown the radio
                    if shutdown_counter == 0:
                        shutdown()

        # Don't overload the Pi by infinite loop with no delay
        sleep(0.3)

    logger.info("Finishing volume thread")

# Plays a stream and resets the volume thread
def play_stream(stream_url):
    global player
    global volume_thr
    global volume_thread_continue

    logger.info("Playing stream: " + stream_url)

    # Use python-vlc to create a media player
    player = vlc.MediaPlayer(stream_url)
    vlc.libvlc_audio_set_volume(player, 30)
    player.play()

    # Shutdown previous volume thread
    logger.info("Telling volume thread to stop")
    volume_thread_continue = False
    logger.info("Joining volume_thr thread")
    volume_thr.join()
    logger.info("Volume thread has finished. Starting a new one")

    # Start new volume thread
    volume_thread_continue = True
    volume_thr = threading.Thread(target=volume_thread, args=(volume_pot, player), daemon=True)
    volume_thr.start()

# Just stops the current stream
def stop_stream():
    global player

    logger.info("Stopping current station")
    player.stop()

# Play individual stations (on button presses)
def play_radio_2():
    stop_stream()
    say("BBC Radio 2")
    logger.info("Playing BBC Radio 2")
    play_stream("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p")

def play_radio_4():
    stop_stream()
    say("BBC Radio 4")
    logger.info("Playing BBC Radio 4")
    play_stream("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p")

def play_radio_3cr():
    stop_stream()
    say("BBC Three Counties Radio")
    logger.info("Playing BBC Radio 3 Counties")
    play_stream("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_lr3cr_mf_p")

# Button 4 uses the tuner knob to select a station
def play_other():
    enabled = True

    # Helps us work out channel changes
    last_channel = 0

    # Always read the instructions!
    say("Use the tuner to select a station")

    while enabled:
        if button4_up.value == 1:
            # Stream SHOULD stop as a result of the button-up, so no need to stop it here
            enabled = False

        # Get adjusted pot value from the tuning knob
        tuner = get_abs_from_pot(tuning_pot)

        # Specify channel number ranges (must be a better way to do this!)
        if tuner >= 0 and tuner <= 10:
            channel = 1
        elif tuner > 10 and tuner <= 20:
            channel = 2
        elif tuner > 20 and tuner <= 30:
            channel = 3
        elif tuner > 30 and tuner <= 40:
            channel = 4
        elif tuner > 40 and tuner <= 50:
            channel = 5
        elif tuner > 50 and tuner <= 60:
            channel = 6
        elif tuner > 60 and tuner <= 70:
            channel = 7
        elif tuner > 70 and tuner <= 80:
            channel = 8
        elif tuner > 80 and tuner <= 90:
            channel = 9
        elif tuner > 90 and tuner <= 100:
            channel = 10

        # Only change channel if the new channel is different to the last channel
        if channel != last_channel:
            last_channel = channel
            stop_stream()

            # Channel to stream IF statements
            if channel == 1:
                # Film music
                say("Film music")
                play_stream("http://5.39.71.159:8173/stream")
            elif channel == 2:
                # Cinemix
                say("Cinemix")
                play_stream("http://streamingV2.shoutcast.com/SoundtrackRadiostation")
            elif channel == 3:
                # Soundtrack Radiostation
                say("Soundtrack Radio Station")
                play_stream("http://streamingV2.shoutcast.com/CINEMIX")
            elif channel == 4:
                # Parry Sound Eastern Shores Radio
                say("Parry Sound Eastern Shores Radio")
                play_stream("http://us5.internet-radio.com:8246/live")
            elif channel == 5:
                # Shine Digital Christian Radio
                say("Shine digital Christian radio")
                play_stream("http://uk5.internet-radio.com:8204/")
            elif channel == 6:
                 # We The Kingdom
                 say("We the kingdom")
                 play_stream("http://uk2.internet-radio.com:8201/")
            elif channel == 7:
                 say("The ranch classic country")
                 # The Ranch - Classic Country
                 play_stream("http://us3.internet-radio.com:8297/")
            elif channel == 8:
                # Magic Musicals
                say("Magic musicals")
                play_stream("https://stream-mz.planetradio.co.uk/magicmusicals.mp3")
            elif channel > 8:
                say("Station not defined")

        sleep(0.3)

# Run a string through espeak
def say_espeak(sentence):
    os.system('espeak -a 40 -s 100 "' + sentence + '"')

# Run a string through pico-tts
def say_pico(sentence):
    os.system('pico2wave --lang="en-GB" -w stdout.wav "' + sentence + '" | aplay')

# Wrapper so we can centrally change the speech synthesiser
def say(sentence):
    if speech_engine == "espeak":
        say_espeak(sentence)
    elif speech_engine == "pico":
        say_pico(sentence)

# Shutdown the Pi gracefully
def shutdown():
    logger.info("Shutting down")
    stop_stream()

    say("Shut down")

    player = vlc.MediaPlayer("/home/pi/roberts-radio/media/shutdown.mp3")
    # Nice and lound
    vlc.libvlc_audio_set_volume(player, 80)
    player.play()
    sleep(3)

    # Shutdown the Raspberry Pi and exit nicely
    subprocess.call(["sudo", "halt"])
    exit(0)


# Define button actions as auto-threads
button1_down.when_pressed = play_radio_2
button1_up.when_pressed = stop_stream

button2_down.when_pressed = play_radio_4
button2_up.when_pressed = stop_stream

button3_down.when_pressed = play_radio_3cr
button3_up.when_pressed = stop_stream

button4_down.when_pressed = play_other
button4_up.when_pressed = stop_stream

# Play an intro sound so we know it's booted up. We could get it to "say" it's IP address eventually!
logger.info("Playing intro")
player = vlc.MediaPlayer("/home/pi/roberts-radio/media/guitar.mp3")
vlc.libvlc_audio_set_volume(player, 30)
player.play()
sleep(3)
player.stop()

# Say a welcome message
say("Welcome to the Roberts Radio Project")

# Start volume control thread just to register the variabl so we can use it as a global below
volume_thr = threading.Thread(target=volume_thread, args=(volume_pot, player), daemon=True)
volume_thr.start()

# Don't let the program exit - it's all in threaded control now
pause()
