from dateutil import parser
from datetime import datetime, timedelta

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

# Function to simulate get_speech_input() and speak()
def get_speech_input():
    return input("Enter new speech input: ")

def speak(message):
    print(message)

sentence = 'schedule my call on tomorrow 3 pm.'
result = extract_date_time(sentence)

print("Original Sentence:", sentence)
print("Parsed Date and Time:", result)

# import pymongo

# mongourl = "mongodb://localhost:27017/['call_data']"
# client = pymongo.MongoClient(mongourl)
# database = client["call_data"]
# collection = database["data"]

# print(collection)

