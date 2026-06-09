import json
import os

PROFILE_FILE = "user_profile.json"


def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return {}

    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)


def remember_fact(key, value):
    profile = load_profile()

    profile[key] = value

    save_profile(profile)


def get_fact(key):
    profile = load_profile()

    return profile.get(key)

def get_profile():
    return load_profile()