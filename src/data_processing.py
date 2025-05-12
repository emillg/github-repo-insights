from datetime import datetime, timedelta
import os
import json


def fill_missing_dates(data):
    """Fill in missing dates with default values (count: 0, uniques: 0)."""
    if not data:
        return data

    # Parse timestamps and find the date range
    timestamps = [datetime.strptime(
        item["timestamp"], "%Y-%m-%dT%H:%M:%SZ") for item in data]
    start_date = min(timestamps)
    end_date = max(timestamps)

    # Create a complete list of dates in the range
    complete_dates = {
        start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)}

    # Convert existing timestamps to a set for quick lookup
    existing_dates = {datetime.strptime(
        item["timestamp"], "%Y-%m-%dT%H:%M:%SZ") for item in data}

    # Add missing dates with default values
    for date in complete_dates - existing_dates:
        data.append({
            "timestamp": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": 0,
            "uniques": 0
        })

    return data


def merge_data(new_data, filepath, key):
    if os.path.exists(filepath):
        with open(filepath, "r") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = {key: []}

    # Create a dictionary for quick lookup of existing data by timestamp
    existing_data_by_timestamp = {
        item["timestamp"]: item for item in existing_data[key]
    }

    for item in new_data[key]:
        timestamp = item["timestamp"]
        if timestamp in existing_data_by_timestamp:
            # Update the values if the new values are higher
            existing_item = existing_data_by_timestamp[timestamp]
            existing_item["count"] = max(existing_item["count"], item["count"])
            existing_item["uniques"] = max(
                existing_item["uniques"], item["uniques"])
        else:
            # Add new data if the timestamp doesn't exist
            existing_data[key].append(item)

    # Fill in missing dates
    existing_data[key] = fill_missing_dates(existing_data[key])

    # Sort the data by timestamp
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
