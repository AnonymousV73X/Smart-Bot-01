import json
import re


def remove_duplicate_ids(file_data):
    # Iterate over each file in the file data
    for file_name, file_ids in file_data.items():
        if len(file_ids) > 1:
            # Remove one of the duplicate IDs
            file_data[file_name] = [file_ids[0]]


def load_file_data(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data


def save_file_data(file_name, file_data):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(file_data, file, indent=4)


# Define the file name
file_name = "file_data.json"

# Load file data from JSON
file_data = load_file_data(file_name)

# Call the function to remove duplicate IDs
remove_duplicate_ids(file_data)


# Custom sorting function
def custom_sort_key(key):
    # Remove special characters you want to ignore
    cleaned_key = re.sub(r'[\/!_.,:;\'"+&%$#!)(\^<>?|]', "", key)

    # Check if the key starts with a number
    if cleaned_key[0].isdigit():
        # Return a tuple with (0, cleaned_key) to make keys starting with numbers come first
        return (0, cleaned_key)
    else:
        # Return a tuple with (1, cleaned_key) for other keys
        return (1, cleaned_key)


# Sort the keys alphabetically, ignoring special characters and considering numbers first
sorted_file_data = {
    k: v
    for k, v in sorted(file_data.items(), key=lambda item: custom_sort_key(item[0]))
}

# Write the sorted data back to file_data.json
save_file_data(file_name, sorted_file_data)

print("File_data.json has been sorted alphabetically.")
