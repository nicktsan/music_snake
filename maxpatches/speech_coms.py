import speech_recognition as sr
import time

r = sr.Recognizer()
m = sr.Microphone()

def get_command():
	with m as source:
		print("Say something!")
		audio = r.listen(source, phrase_time_limit = 1.0)
	try:
		data = r.recognize_sphinx(audio)
		print("Sphinx thinks you said: " + data)
	except sr.UnknownValueError:
		print("Sphinx could not understand audio")
	except sr.RequestError as e:
		print("Sphinx error; {0}".format(e))	
	return data
if __name__ == "__main__" :
	get_command()

