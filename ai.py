from textblob import TextBlob
from openai import OpenAI
from termcolor import colored
import pyttsx3
import speech_recognition as sr
import subprocess
import platform
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    print("OpenAI API key not found")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)

def get_emotion(sentiment_score):
    if sentiment_score >= 0.5:
        return "Joy"
    elif sentiment_score <= -0.5:
        return "Sadness"
    elif sentiment_score > 0:
        return "Happiness"
    elif sentiment_score < 0:
        return "Disapproval"
    else:
        return "Neutral"

def speak_with_emotion(text, emotion):
    engine = pyttsx3.init()

    # Adjust voice parameters based on emotion
    if emotion == "Joy":
        engine.setProperty('rate', 150)
        engine.setProperty('pitch', 200)
    elif emotion == "Sadness":
        engine.setProperty('rate', 100)
        engine.setProperty('pitch', 50)
    else:
        engine.setProperty('rate', 160)
        engine.setProperty('pitch', 150)

    engine.say(text)
    engine.runAndWait()

def open_application(application_name):
    try:
        if platform.system() == "Windows":
            subprocess.run(["start", "", application_name], shell=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", "-a", application_name])
        elif platform.system() == "Linux":
            subprocess.run([application_name])
    except Exception as e:
        print(f"An error occurred while opening {application_name}: {e}")

while True:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(colored("Listening...", 'green'))
        audio = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio)
        print(colored("You (Voice):", 'red') + colored(user_input, 'cyan'))

        if user_input.lower() == "exit":
            break

        # Check if the user wants to open an application
        if "open" in user_input.lower() and any(app in user_input.lower() for app in ['chrome', 'firefox', 'notepad']):
            app_to_open = next((app for app in ['chrome', 'firefox', 'notepad'] if app in user_input.lower()), None)
            if app_to_open:
                open_application(app_to_open)
                continue

        # Analyze sentiment using TextBlob
        blob = TextBlob(user_input)
        sentiment_score = blob.sentiment.polarity
        emotion = get_emotion(sentiment_score)

        print(colored(f"Emotion Analysis: {emotion}", 'blue'))

        prompt = user_input
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Emotion: {emotion}. Please act like Jarvis and call me sir and you have a sense of humor with human expressions and feelings"},
                {"role": "user", "content": prompt}
            ]
        )

        response = completion.choices[0].message.content
        print(colored("AI:", 'yellow') + colored(response, 'cyan'))

        # Speak with adjusted emotion
        speak_with_emotion(response, emotion)

    except sr.UnknownValueError:
        print(colored("Sorry, couldn't understand the audio. Please try again.", 'red'))
    except sr.RequestError as e:
        print(colored(f"Could not request results from Google Speech Recognition service; {e}", 'red'))
