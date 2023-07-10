#!/usr/bin/env python3

import speech_recognition as sr
import RPi.GPIO as gpio
from sys import stderr
import threading

R_FORWARDS = 32
L_FORWARDS = 31
R_BACKWARDS = 33
L_BACKWARDS = 29


def configure_movement(rf: bool = False, lf: bool = False, rb: bool = False, lb: bool = False) -> None:
	gpio.output(R_FORWARDS, rf)
	gpio.output(L_FORWARDS, lf)
	gpio.output(R_BACKWARDS, rb)
	gpio.output(L_BACKWARDS, lb)

def initialize() -> None:
	gpio.setwarnings(False)
	gpio.setmode(gpio.BOARD)

	gpio.setup(L_FORWARDS, gpio.OUT)
	gpio.setup(L_BACKWARDS, gpio.OUT)
	gpio.setup(R_FORWARDS, gpio.OUT)
	gpio.setup(R_BACKWARDS, gpio.OUT)

	configure_movement()

def move_forwards() -> None:
	configure_movement(rf=True, lf=True)

def move_backwards() -> None:
	configure_movement(rb=True, lb=True)

def turn_left() -> None:
	configure_movement(rf=True, lb=True)

def turn_right() -> None:
	configure_movement(rb=True, lf=True)



def speech_control(speech_text: str) -> None:
	commands_dict = {
		"forward": move_forwards,
		"backward": move_backwards,
		"left": turn_left,
		"right": turn_right,
		"stop": configure_movement
	}

	for cmd, func in commands_dict.items():
		if cmd in speech_text:
			func()

def get_recognizer_source() -> (sr.Recognizer, sr.Microphone):
	recognizer = sr.Recognizer()

	mic_source = sr.Microphone()
	with mic_source as source:
		recognizer.adjust_for_ambient_noise(source, duration=0.2)

	return recognizer, mic_source

def catch_speech(recognizer: sr.Recognizer, mic_source: sr.Microphone) -> None:
	try:
		with mic_source as source:
			audio = recognizer.listen(source)

			speech_text = recognizer.recognize_google(audio)
			cmd_thread = threading.Thread(target=speech_control, args=(speech_text,))
			cmd_thread.start()

	except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError) as err:
		print(err, file=stderr)



def main() -> None:
	initialize()
	recognizer, mic_source = get_recognizer_source()

	while True:
		catch_speech(recognizer, mic_source)


if __name__ == "__main__":
	main()