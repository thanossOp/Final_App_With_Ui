import pyttsx3
import speech_recognition as sr
import os
from sentence_transformers import SentenceTransformer, util
from dateutil import parser
from datetime import datetime, timedelta
from pymongo import MongoClient

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

client = MongoClient("mongodb://localhost:27017/call_data")
db = client["call_data"]
dataset_collection = db["data"]
dataset = list(dataset_collection.find())

current_session_file_path = None

user_name = "nisarg"


def log_interaction(log_text):
    global current_session_file_path

    if current_session_file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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


def get_speech_input(try_count=0, max_tries=3):
    if try_count >= max_tries:
        speak(
            "It seems we're having trouble with the connection.I will call you latter. Goodbye!"
        )
        return None

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, phrase_time_limit=10, timeout=10)

    try:
        user_input = r.recognize_google(audio)
        log_interaction(f"User said: {user_input}\n")
        return user_input.lower()
    except sr.UnknownValueError as e:
        print(e)
        speak(f"I couldn't hear you. Are you there {user_name}?")
        return get_speech_input(try_count + 1, max_tries)


def greet_user():
    curent_hour = datetime.now().hour

    if 5 < curent_hour < 12:
        speak(f"Hello {user_name} Good Morning ")
    elif 12 <= curent_hour < 18:
        speak(f"Hello {user_name} Good Afternoon")
    else:
        speak(f"Hello {user_name} Good Evening ")

    speak(
        f"my name is thanos, and I'm calling from Health Insurance system. How are you today?"
    )


def extract_date_time(sentence):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    sentence = sentence.replace(
        "tomorrow", (today + timedelta(days=1)).strftime("%Y-%m-%d")
    )

    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for day in weekdays:
        if day in sentence.lower():
            day_index = weekdays.index(day)
            days_until_day = (day_index - today.weekday() + 7) % 7
            target_date = today + timedelta(days=days_until_day)
            sentence = sentence.replace(day, target_date.strftime("%Y-%m-%d"))
            break

    parsed_date_time = parser.parse(sentence, fuzzy=True)

    if parsed_date_time < datetime.now():
        speak(
            "date and time is earlier than today's date and time. Can you please provide me valid date and time"
        )
        new_input = get_speech_input()
        return extract_date_time(new_input)

    return parsed_date_time


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
            dataset_collection.insert_one(newdata)
        return answer


if __name__ == "__main__":
    greet_user()

    negative_keywords = [
        "not interested",
        "don't want",
        "don't have time",
        "don't need",
    ]
    consecutive_negative_responses = 0

    while True:
        user_input = 'I am fine'
        if any(keyword in user_input.lower() for keyword in negative_keywords):
            consecutive_negative_responses += 1
        else:
            consecutive_negative_responses = 0

        if "schedule my call" in user_input:
            speak(
                "Of course, I'd be happy to schedule the call for you. Could you please let me know what time works best for you?"
            )
            schedule_input = get_speech_input()
            schedule_time = extract_date_time(schedule_input)
            if schedule_time:
                speak(
                    f"Excellent! I've scheduled the call for {schedule_time} to discuss your health insurance plan. Thank you for your time. Have a great day {user_name}."
                )
            else:
                speak(
                    "I'm sorry, I couldn't understand the scheduling time. Let's try again."
                )
            break
        elif user_input and consecutive_negative_responses < 4:
            response = getresponse(user_input)
            speak(response)
        elif consecutive_negative_responses >= 4:
            speak(f"Okk {user_name}. Thank you for your time. Have a great day!")
            break
        else:
            break
