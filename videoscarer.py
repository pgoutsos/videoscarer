import RPi.GPIO as GPIO
import time
import os
import sys
import signal
import pygame
import subprocess

# Setup video lists
normVideos_girlls = ["/home/pi/Videos/ghosts/girl_ls/meander1.mp4", \
                     "/home/pi/Videos/ghosts/girl_ls/phase1.mp4"]
scareVideos_girlls = ["/home/pi/Videos/ghosts/girl_ls/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/girl_ls/phasejumpscare1.mp4"]
normVideos_girlvert = ["/home/pi/Videos/ghosts/girl_vert/meander1.mp4", \
                     "/home/pi/Videos/ghosts/girl_vert/phase1.mp4"]
scareVideos_girlvert = ["/home/pi/Videos/ghosts/girl_vert/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/girl_vert/phasejumpscare1.mp4"]

normVideos_man1ls = ["/home/pi/Videos/ghosts/man_ls/meander1.mp4", \
                     "/home/pi/Videos/ghosts/man_ls/phase1.mp4"]
scareVideos_man1ls = ["/home/pi/Videos/ghosts/man_ls/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/man_ls/phasejumpscare1.mp4"]
normVideos_man1vert = ["/home/pi/Videos/ghosts/man_vert/meander1.mp4", \
                     "/home/pi/Videos/ghosts/man_vert/phase1.mp4"]
scareVideos_man1vert = ["/home/pi/Videos/ghosts/man_vert/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/man_vert/phasejumpscare1.mp4"]

normVideos_womanls = ["/home/pi/Videos/ghosts/woman_ls/meander1.mp4", \
                     "/home/pi/Videos/ghosts/woman_ls/phase1.mp4"]
scareVideos_womanls = ["/home/pi/Videos/ghosts/woman_ls/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/woman_ls/phasejumpscare1.mp4"]
normVideos_womanvert = ["/home/pi/Videos/ghosts/woman_vert/meander1.mp4", \
                     "/home/pi/Videos/ghosts/woman_vert/phase1.mp4"]
scareVideos_womanvert = ["/home/pi/Videos/ghosts/woman_vert/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/woman_vert/phasejumpscare1.mp4"]

normVideos_man2ls = ["/home/pi/Videos/ghosts/man2_ls/meander1.mp4", \
                     "/home/pi/Videos/ghosts/man2_ls/phase1.mp4"]
scareVideos_man2ls = ["/home/pi/Videos/ghosts/man2_ls/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/man2_ls/phasejumpscare1.mp4"]
normVideos_man2vert = ["/home/pi/Videos/ghosts/man2_vert/meander1.mp4", \
                     "/home/pi/Videos/ghosts/man2_vert/phase1.mp4"]
scareVideos_man2vert = ["/home/pi/Videos/ghosts/man2_vert/jumpscare1.mp4", \
                      "/home/pi/Videos/ghosts/man2_vert/phasejumpscare1.mp4"]

normVideos_allls = normVideos_girlls + normVideos_man1ls \
                   + normVideos_womanls + normVideos_man2ls
scareVideos_allls = scareVideos_girlls + scareVideos_man1ls \
                    + scareVideos_womanls + scareVideos_man2ls
normVideos_allvert = normVideos_girlvert + normVideos_man1vert \
                   + normVideos_womanvert + normVideos_man2vert
scareVideos_allvert = scareVideos_girlvert + scareVideos_man1vert \
                   + scareVideos_womanvert + scareVideos_man2vert

normVideos = normVideos_allls
scareVideos = scareVideos_allls

