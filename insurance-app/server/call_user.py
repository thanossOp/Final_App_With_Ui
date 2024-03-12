import pyttsx3
import speech_recognition as sr
import json
import datetime
import os
from sentence_transformers import SentenceTransformer, util
import time

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

try:
    json_file_path = os.path.join(os.path.dirname(__file__), "call.json")
    with open("call.json", "r") as file:
        dataset = json.load(file)
except FileNotFoundError:
    dataset = []

current_session_file_path = None

user_name = "nisarg"

def log_interaction(log_text):
    global current_session_file_path

    if current_session_file_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("call_recording")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        current_session_file_path = os.path.join(
            folder_path, f"interaction_log_{timestamp}.txt"
        )

    with open(current_session_file_path, "a") as log_file:
        log_file.write(f"{log_text}\n")


def restart_session():
    global current_session_file_path
    current_session_file_path = None


def speak(response):
    engine = pyttsx3.init()
    voice = engine.getProperty("voices")
    engine.setProperty("voice", voice[0].id)
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 0.9)
    engine.say(response)
    engine.runAndWait()
    log_interaction(f"AI said: {response}")


def get_speech_input(timeout=5, max_attempts=3):
    attempts = 0

    while attempts < max_attempts:
        print("Listening....")
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, phrase_time_limit=10, timeout=5)

        try:
            print("Recognizing...")
            user_input = r.recognize_google(audio)
            print("command", user_input)
            log_interaction(f"User said: {user_input}\n")
            return user_input.lower()
        except sr.UnknownValueError as e:
            attempts += 1
            if attempts < max_attempts:
                speak(f"I couldn't hear you. Are you there {user_name}?")
                time.sleep(timeout)  
            else:
                speak("I couldn't hear you. It seems we're having trouble with the connection. Goodbye!")
                break
    return None


def greet_user():
    curent_hour = datetime.datetime.now().hour

    if 5 < curent_hour < 12:
        speak(f"Hello {user_name} Good Morning ")
    elif 12 <= curent_hour < 18:
        speak(f"Hello {user_name} Good Afternoon")
    else:
        speak(f"Hello {user_name} Good Evening ")

    speak(
        f"my name is thanos, and I'm calling from Health Insurance system. How are you today?"
    )


def getresponse(user):

    user_question_embeding = model.encode(user, convert_to_tensor=True)
    similarities = []

    for data in dataset:
        dataset_question_embedding = model.encode(data["user"], convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(
            user_question_embeding, dataset_question_embedding
        )
        similarities.append(similarity_score)

    most_similar_index = similarities.index(max(similarities))

    if similarities[most_similar_index] < 0.3:
        return "I couldn't hear you properly. Can you please say that again?"
    else:
        answer = dataset[most_similar_index]["ai"]
        if user.lower() != dataset[most_similar_index]["user"].lower():
            newdata = {"user": user, "ai": answer}
            dataset.append(newdata)

            with open("call.json", "w") as file:
                json.dump(dataset, file, indent=2)
        return answer


if __name__ == "__main__":
    greet_user()

    while True:
        user_input = get_speech_input()
        if user_input:
            response = getresponse(user_input)
            speak(response)
        else:
            break
