from sentence_transformers import SentenceTransformer, util
import pyttsx3
import speech_recognition as sr
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import datetime
import os
import re
from pymongo import MongoClient


model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

client = MongoClient("mongodb://localhost:27017/enquiry_data")
db = client["enquiry_data"]
dataset_collection = db["data"]
dataset = list(dataset_collection.find())

current_session_file_path = None


def log_interaction(log_text):
    global current_session_file_path

    if current_session_file_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("enquiry_recording")

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
    engine.setProperty("voice", voice[1].id)
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 0.9)
    engine.say(response)
    engine.runAndWait()
    log_interaction(f"AI said: {response}")


def get_speech_input():

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, phrase_time_limit=10, timeout=10)

    try:
        user_input = r.recognize_google(audio)
        log_interaction(f"User said: {user_input}\n")
        return user_input.lower()
    except sr.UnknownValueError as e:
        return None


def generate_chatgpt_response(user_input):
    chatgpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
    chatgpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    input_ids = chatgpt_tokenizer.encode(user_input, return_tensors="pt")
    output = chatgpt_model.generate(
        input_ids,
        max_length=100,
        num_beams=5,
        no_repeat_ngram_size=2,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
    )
    response = chatgpt_tokenizer.decode(output[0], skip_special_tokens=True)

    return response


def greet_user(user_name):
    curent_hour = datetime.datetime.now().hour

    if 5 < curent_hour < 12:
        speak(f"Good Morning {user_name}")
    elif 12 <= curent_hour < 18:
        speak(f"Good Afternoon {user_name}")
    else:
        speak(f"Good Evening {user_name}")

    speak(f"Welcome to our Health Insurance Planning System!")
    speak("How can i assist you today?")


def extract_name():
    input_text = get_speech_input()
    matches_pattern = re.findall(r"my name is (\w+)", input_text, re.IGNORECASE)

    if matches_pattern:
        return matches_pattern[0]
    else:
        matches_words = re.findall(r"\b\w+\b", input_text)
        valid_names = [
            match
            for match in matches_words
            if match.lower() not in ["is", "my", "name"] and len(match) > 1
        ]

        if valid_names:
            return valid_names[0]
        else:
            return None


def get_response(user_question):

    user_question_embeding = model.encode(user_question, convert_to_tensor=True)
    similarities = []

    for data in dataset:
        dataset_question_embeding = model.encode(
            data["question"], convert_to_tensor=True
        )
        similarity_score = util.pytorch_cos_sim(
            user_question_embeding, dataset_question_embeding
        )
        similarities.append(similarity_score)

    most_similar_index = similarities.index(max(similarities))

    if similarities[most_similar_index] < 0.3:
        chatgpt_response = generate_chatgpt_response(user_question)

        newdata = {"question": user_question, "answer": chatgpt_response}
        dataset_collection.insert_one(newdata)

        speak(chatgpt_response)
        return chatgpt_response

    else:
        answer = dataset[most_similar_index]["answer"]
        if user_question.lower() != dataset[most_similar_index]["question"].lower():
            newdata = {"question": user_question, "answer": answer}
            dataset_collection.insert_one(newdata)
        return answer


if __name__ == "__main__":
    speak("Hello! What is your name?")
    user_name = extract_name()

    greet_user(user_name)

    while True:
        user_question = get_speech_input()
        user_input = user_question

        if user_input:
            response = get_response(user_input)
            speak(response)

        elif user_input is None:
            speak("Do you have any more questions? Say 'yes' or 'no'.")
            user_response = get_speech_input()

            if user_response and "no" in user_response:
                speak(f"Goodbye {user_name}! I hope we were able to assist you.")
                break
            else:
                speak(
                    f"Sorry, I didn't get a response. If you have more questions, feel free to ask. Otherwise, say 'no' to end the conversation."
                )
        else:
            continue
