import json

def convert_to_utf8(file_path):
    try:
        # Read the file using the default encoding (likely 'utf-8' on most systems)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()

        # Decode the data using the default encoding
        decoded_data = data.encode().decode('utf-8')

        # Re-encode the data using UTF-8
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(decoded_data)

        print(f"File '{file_path}' successfully converted to UTF-8.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while converting the file: {e}")

# Usage example:
file_path = 'file_data.json'
convert_to_utf8(file_path)