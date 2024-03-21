import pandas as pd
import speech_recognition as sr
import pyttsx3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer
import spacy
import datetime
import os
import re

current_session_file_path = None


def log_interaction(log_text):
    global current_session_file_path

    if current_session_file_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = "data_recording"

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
    engine.setProperty('rate', 180)
    engine.setProperty("volume", 0.9)
    engine.say(response)
    engine.runAndWait()
    log_interaction(f"AI said: {response}")


def get_speech_input(try_count=0, max_tries=3):
    if try_count > max_tries:
        speak("It seems we're having trouble with the connection.I will call you latter. Goodbye!")
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
        speak("I couldn't hear you")
        return get_speech_input(try_count + 1, max_tries)


def greet_user(user_name):

    curent_hour = datetime.datetime.now().hour

    if 5 < curent_hour < 12:
        speak(f"Good Morning {user_name}")
    elif 12 <= curent_hour < 18:
        speak(f"Good Afternoon {user_name}")
    else:
        speak(f"Good Evening {user_name}")

    speak(f"Welcome to our Health Insurance Planning System!")
    speak(
        "To ensure I provide you with the best health insurance plan, I'll need some information."
    )
    speak(
        "Your privacy is important, and all your information will be handled confidentially."
    )
    speak("Let's get started!")


file_path = "insurance_data.csv"

original_df = pd.read_csv(file_path)

imputer = SimpleImputer(strategy="mean")

column_with_missing_values = ["age"]

original_df[column_with_missing_values] = imputer.fit_transform(
    original_df[column_with_missing_values]
)

features = original_df.drop(["claim"], axis=1)
target = original_df["claim"]


categorical_columns = features.select_dtypes(include=["object"]).columns

features = pd.get_dummies(features, columns=categorical_columns, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.2, random_state=42
)

reg = RandomForestRegressor(n_estimators=400, max_depth=4, random_state=42)
reg.fit(X_train, y_train)


def extract_gender():
    user_input = get_speech_input().lower()

    if "male" in user_input:
        gender = "male"
    elif "female" in user_input:
        gender = "female"
    else:
        speak("Can't understand. Please provide valid gender (male or female).")
        return extract_gender()

    return gender


def extract_numeric_value():
    user_input = get_speech_input()

    numeric_values = []
    numeric_str = ""
    number_mapping = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    for word in user_input.lower().split():
        if word.isdigit() or word.replace(".", "", 1).isdigit():
            numeric_str += word
        elif word in number_mapping:
            numeric_str += number_mapping[word]
        elif numeric_str:
            numeric_values.append(numeric_str)
            numeric_str = ""

    if numeric_str:
        numeric_values.append(numeric_str)

    try:
        last_sequence = numeric_values[-1]
        numeric_value = (
            float(last_sequence) if "." in last_sequence else int(last_sequence)
        )
        return numeric_value
    except ValueError:
        speak(f"Sorry, I couldn't understand. Please provide a valid numeric value.")
        return extract_numeric_value()
    except IndexError:
        speak(f"Sorry, I couldn't understand. Please provide a valid numeric value.")
        return extract_numeric_value()


def extract_binary_category():
    user_input = get_speech_input().lower()

    if "yes" in user_input or "no" in user_input:
        last_occurrence_yes = user_input.rfind("yes")
        last_occurrence_no = user_input.rfind("no")
        last_occurrence = max(last_occurrence_yes, last_occurrence_no)
        category_value = user_input[last_occurrence : last_occurrence + 3]
    else:
        speak("Can't understand. Please say 'yes' or 'no'.")
        # user_input = None
        return extract_binary_category()

    return category_value


def extract_city():
    user_input = get_speech_input().lower()

    nlp = spacy.load("en_core_web_sm")

    doc = nlp(user_input)

    cities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    if cities:
        return cities[-1]
    else:
        return extract_city()


def extract_job_title():
    user_input = get_speech_input().lower()

    job_titles = original_df["job_title"].unique()
    for job_title in job_titles:
        if job_title.lower() in user_input:
            return job_title

    speak("Can't understand. Please provide a valid job title.")
    return extract_job_title()


def extract_hereditary_diseases(user_hereditary_diseases):
    user_hereditary_diseases_lower = user_hereditary_diseases.lower().strip()

    if user_hereditary_diseases_lower == "yes":
        speak("Could you specify which hereditary diseases are present in your family?")
        command = get_speech_input()

        diseases_list = original_df["hereditary_diseases"].unique()
        user_diseases = []

        for disease in diseases_list:
            if disease.lower() in command:
                user_diseases.append(disease)

        if not user_diseases:
            speak("Can't understand. Please specify at least one hereditary disease.")
            return extract_hereditary_diseases(user_hereditary_diseases)

        return user_diseases

    elif user_hereditary_diseases_lower == "no":
        return ["NoDisease"]

    else:
        speak("Can't understand. Please say 'yes' or 'no'.")
        return extract_hereditary_diseases(user_hereditary_diseases)


def format_name(name):
    format_word = "".join(word.capitalize() for word in name.split())
    return format_word

def extract_name():
    input_text = get_speech_input()
    matches_pattern = re.findall(r'my name is (\w+)', input_text, re.IGNORECASE)
    
    if matches_pattern:
        return matches_pattern[0] 
    else:
        matches_words = re.findall(r'\b\w+\b', input_text)
        valid_names = [match for match in matches_words if match.lower() not in ['is', 'my', 'name'] and len(match) > 1]

        if valid_names:
            return valid_names[0]  
        else:
            return None

speak("What is You name?")
user_name = extract_name()

greet_user(user_name)

