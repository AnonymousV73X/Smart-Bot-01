import telebot
import json

admin_user_ids = [
    1816953935,
    1623281225,
    2143511704,
]


# Create a new telebot instance
bot = telebot.TeleBot("6074675799:AAGorq7Par0IHhUu0C-bnBPs9lKPjOKT8oI")

# Maximum number of files to be processed in a batch


@bot.message_handler(commands=["start"])
def start(message):
    text = '<pre><code class="language-text">Adding stuff please wait</code></pre>'
    bot.send_message(message.chat.id, text, parse_mode="HTML")


MAX_BATCH_SIZE = 300  # Maximum number of files to be processed in a batch
json_file = "file_data.json"
file_data = {}  # Initialize an empty dictionary for file data
update_mode_users = {}  # Initialize a dictionary to track users in update mode


# Modify the save_files function to accept the message parameter
def save_files(message):
    try:
        # Load existing data from JSON or create an empty dictionary
        with open(json_file, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Update the existing data with the new file details
    existing_data.update(file_data)

    # Write the updated data to the JSON file
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)

    # Get the list of file names that have been updated
    updated_file_names = list(file_data.keys())

    # Clear the file_data dictionary
    file_data.clear()

    # Print the number of files remaining for the batch
    remaining_files = MAX_BATCH_SIZE - len(existing_data)

    if updated_file_names:
        print(f"{remaining_files} files sent to JSON. Thank you!")
    else:
        print(f"{remaining_files} files sent to JSON. Thank you!")


# Handler for /update command
@bot.message_handler(commands=["update"])
def handle_update_command(message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        return

    # Check if the user is already in update mode
    if message.from_user.id in update_mode_users:
        return

    # Put the user in update mode
    update_mode_users[message.from_user.id] = True


# Handler for file messages while in update mode
@bot.message_handler(
    content_types=["document"],
    func=lambda message: message.from_user.id in update_mode_users,
)
def handle_file_update_mode(message):
    # Get the file name and ID
    file_name = message.document.file_name
    file_id = message.document.file_id

    # If the file name is already present, extend the list of file IDs
    if file_name in file_data:
        file_data[file_name].append(file_id)
    else:
        # If the file name is new, add it to the dictionary with the file ID as a list
        file_data[file_name] = [file_id]

    # Print the number of files remaining for the batch
    remaining_files = MAX_BATCH_SIZE - len(file_data)

    print( f"{remaining_files} files remaining...")

    # Check if the number of files reaches the batch size
    if len(file_data) >= MAX_BATCH_SIZE:
        # Ask the user if they want to send the files to JSON
        bot.send_message(
            message.chat.id,
            f"Do you want to send {MAX_BATCH_SIZE} files to JSON? (yes/no)",
        )


# Handler for responding to the confirmation to send files to JSON
@bot.message_handler(func=lambda message: message.text.lower() in ["yes", "no"])
def handle_confirmation(message):
    if message.text.lower() == "yes":
        if len(file_data) >= MAX_BATCH_SIZE:
            save_files(message)
    else:
        print("Files have not been sent to JSON. You can continue adding more files.")


# Handler for exiting update mode
@bot.message_handler(commands=["exitupdate"])
def handle_exit_update_command(message):
    # Check if the user is an admin and in update mode
    if message.from_user.id not in admin_user_ids:
        return

    if message.from_user.id in update_mode_users:
        # Remove the user from update mode
        del update_mode_users[message.from_user.id]
        bot.send_message(message.chat.id, "You have exited update mode.")
    else:
        bot.send_message(message.chat.id, "You are not in update mode.")


# Handler for the /listfiles command to list files in the batch
@bot.message_handler(commands=["listfiles"])
def handle_list_files_command(message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        return

    # Get the list of file names in the batch
    file_names = list(file_data.keys())

    if file_names:
        bot.send_message(
            message.chat.id, f"Files in the update batch:\n{', '.join(file_names)}"
        )
    else:
        bot.send_message(message.chat.id, "No files in the update batch.")


# Run the bot
while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Error: Unable to run the bot. {str(e)}")