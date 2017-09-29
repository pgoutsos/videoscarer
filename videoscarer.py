import RPi.GPIO as GPIO
import time
import os
import sys
import pygame
from subprocess import Popen

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

# Initialize
scareInterval = 10
button1State = True
lastButton1State = True
GPIO.output(ledPin, GPIO.LOW)
vidPlayer = None

class VideoScarer:
    def __init__(self,normVideos,scareVideos,volumeLevel):
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
		self.playerCommand = ['omxplayer']
		self.playerCommand.extend(['--vol', str(volumeLevel)])
		self.playerCommand.extend(['-o', 'hdmi']) # change to 'local' if your Pi has 3.5mm out, and you'd rather use that for audio
    
	def _blank_screen(self):
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
		self.playerCommand.extend(['-b', self.normVideos[self.videoID])
        self.omxProcess = Popen(self.playerCommand, stdout=open(os.devnull, 'wb'), close_fds=True)
        return    
        
    def play_scare(self):
        self.kill_all()
		self.playerCommand.extend(['-b', self.scareVideos[self.videoID])
        self.omxProcess = Popen(self.playerCommand, stdout=open(os.devnull, 'wb'), close_fds=True)
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
		
	def close(self):
		self.kill_all()
		pygame.quit()

class FFButton:
    def __init__(self, buttonPin, videoScarer):
		self.videoScarer = videoScarer
		# Setup the button as a GPIO input and initialize its status
		self.buttonPin = buttonPin
		GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.buttonState = True
		self.lastButtonState = True
	
	def advance_if_needed(self):
		# force movie to advance if button is pressed
		self.buttonState = GPIO.input(self.buttonPin)
		if (self.buttonState != self.lastButtonState) and not self.buttonState: # keeps held down button from re-triggering
			self.videoScarer.play_next()
		self.lastButtonState = self.buttonState
		
class PIRSensor:
	def __init__(self, pirPin, videoScarer, scareInterval):
		self.lastScareTime = time.time()
		self.videoScarer = videoScarer
		# Setup the button as a GPIO input and initialize its status
		self.pirPin = pirPin
		GPIO.setup(self.pirPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		self.scareInterval = scareInterval

	def scare_if_needed(self):
		# SCARE if PIR is triggered and enough time has passed since last scare
		if (time.time() - self.lastScareTime) > self.scareInterval:
			pirVal = GPIO.input(pirPin)
			if pirVal == 0:
				#print("No scare", pirVal)
				#GPIO.output(ledPin, GPIO.LOW)
				time.sleep(0.1)

			elif pirVal == 1:
				#print("Spooky time!", pirVal)
				#GPIO.output(ledPin, GPIO.HIGH)
				self.vidPlayer.play_scare()
				self.lastScareTime = time.time()
				time.sleep(0.1)
				
if __name__ == '__main__':
	# Pin definitions
	pirPin = 17
	buttonPin = 22

	# Setup GPIO
	GPIO.setmode(GPIO.BCM)
	
	vidPlayer = None
	try:
		videoScarer = VideoScarer(normVideos, scareVideos)
		ffButton = FFButton(buttonPin, videoScarer)
		pirSensor = PIRSensor(pirPin, videoScarer, 10)
		videoScarer.play_normal()

		while True:
			# play through list of normal videos
			if not videoScarer.is_playing():
				videoScarer.play_next()

			# FF if requested
			ffButton.advance_if_needed()
			
			# Check the PIR sensor and scare if appropriate
			pirSensor.scare_if_needed()


	except:
		if vidPlayer is not None:
			vidPlayer.close()
		GPIO.cleanup()