class VideoScarer:
    def __init__(self,normVideos,scareVideos,volumeLevel,scareInterval,pirPin,ffButtonPin):
        GPIO.setmode(GPIO.BCM)
        self.pirSensor = PIRSensor(pirPin, scareInterval)
        self.ffButton = Button(ffButtonPin)

        self.isInitialized = True
        self.videoID = 0
        self.omxProcess = None
        if len(normVideos) != len(scareVideos):
            raise ValueError("normVideos and scareVideos must be same length")
        else:
            self.normVideos = normVideos
            self.scareVideos = scareVideos
                        
            # setup blank screen using pygame
            # From Adafruit's video looper
            self.bgcolor = [0,0,0]  # blank screen color (rgb)
            pygame.display.init()
            pygame.font.init()
            pygame.mouse.set_visible(False)
            size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            self.blank_screen()
            self.playerCommand = ['omxplayer','-b']
            self.playerCommand.extend(['--vol', str(volumeLevel)])
            self.playerCommand.extend(['-o', 'hdmi']) # change to 'local' if your Pi has 3.5mm out, and you'd rather use that for audio
    
    def blank_screen(self):
        # from Adafruit's video looper
        self.screen.fill(self.bgcolor)
        pygame.display.update()
                
    def kill_all(self):
        if self.is_playing():
            self.omxProcess.kill()
        os.system('killall omxplayer.bin')
        return

    def is_playing(self):
        if hasattr(self.omxProcess, 'poll'):
            if self.omxProcess.poll() is None:
                return True
        return False

    def play_normal(self):
        self.kill_all()
        self.omxProcess = subprocess.Popen(self.playerCommand + [self.normVideos[self.videoID]], stdout=open(os.devnull, 'wb'), close_fds=True)
        return    
        
    def play_scare(self):
        self.kill_all()
        self.omxProcess = subprocess.Popen(self.playerCommand + [self.scareVideos[self.videoID]], stdout=open(os.devnull, 'wb'), close_fds=True)
        self.omxProcess.wait()
        return

    def play_next(self):
        self.videoID += 1
        if self.videoID > (len(self.normVideos) - 1):
            self.videoID = 0
        self.play_normal()
        return

    def play_prev(self):
        self.videoID -= 1
        if self.videoID < 0:
            self.videoID = len(self.normVideos) - 1
        self.play_normal()
        return
        
    def close(self,signal=None,frame=None):
        if self.isInitialized:
            self.isInitialized = False
            self.kill_all()
            GPIO.cleanup()
            pygame.quit()
            sys.exit(0)
            
    def run(self):
        # NOTE: all the PIR timer resets avoid a brownout issue that happens
        # when the video player starts. The PIR sensor will detect a false
        # positive due to the power fluctuation, and the time reset just 
        # repurposes the triggerInterval to wait a few seconds. Alternatively,
        # don't source the power from the Pi. 
        self.play_normal()
        self.pirSensor.reset_trigger_time()
        while self.isInitialized:
            # Quit on ctrl-c or esc using PyGame's event handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()
                    elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.close()
                        
            # play through list of normal videos
            if not self.is_playing():
                self.play_next()
                self.pirSensor.reset_trigger_time()

            # FF if requested
            if self.ffButton.is_pressed():
                self.play_next()
                self.pirSensor.reset_trigger_time()
            time.sleep(0.1)
                        
            # Check the PIR sensor and scare if appropriate
            if self.pirSensor.is_triggered():
                self.play_scare()
                self.pirSensor.reset_trigger_time()

class Button:
    def __init__(self, buttonPin):
        self.videoScarer = videoScarer
        # Setup the button as a GPIO input and initialize its status
        self.buttonPin = buttonPin
        GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.buttonState = True
        self.lastButtonState = True
        
    def is_pressed(self):
        # check if button is pressed, but not held down
        self.buttonState = GPIO.input(self.buttonPin)
        if (self.buttonState != self.lastButtonState) and not self.buttonState: # keeps held down button from re-triggering
            return True
        self.lastButtonState = self.buttonState
        return False
                
class PIRSensor:
    def __init__(self, pirPin, triggerInterval):
        self.lastTriggerTime = time.time()
        # Setup the button as a GPIO input and initialize its status
        self.pirPin = pirPin
        GPIO.setup(self.pirPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.triggerInterval = triggerInterval

    def is_triggered(self):
        # is PIR is triggered and enough time has passed since last trigger
        if (time.time() - self.lastTriggerTime) > self.triggerInterval:
            pirVal = GPIO.input(self.pirPin)
            if pirVal == 0:
                return False

            elif pirVal == 1:
                self.lastTriggerTime = time.time()
                return True
            
    def reset_trigger_time(self):
        self.lastTriggerTime = time.time()
                                
if __name__ == '__main__':
    # Some constants
    volumeLevel = 10   # omxplayer volume level
    scareInterval = 10 # seconds between consecutive scares
    
    # Pin definitions
    pirPin = 17
    ffButtonPin = 22
        
    videoScarer = None
    try:
        videoScarer = VideoScarer(normVideos, scareVideos, volumeLevel, scareInterval,pirPin,ffButtonPin)
        # handle ctrl-c... only works if pygame is inactive
        signal.signal(signal.SIGINT, videoScarer.close)
        signal.signal(signal.SIGTERM, videoScarer.close)
        videoScarer.run()

    finally:
        if videoScarer is not None:
            videoScarer.close()