speak(
    " Firstly, age,age is a crucial factor in tailoring the best health insurance plan for you.Can you please tell me what is your age?"
)
user_age = extract_numeric_value()

speak(" Great, thank you. Now, could you share your current weight in pounds?")
user_weight = round(extract_numeric_value())

speak("Perfect. Next, can you tell me the city where you currently reside?")
user_city_name = extract_city()
user_city = format_name(user_city_name)

speak("Excellent. And what is your gender?")
user_gender = extract_gender()

speak("Thank you. Now, could you share a bit about your occupation or job?")
user_job = extract_job_title()
user_job_title = format_name(user_job)

speak(
    "Great to know. Moving on, could you please share the number of family members you'd like to include in the plan?"
)
user_members = extract_numeric_value()

speak(
    "Perfect. Now, are there any hereditary diseases or medical conditions that run in your family that we should be aware of?please say yes or no"
)
user_hereditary_diseases = extract_binary_category()
check_dieases = extract_hereditary_diseases(user_hereditary_diseases)

if user_hereditary_diseases == "yes" and check_dieases == "diabetes":
    user_diabetes = "yes"
else:
    user_diabetes = "no"

speak(
    "Thank you for providing that information. Next, do you smoke?please say yes or no"
)
user_smoker = extract_binary_category()

speak("Now, could you please share your blood pressure levels in digits?")
user_bloodpressure = extract_numeric_value()

speak(
    "Thank you for sharing that. Lastly, do you engage in regular exercise?please say yes or no"
)
user_regular_ex = extract_binary_category()


# user_age = 24
# user_gender = "male"
# user_weight = 61.7
# user_hereditary_diseases = "yes"
# check_dieases_list = ['Diabetes', 'Cancer']
# user_bloodpressure = 72

# if user_hereditary_diseases == "yes" and "Diabetes" in check_dieases_list:
#     user_diabetes = "yes"
# else:
#     user_diabetes = 'no'

# user_members = 3
# user_smoker = "no"
# user_city_name = "new york"
# user_regular_ex = "yes"
# user_job = "engineer"
# user_city = format_name(user_city_name)
# user_job_title = format_name(user_job)
# check_dieases = check_dieases_list

check_dieases_lower = [disease.lower() for disease in check_dieases]

matching_row = original_df[
    (original_df["age"] == user_age)
    & (original_df["sex"] == user_gender)
    & (original_df["weight"] == user_weight)
    & original_df["hereditary_diseases"].apply(
        lambda x: any(disease in x.lower() for disease in check_dieases_lower)
    )
    & (original_df["members"] == user_members)
    & (original_df["smoker"] == (1 if user_smoker == "yes" else 0))
    & (original_df["city"] == user_city)
    & (original_df["bloodpressure"] == user_bloodpressure)
    & (original_df["diabetes"] == (1 if user_diabetes == "yes" else 0))
    & (original_df["regular_ex"] == (1 if user_regular_ex == "yes" else 0))
    & (original_df["job_title"] == user_job_title)
]

if not matching_row.empty:
    actual_charges = matching_row["claim"].min()
    speak(
        "Thank you for co-operate and sharing this informations. It will help us find the best health insurance plan for you."
    )
    decimal_place = 2
    rounded_charge = round(actual_charges, decimal_place)
    speak(
        f"So {user_name} Based on the information you provided, the estimated insurance charges for your tailored plan are: {rounded_charge}"
    )
else:
    user_data = pd.DataFrame(
        {
            "age": [user_age],
            "sex_male": [1 if user_gender == "male" else 0],
            "weight": [user_weight],
            "hereditary_diseases_NoDisease": [
                1 if user_hereditary_diseases == "yes" else 0
            ],
            "members": [user_members],
            "smoker": [1 if user_smoker == "yes" else 0],
            **{
                f"{col}_{user_input}": 1
                for col, user_input in zip(
                    categorical_columns, [user_city, user_job_title]
                )
            },
            "bloodpressure": [user_bloodpressure],
            "diabetes": [1 if user_diabetes == "yes" else 0],
            "regular_ex": [1 if user_regular_ex == "yes" else 0],
        },
        columns=features.columns,
    )

    predicted_charge = reg.predict(user_data)

    rounded_charge = round(predicted_charge[0])

    new_entry = pd.DataFrame(
        {
            "age": [user_age],
            "sex": [user_gender],
            "weight": [user_weight],
            "hereditary_diseases": [
                (
                    "NoDisease"
                    if user_hereditary_diseases == "no"
                    else ", ".join(check_dieases)
                )
            ][0].replace('"', ""),
            "members": [user_members],
            "smoker": [1 if user_smoker == "yes" else 0],
            "city": [user_city],
            "bloodpressure": [user_bloodpressure],
            "diabetes": [1 if user_diabetes == "yes" else 0],
            "regular_ex": [1 if user_regular_ex == "yes" else 0],
            "job_title": [user_job_title],
            "claim": [rounded_charge],
        },
        columns=original_df.columns,
    )
    updated_df = pd.concat([original_df, new_entry], ignore_index=True)

    updated_df.to_csv(file_path, index=False)

    predicted_charge_rf = reg.predict(features)
    mae_rf = mean_absolute_error(target, predicted_charge_rf)
    r2_rf = r2_score(target, predicted_charge_rf)

    # print(f"Mean Absolute Error (Random Forest Regression): {mae_rf}")
    # print(f"R^2 Score (Random Forest Regression): {r2_rf}")
    speak(
        f"Thank you {user_name} for co-operate with us and sharing all informations. It will help us find the best health insurance plan for you."
    )
    speak(
        f"So {user_name} Based on the information you provided, the estimated insurance charges for your tailored plan are: {rounded_charge}"
    )
