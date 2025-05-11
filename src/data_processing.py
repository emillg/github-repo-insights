import os
import json


def merge_data(new_data, filepath, key):
    if os.path.exists(filepath):
        with open(filepath, "r") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = {key: []}

    existing_timestamps = {item["timestamp"] for item in existing_data[key]}
    for item in new_data[key]:
        if item["timestamp"] not in existing_timestamps:
            existing_data[key].append(item)

    existing_data[key] = sorted(
        existing_data[key], key=lambda x: x["timestamp"])

    return existing_data


def save_data(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as json_file:
        json.dump(data, json_file, indent=4)


def preprocess_data(data):
    dates = [item["timestamp"][:10] for item in data]
    counts = [item["count"] for item in data]
    return dates, counts
