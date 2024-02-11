# Importing Modules

import time


import telebot
import json
import re
import random
from jokes import jokes


import threading
from difflib import SequenceMatcher
from telebot.types import Message
from stickers import sticker_ids, not_found_stickers, hello_stickers, photos
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Create a Telebot instance
bot = telebot.TeleBot("6074675799:AAGorq7Par0IHhUu0C-bnBPs9lKPjOKT8oI")


# Define an empty list to store user data
user_ids = []

admin_user_ids = [
    1816953935,
    1623281225,
    2143511704,
    1315053937,
    1209904298,
    1529546916
]


MAX_BATCH_SIZE = 1000  # Maximum number of files to be processed in a batch
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

    # Send a message with the names of files that have been updated
    # Send a message with the names of files that have been updated
    if updated_file_names:
        message_text = f"{remaining_files*-1} Files sent to JSON.\n\n⚡Updated files:"
        for file_name in updated_file_names:
            file_name_html = f"<pre><code class='language-text'>{file_name}</code></pre>"
            message_text += f"\n\n ✅\t{file_name_html}"

        ##bot.send_message(message.chat.id, message_text, /parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, f"{remaining_files} files sent to JSON.")




# Handler for /update command
@bot.message_handler(commands=["update"])
def handle_update_command(message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
        return

    # Check if the user is already in update mode
    if message.from_user.id in update_mode_users:
        bot.send_message(message.chat.id, "You are already in update mode.")
        return

    # Put the user in update mode
    update_mode_users[message.from_user.id] = True
    bot.send_message(
        message.chat.id, "You are now in update mode. You can send files to update."
    )


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
        bot.send_message(
            message.chat.id,
            "Files have not been sent to JSON. You can continue adding more files.",
        )


# Handler for exiting update mode
@bot.message_handler(commands=["exitupdate"])
def handle_exit_update_command(message):
    # Check if the user is an admin and in update mode
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
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
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
        return

    # Get the list of file names in the batch
    file_names = list(file_data.keys())

    if file_names:
        bot.send_message(
            message.chat.id, f"Files in the update batch:\n{', '.join(file_names)}"
        )
    else:
        bot.send_message(message.chat.id, "No files in the update batch.")


broadcast_mode = {}  # Use a dictionary to track broadcast mode for each admin user


# Function to load user data from JSON file
def load_user_ids():
    global user_ids
    try:
        with open("user_ids.json", "r", encoding="utf-8") as file:
            user_data = json.load(file)
            user_ids = [user["id"] for user in user_data]
    except FileNotFoundError:
        user_ids = []


load_user_ids()


# Command handler for /broadcast command
@bot.message_handler(commands=["broadcast"])
def handle_broadcast_command(message: telebot.types.Message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
        return

    # Check if broadcast mode is already active for this admin
    if message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id]:
        bot.send_message(message.chat.id, "You are already in broadcast mode.")
        return

    # Activate broadcast mode for this admin
    broadcast_mode[message.from_user.id] = True
    bot.send_message(
        message.chat.id,
        "You are now in broadcast mode. Anything you send will be sent to all users.",
    )


# Command handler for /stop command to exit broadcast mode
@bot.message_handler(commands=["stop"])
def handle_stop_command(message: telebot.types.Message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
        return

    # Check if broadcast mode is active for this admin
    if message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id]:
        # Deactivate broadcast mode for this admin
        broadcast_mode[message.from_user.id] = False
        bot.send_message(message.chat.id, "Broadcast mode has been deactivated.")
    else:
        bot.send_message(message.chat.id, "Broadcast mode is not active.")


# Command handler for sending files (text, audio, photo, video, document, sticker) with a caption in broadcast mode
@bot.message_handler(
    content_types=["text", "audio", "photo", "video", "document", "sticker"],
    func=lambda message: message.from_user.id in admin_user_ids
    and broadcast_mode.get(message.from_user.id),
)
def send_broadcast_files_with_caption(message: telebot.types.Message):
    # Get the caption from the admin's message
    original_caption = message.caption or "@Smart_Search69bot"

    # Add mentioned content to the caption
    caption = f"{original_caption}\n\n@alekiesbot | @Smart_Search69bot\n\n#Announcement"

    # Loop through user IDs and send the appropriate file type with the modified caption
    for user_id in user_ids:
        try:
            if message.text:
                bot.send_message(user_id, message.text)
            elif message.audio:
                audio_file_id = message.audio.file_id
                bot.send_audio(user_id, audio_file_id, caption=caption)
            elif message.photo:
                photo_file_id = message.photo[-1].file_id
                bot.send_photo(user_id, photo_file_id, caption=caption)
            elif message.video:
                video_file_id = message.video.file_id
                bot.send_video(user_id, video_file_id, caption=caption)
            elif message.document:
                document_file_id = message.document.file_id
                bot.send_document(user_id, document_file_id, caption=caption)
            elif message.sticker:
                sticker_file_id = message.sticker.file_id
                bot.send_sticker(user_id, sticker_file_id)
        except Exception as e:
            print(f"Failed to send to user {user_id}: {str(e)}")

    # Deactivate broadcast mode after sending
    broadcast_mode[message.from_user.id] = False
    bot.send_message(message.chat.id, "Broadcast mode has been deactivated.")


# ... (Rest of your existing code)


# Dictionary to store user information
user_data = []


# Function to load user data from JSON file
def load_user_data():
    global user_data
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = []


# Function to save user data to JSON file
def save_user_data():
    with open("user_data.json", "w") as file:
        json.dump(user_data, file)


# Load user data when the bot starts
load_user_data()


@bot.message_handler(commands=["log"])
def handle_log_command(message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
        return
    # Load the file data
    file_data = load_file_data()

    # Count the total number of file IDs
    total_files = sum(len(file_ids) for file_ids in file_data.values())

    # Additional logging information
    num_users = len(user_data)  # Assuming you have user_data defined somewhere

    # Construct the message
    msg = "*𝐁𝐨𝐭 𝐋𝐨𝐠 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :*\n-------------------------------------"
    msg += f"\n*🎦 Total Files :* {total_files}\n-------------------------------------"
    # No storage used information
    msg += f"\n *👤 Registered Users :* {num_users*3}\n-------------------------------------"
    msg += "\n *⌚ Uptime :* Consuming CPU\n-------------------------------------"

    # Send the log report message
    sent_message = bot.send_message(
        chat_id=message.chat.id, text=msg, parse_mode="Markdown"
    )

    # Function to delete the user's command and the bot's message after 30 seconds
    def delete_messages():
        time.sleep(10)  # Wait for 30 seconds
        # Delete the user's command
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except telebot.apihelper.ApiException:
            pass  # If the message is already deleted or any other issue occurs, just continue
        # Delete the bot's message
        try:
            bot.delete_message(
                chat_id=message.chat.id, message_id=sent_message.message_id
            )
        except telebot.apihelper.ApiException:
            pass  # If the message is already deleted or any other issue occurs, just continue

    # Create a thread to delete the messages after 30 seconds
    deletion_thread = threading.Thread(target=delete_messages)
    deletion_thread.start()


# Function to delete a message by its message_id after a certain delay
def delete_message_after_delay(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except telebot.apihelper.ApiException:
        pass


# Command handler for /use command
@bot.message_handler(commands=["use"])
def handle_use_command(message: Message):
    if message.from_user.id not in admin_user_ids:
        return
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Check if the user is already registered
    for user in user_data:
        if user["id"] == user_id:
            reply_message = bot.reply_to(
                message,
                f"Come on, {user_name} 😊!\n You are already registered on the leaderboard.\n\nCheck out where you're ranked 👇\n\n 🏆\tLeaderboard : /leaderboard \n\n🙏\tThank you for staying with us",
            )

            # Delete the command and the bot's response after 5 seconds
            threading.Thread(
                target=delete_message_after_delay,
                args=(message.chat.id, message.message_id, 15),
            ).start()
            threading.Thread(
                target=delete_message_after_delay,
                args=(message.chat.id, reply_message.message_id, 15),
            ).start()
            return

    # Assign a number based on the number of registered users
    user_number = len(user_data) + 1

    # Create a new entry for the user
    new_user = {"id": user_id, "name": user_name, "number": user_number}

    # Save user data in the list
    user_data.append(new_user)

    # Save user data to the JSON file
    save_user_data()

    # Send a confirmation message
    confirmation_message = bot.reply_to(
        message,
        f"Congratulations, {user_name}!☺️\n You have been registered on the leaderboard as User {user_number}.",
    )

    # Delete the command and the bot's response after 10 seconds
    threading.Thread(
        target=delete_message_after_delay,
        args=(message.chat.id, message.message_id, 10),
    ).start()
    threading.Thread(
        target=delete_message_after_delay,
        args=(message.chat.id, confirmation_message.message_id, 10),
    ).start()


# Command handler for /leaderboard command
@bot.message_handler(commands=["leaderboard"])
def handle_leaderboard_command(message: telebot.types.Message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "You are not authorized to perform this action."
        )
        return
    user_id = message.from_user.id

    # Check if the user is registered
    if not is_user_registered(user_id):
        # If the user is not registered, send a message asking them to register first
        registration_message = bot.reply_to(
            message,
            "You need to register using the /use command before you can view the leaderboard.",
        )
        # Delete the registration message after 10 seconds
        threading.Thread(
            target=delete_message_after_delay,
            args=(message.chat.id, registration_message.message_id, 10),
        ).start()
        # Delete the user's command after 10 seconds
        threading.Thread(
            target=delete_message_after_delay,
            args=(message.chat.id, message.message_id, 10),
        ).start()
        return

    # Sort the user data based on the user numbers
    sorted_users = sorted(user_data, key=lambda x: x["number"])

    # Number of users to display per page
    users_per_page = 10

    # Get the page number from the user's input, default to 1 if not provided or invalid
    try:
        page_number = int(message.text.split()[1])
        if page_number < 1:
            page_number = 1
    except (ValueError, IndexError):
        page_number = 1

    # Calculate the starting and ending indices of the users to display on the current page
    start_index = (page_number - 1) * users_per_page
    end_index = start_index + users_per_page

    # Get the users for the current page
    users_on_page = sorted_users[start_index:end_index]

    # Create the leaderboard caption for the current page
    leaderboard_caption = "📃 𝐋𝐞𝐚𝐝𝐞𝐫𝐛𝐨𝐚𝐫𝐝 :\n\n"
    for user in users_on_page:
        leaderboard_caption += f"User No. {user['number']} - {user['name']}\n-------------------------------------\n"

    # Create an inline keyboard to handle pagination
    inline_keyboard = InlineKeyboardMarkup(row_width=1)  # Changed row_width to 1

    # Add navigation buttons for next and previous pages side by side on the same row
    navigation_row = []
    if len(sorted_users) > end_index:
        navigation_row.append(
            InlineKeyboardButton(
                " Next ➡️", callback_data=f"page_next:{page_number + 1}"
            )
        )
    if page_number > 1:
        navigation_row.append(
            InlineKeyboardButton(
                "⬅️ Previous", callback_data=f"page_prev:{page_number - 1}"
            )
        )
    inline_keyboard.add(*navigation_row)  # Unpack the list to add buttons side by side

    # Pick a random photo from the list of available photos
    photo_path = random.choice(photos)

    # Send the leaderboard as a photo with the caption and inline keyboard
    with open(photo_path, "rb") as image_file:
        leaderboard_message = bot.send_photo(
            chat_id=message.chat.id,
            photo=image_file,
            caption=leaderboard_caption,
            reply_markup=inline_keyboard,
        )

    # Delete the leaderboard message and the user's command after 45 seconds
    threading.Thread(
        target=delete_message_after_delay,
        args=(message.chat.id, message.message_id, 45),
    ).start()
    threading.Thread(
        target=delete_message_after_delay,
        args=(message.chat.id, leaderboard_message.message_id, 45),
    ).start()


# Function to check if a user is registered
def is_user_registered(user_id):
    for user in user_data:
        if user["id"] == user_id:
            return True
    return False


# Callback query handler to handle pagination
@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_pagination_callback(call: telebot.types.CallbackQuery):
    try:
        _, page_number = call.data.split(":")
        page_number = int(page_number)

        if page_number == 0:
            # If the user is on page 1 and wants to navigate back, set the page number to the last page
            sorted_users = sorted(user_data, key=lambda x: x["number"])
            last_page_number = (len(sorted_users) - 1) // 10 + 1
            page_number = last_page_number

        # Edit the existing leaderboard message to show the requested page
        edit_leaderboard(call.message, page_number)

        # Answer the callback query to remove the "loading" state from the button
        bot.answer_callback_query(call.id)

    except ValueError:
        # In case of invalid data, answer the callback query with an error message
        bot.answer_callback_query(call.id, text="Why did you click that!😁")


# Function to edit the leaderboard message to show the requested page
def edit_leaderboard(message: telebot.types.Message, page_number: int):
    # Sort the user data based on the user numbers
    sorted_users = sorted(user_data, key=lambda x: x["number"])

    # Number of users to display per page
    users_per_page = 10

    # Calculate the starting and ending indices of the users to display on the current page
    start_index = (page_number - 1) * users_per_page
    end_index = start_index + users_per_page

    # Get the users for the current page
    users_on_page = sorted_users[start_index:end_index]

    # Create the leaderboard caption for the current page
    leaderboard_caption = "📃 𝐋𝐞𝐚𝐝𝐞𝐫𝐛𝐨𝐚𝐫𝐝 :\n\n"
    for user in users_on_page:
        leaderboard_caption += f"👤\tUser No. {user['number']}\t\t - \t\t{user['name']}\n-------------------------------------\n"

    # Create an inline keyboard to handle pagination
    inline_keyboard = InlineKeyboardMarkup(row_width=2)

    # Add navigation buttons for next and previous pages side by side on the same row
    navigation_row = []
    if page_number > 1:
        navigation_row.append(
            InlineKeyboardButton(
                "⏪\t Previous", callback_data=f"page_prev:{page_number - 1}"
            )
        )
    if len(sorted_users) > end_index:
        navigation_row.append(
            InlineKeyboardButton(
                "Next \t⏩", callback_data=f"page_next:{page_number + 1}"
            )
        )

    # If both buttons are present, add them in the desired order
    if len(navigation_row) == 2:
        inline_keyboard.add(navigation_row[0], navigation_row[1])
    elif len(navigation_row) == 1:
        inline_keyboard.add(navigation_row[0])  # If only one button is present, add it

    # Update the leaderboard message with the new caption and inline keyboard
    bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message.message_id,
        caption=leaderboard_caption,
        reply_markup=inline_keyboard,
    )


# Function to handle the start command
@bot.message_handler(commands=["start"])
def welcome(message):
    user = message.from_user
    user_id = user.id
    user_name = user.first_name

    # Check if the user is already registered
    if any(user_data_item["id"] == user_id for user_data_item in user_data):
        # User is already registered, handle as needed
        pass
    else:
        # Assign a number based on the number of registered users
        user_number = len(user_data) + 1

        # Create a new entry for the user
        new_user = {"id": user_id, "name": user_name, "number": user_number}

        # Save user data in the list
        user_data.append(new_user)

        # Save user data to the JSON file
        save_user_data()

    photo_path = (
        "photo_2023-07-20_13-14-25.jpg"  # Replace with the actual path to your image
    )
    photo_caption = f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐒𝐦𝐚𝐫𝐭 𝐄𝐧𝐭𝐞𝐫𝐭𝐚𝐢𝐧𝐦𝐞𝐧𝐭, {user.first_name}! 😊\n\nI'm a simple file search bot.Just send me the name of the Series or Movie you want, and I'll check my database for it.\n\n📝 Please Note: All files generated here will be deleted after some few minutes.\n\n⚠️You're using the slow version of this bot"

    # Send the photo with caption and the inline keyboard
    bot.send_photo(
        chat_id=message.chat.id,
        photo=open(photo_path, "rb"),
        caption=photo_caption,
    )
    random_sticker_id = random.choice(hello_stickers)
    bot.send_sticker(chat_id=message.chat.id, sticker=random_sticker_id)


# Function to handle the alive command
@bot.message_handler(commands=["alive"])
def alive(message):
    user = message.from_user
    # Randomly select a joke from the array
    joke = random.choice(jokes)

    caption = f"𝑶𝒇 𝑪𝒐𝒖𝒓𝒔𝒆 𝑰'𝒎 𝑨𝒍𝒊𝒗𝒆,\t {user.first_name} 😊\n\n {joke}\n\n 𝑶𝒌𝒂𝒚 𝒋𝒐𝒌𝒆𝒔 𝒂𝒔𝒊𝒅𝒆 😁\n 𝑾𝒉𝒂𝒕 𝑺𝒆𝒓𝒊𝒆𝒔 𝒄𝒂𝒏 𝑰 𝒈𝒆𝒕 𝒚𝒐𝒖 💁"
    photo_path = (
        "photo_2023-07-20_13-15-28.jpg"  # Replace with the actual path to your image
    )

    # Send the photo with caption (without the button)
    alive_message = bot.send_photo(
        chat_id=message.chat.id,
        photo=open(photo_path, "rb"),
        caption=caption,
    )

    # Function to delete messages after a certain delay
    def delete_message_after_delay(chat_id, message_id, delay):
        time.sleep(delay)
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except telebot.apihelper.ApiException:
            pass  # If the message is already deleted or any other issue occurs, just continue

    # Create threads to delete messages after a certain delay
    thread_message = threading.Thread(
        target=delete_message_after_delay,
        args=(message.chat.id, message.message_id, 30),
    )
    thread_alive_message = threading.Thread(
        target=delete_message_after_delay,
        args=(message.chat.id, alive_message.message_id, 30),
    )

    # Start the threads
    thread_message.start()
    thread_alive_message.start()


#########################################################################################

#########################################################################################

#########################################################################################

#########################################################################################


# Create a dictionary to keep track of the user's search progress
search_progress = {}


# Load file data from the file_data JSON
def load_file_data():
    try:
        with open("file_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data


##########################################################################################


def delete_messages_after_delay(bot, chat_id, message_ids, delay):
    time.sleep(delay)
    try:
        for message_id in message_ids:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
    except telebot.apihelper.ApiException:
        pass  # If the message is already deleted or any other issue occurs, just continue


def start_thread_to_delete_messages(bot, chat_id, message_ids, delay=30):
    thread = threading.Thread(
        target=delete_messages_after_delay,
        args=(bot, chat_id, message_ids, delay),
    )
    thread.start()


# Function to calculate similarity score between two strings based on the first 4 characters
# Function to calculate similarity score between two strings
def similarity_score(query, suggestion):
    query = query.lower()
    suggestion = suggestion.lower()
    
    # Calculate the similarity ratio based on the entire strings
    full_ratio = SequenceMatcher(None, query, suggestion).ratio()
    
    # Calculate the similarity ratio based on the first 4 characters
    prefix_ratio = SequenceMatcher(None, query[:4], suggestion[:4]).ratio()
    
    # Weight the full ratio and prefix ratio to emphasize the importance of the first 4 characters
    weighted_ratio = (full_ratio * 0.2) + (prefix_ratio * 0.8)
    
    return weighted_ratio


###################################################################################


# Function to limit the search query length
def limit_search_query_length(search_query, max_length):
    if len(search_query) > max_length:
        # Truncate the search query to the specified max length
        limited_search_query = search_query[:max_length]
        # Remove any incomplete words at the end of the truncated search query
        limited_search_query = limited_search_query.rsplit(" ", 1)[0]
        return limited_search_query
    return search_query


search_query = ""


def custom_sort(x):
    keywords_present = any(
        keyword.lower() in x[0].lower() for keyword in ["x265", "10bit"]
    )
    modified_string = re.sub(r"[%!_.,:;'#%$@`~()+=*&<>?/\- ]", "", x[0]).lower()
    return (1 if keywords_present else 0, modified_string)


# Handle search queries
@bot.message_handler(func=lambda message: True)
def handle_search(message):
    chat_id = message.chat.id
    global search_query

    # Check if there's a previous inline keyboard message and delete it (if possible)
    search_data = search_progress.get(chat_id, {})
    if "message_id" in search_data:
        try:
            bot.delete_message(chat_id=chat_id, message_id=search_data["message_id"])
        except telebot.apihelper.ApiException as e:
            pass

        del search_data["message_id"]

    search_query = message.text.lower()

    search_query = limit_search_query_length(search_query, max_length=70)

    
    # and replace years from 1990 to the current year (2023) with empty strings
    search_query = re.sub(r"[,_!\.\-]|(\s+|^)(19[9][0-9]|20[0-2][0-3])", " ", search_query)



    # Load file data
    file_data = (
        load_file_data()
    )  # Assuming the 'load_file_data()' function exists to load file data

    # Search for files based on query
    results = []

    for file_name, file_ids in file_data.items():
        # Replace underscores, dots, and hyphens with spaces in the file name
        normalized_file_name = re.sub(r"[_!\.\-]", " ", file_name.lower())

        # Check if there is a year in the normalized file name
        if re.search(r"\b(19|20)\d{2}\b", normalized_file_name):
            normalized_file_name = re.sub(
                r"\b(19|20)\d{2}\b", " ", normalized_file_name
            )

        # Replace consecutive spaces with a single space if there are more than one
        normalized_file_name = re.sub(r" +", " ", normalized_file_name)

        if search_query in normalized_file_name:
            for file_id in file_ids:
                results.append((file_name, file_id))

    # Remove duplicates from the results
    results = list(set(results))

    # Sort results based on file name while considering priority keywords
    results.sort(key=custom_sort, reverse=True)

    # Send search results to user
    num_results = len(results)
    if num_results == 0:
        try:
            # Suggest similar file names using a similarity score algorithm
            file_name_scores = [
                (file_name, similarity_score(search_query, file_name.lower()))
                for file_name in file_data
            ]

            # Sort the file names based on similarity scores in descending order
            file_name_scores = sorted(
                file_name_scores, key=lambda x: x[1], reverse=True
            )

            # Select the top 5 suggestions
            top_suggestions = [file_name for file_name, _ in file_name_scores[:5]]

            # Modify the suggestions to show only the first word (including spaces)
            # Replace special characters with spaces in the top_suggestions list
            top_suggestions = [
                re.sub(r"\W+", " ", suggestion) for suggestion in top_suggestions
            ]
            # Construct the message text with search query suggestions in Markdown format

            message_text = f"🙅‍♂️\t\tSorry, '{search_query.title()}' Not Found!\n\nPlease Check Your Spelling or Use The Correct Search Syntax i.e \n\n*Bay*\n*Baymax*\n*Baymax S01*\n*Baymax S01E02*\n\nMeanwhile, here are some files closely related to \"{search_query.title()}\" that are available in our database\t💁  :"

            # Create the inline keyboard with the suggestions as buttons
            keyboard = telebot.types.InlineKeyboardMarkup()

            for suggestion in top_suggestions:
                keyboard.add(
                    telebot.types.InlineKeyboardButton(
                        suggestion,
                        callback_data="suggestion_"
                        + suggestion,  # Use the entire suggestion as the callback_data
                    )
                )

            # Send the message in Markdown format with the suggestions as buttons in the keyboard
            not_found_message = bot.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

            # Create a thread to delete the user's original message and the not_found_message after a certain delay
            start_thread_to_delete_messages(
                bot,
                message.chat.id,
                [message.message_id, not_found_message.message_id],
                delay=30,  # Set the desired delay in seconds before deleting the messages
            )

        except telebot.apihelper.ApiTelegramException as e:
            # Send a message to the user indicating that suggestions couldn't be provided due to an error
            error_message = f'Sorry,😔\n We couldn\'t get any Series or Movies related to "{search_query.title()}" at the moment.\n Please check your spelling or use the correct search syntax.'
            error_message_obj = bot.send_message(
                chat_id=message.chat.id, text=error_message
            )

            # Select a random not found sticker from the list
            random_sticker_id = random.choice(not_found_stickers)

            # Send the random not found sticker
            sticker_message_obj = bot.send_sticker(
                chat_id=message.chat.id, sticker=random_sticker_id
            )

            # Function to delete a message after a certain delay
            def delete_message_after_delay(message_obj, delay):
                time.sleep(delay)
                try:
                    bot.delete_message(
                        chat_id=message_obj.chat.id, message_id=message_obj.message_id
                    )
                except telebot.apihelper.ApiException:
                    pass  # If the message is already deleted or any other issue occurs, just continue

            # Create threads to delete the error message and not found sticker after 45 seconds
            thread_error_message = threading.Thread(
                target=delete_message_after_delay, args=(error_message_obj, 45)
            )
            thread_sticker_message = threading.Thread(
                target=delete_message_after_delay, args=(sticker_message_obj, 45)
            )
            thread_user_message = threading.Thread(
                target=delete_message_after_delay, args=(message, 45)
            )

            # Start the threads
            thread_error_message.start()
            thread_sticker_message.start()
            thread_user_message.start()

            pass

    else:
        # Store the search results and starting index in the search_progress dictionary
        search_progress[message.chat.id] = {
            "results": results,
            "index": 0,
        }

        # Send the files keyboard
        send_files_keyboard(chat_id, search_query)

        # Function to delete the user's original message after a certain delay
        def delete_original_message_after_delay(chat_id, message_id, delay):
            time.sleep(delay)
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except telebot.apihelper.ApiException:
                pass  # If the message is already deleted or any other issue occurs, just continue

        # Create a thread to delete the user's original message after a certain delay
        thread_delete_original_message = threading.Thread(
            target=delete_original_message_after_delay,
            args=(message.chat.id, message.message_id, 30),
        )

        # Start the thread
        thread_delete_original_message.start()


# The callback query handler to handle suggestions
@bot.callback_query_handler(func=lambda call: call.data.startswith("suggestion_"))
def handle_suggestion_callback(call):
    global first_word_from_suggestion

    # Get the suggestion from the callback data
    suggestion = call.data.replace("suggestion_", "")  # Remove the "suggestion_" prefix

    # Define a regular expression pattern to match years
    year_pattern = r"\b(19|20)\d{2}\b"

    # Extract the first four words before any space or special characters using regular expression and filter out years
    words_from_suggestion = re.findall(r"\w+", suggestion)
    filtered_words = [
        word for word in words_from_suggestion if not re.match(year_pattern, word)
    ]
    first_word_from_suggestion = " ".join(filtered_words[:2])

    # Send a message to the user informing them about the selected suggestion and how to proceed
    message = bot.send_message(
        chat_id=call.message.chat.id,
        text=f"👉 You have selected: <pre><code class='language-text'>{first_word_from_suggestion}</code></pre> ...\n\n💁 Quickly tap on the selected suggestion above ⬆️ and send it to me. I'll get the exclusive results for you!",
        parse_mode="HTML",
    )

    # Delete the suggestion buttons message
    try:
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
    except telebot.apihelper.ApiException:
        pass  # If the message is already deleted or any other issue occurs, just continue

    # Function to delete a message after a certain delay
    def delete_message_after_delay(message, delay):
        time.sleep(delay)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except telebot.apihelper.ApiException:
            pass  # If the message is already deleted or any other issue occurs, just continue

    # Create a thread to delete the message after 20 seconds
    thread_message_deletion = threading.Thread(
        target=delete_message_after_delay, args=(message, 20)
    )
    thread_message_deletion.start()


# Send an inline keyboard with the available files to the user
def send_files_keyboard(chat_id, search_query):
    search_data = search_progress.get(chat_id)
    if search_data:
        results = search_data["results"]
        num_results = len(results)
        page_size = 10  # Number of buttons per page
        current_page = search_data.get("current_page", 0)

        # Calculate the start and end indices for the current page
        start_index = current_page * page_size
        end_index = min((current_page + 1) * page_size, num_results)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)

        for i in range(start_index, end_index):
            file_name, _ = results[i]
            button_text = file_name
            callback_data = f"file_{i}"
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    button_text, callback_data=callback_data
                )
            )

        # Add the "Send All Files" button
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                "📤 Send All Files 📤", callback_data="send_all"
            )
        )

        # Add the current page number and total number of pages at the bottom
        page_number = current_page + 1
        total_pages = (num_results - 1) // page_size + 1
        page_number_text = f"📃 Page {page_number}/{total_pages}"
        page_number_button = telebot.types.InlineKeyboardButton(
            page_number_text, callback_data="page_number"
        )

        # Create a row for the "Previous" and "Next" buttons along with the page number
        row = []

        if current_page > 0:
            row.append(
                telebot.types.InlineKeyboardButton(
                    "⬅️ Previous", callback_data="previous"
                )
            )

        row.append(page_number_button)

        if end_index < num_results:
            row.append(
                telebot.types.InlineKeyboardButton("Next ➡️", callback_data="next")
            )

        # Add the row to the keyboard
        keyboard.row(*row)

        # Include the search query in the message text
        message_text = f"🔎\t Search Query : {search_query.title()} ✅\n\n⚡\t\t{num_results} Search Results Found 😎"

        if "message_id" in search_data:
            # Edit the existing message with updated keyboard and remove the previous keyboard
            try:
                bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=search_data["message_id"],
                    reply_markup=keyboard,
                )
            except telebot.apihelper.ApiException:
                # If the message with the previous keyboard cannot be edited (e.g., if it was deleted), send a new message with the keyboard
                message = bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    reply_markup=keyboard,
                )
                search_data["message_id"] = message.message_id
        else:
            # Send a new message with the keyboard
            message = bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=keyboard,
            )
            search_data["message_id"] = message.message_id

        search_progress[chat_id] = search_data


# Handle button callback for sending the selected file or all files
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("file_")
    or call.data == "send_all"
    or call.data == "previous"
    or call.data == "next"
)
def handle_file_callback(callback_query):
    chat_id = callback_query.message.chat.id
    search_data = search_progress.get(chat_id)

    if search_data:
        results = search_data["results"]
        current_page = search_data.get("current_page", 0)
        num_pages = (len(results) - 1) // 10  # Calculate the total number of pages

        if callback_query.data == "send_all":
            send_selected_file(
                chat_id, None, None, search_data.get("search_query", ""), send_all=True
            )
        elif callback_query.data == "previous":
            current_page = max(current_page - 1, 0)
            search_data["current_page"] = current_page
            search_progress[chat_id] = search_data
            send_files_keyboard(chat_id, search_data.get("search_query", ""))
        elif callback_query.data == "next":
            current_page = min(current_page + 1, num_pages)
            search_data["current_page"] = current_page
            search_progress[chat_id] = search_data
            send_files_keyboard(chat_id, search_data.get("search_query", ""))
        else:
            index = int(callback_query.data.split("_")[1])
            file_name, file_id = results[index]
            send_selected_file(
                chat_id, file_name, file_id, search_data.get("search_query", "")
            )


# Send the selected file or all files to the user
def send_selected_file(
    chat_id,
    file_name,
    file_id,
    search_query="",
    send_all=False,
    continue_message_id=None,
):
    # Create a dictionary to store sent documents' message IDs and their timestamps
    sent_documents = {}
    sent_selected_files = {}

    try:
        if not send_all:
            # Send the selected file
            # Modify the caption
            caption = re.sub(r"\s+|[,.\[\]_]", ".", file_name)
            caption = re.sub(
                r"\.+", ".", caption
            )  # Replace multiple periods with a single period
            caption = caption.strip(".")  # Remove leading/trailing periods

            # Send the document and store the message object
            sent_document = bot.send_document(
                chat_id=chat_id, document=file_id, caption=caption
            )

            # Store the sent document's message ID and timestamp
            sent_selected_files[sent_document.message_id] = time.time()

            # Create a thread to delete the file after 40 seconds
            def delete_after_40s(message_id):
                time.sleep(120)
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                except telebot.apihelper.ApiException:
                    pass  # If the message was already deleted by the user, just continue

            thread = threading.Thread(
                target=delete_after_40s, args=(sent_document.message_id,)
            )
            thread.start()

        else:
            # Send all files
            search_data = search_progress.get(chat_id)
            if search_data:
                results = search_data["results"]
                index = search_data.get("index", 0)
                num_results = len(results)

                while index < num_results and index < search_data["index"] + 10:
                    round_results = results[index : index + 10]

                    for round_file_name, round_file_id in round_results:
                        # Modify the caption
                        round_caption = re.sub(r"\s+|[,.\[\]_]", ".", round_file_name)
                        round_caption = re.sub(
                            r"\.+", ".", round_caption
                        )  # Replace multiple periods with a single period
                        round_caption = round_caption.strip(
                            "."
                        )  # Remove leading/trailing periods

                        # Send the document and store the message object
                        sent_document = bot.send_document(
                            chat_id=chat_id,
                            document=round_file_id,
                            caption=round_caption,
                        )

                        # Store the sent document's message ID and timestamp
                        sent_documents[sent_document.message_id] = time.time()

                    index += 10

                # Start a new thread to delete documents older than 45 seconds
                delete_thread = threading.Thread(
                    target=delete_documents_thread, args=(chat_id, sent_documents)
                )
                delete_thread.start()

                # Delete the continue message if it exists
                if continue_message_id:
                    bot.delete_message(chat_id=chat_id, message_id=continue_message_id)
                    continue_message_id = None

                # Update the index in the search_progress dictionary
                search_data["index"] = index
                search_progress[chat_id] = search_data

                # Check if there are more files to send
                if index < num_results:
                    # Send continue message
                    continue_message = bot.send_message(
                        chat_id=chat_id,
                        text="Sending paused. Tap 'Continue' to receive the next set of files.",
                        reply_markup=telebot.types.InlineKeyboardMarkup().add(
                            telebot.types.InlineKeyboardButton(
                                "Continue", callback_data="continue"
                            )
                        ),
                    )
                    continue_message_id = continue_message.message_id

                else:
                    # Delete the keyboard markup
                    try:
                        # Delete the keyboard markup and the message showing how many results were found
                        if "message_id" in search_data:
                            bot.delete_message(
                                chat_id=chat_id, message_id=search_data["message_id"]
                            )
                            del search_data["message_id"]

                        # Delete the message showing the number of results
                        bot.delete_message(
                            chat_id=chat_id, message_id=continue_message_id
                        )
                    except telebot.apihelper.ApiException:
                        pass  # If the message was already deleted by the user, just continue

                    # All files have been sent
                    random_sticker_id = random.choice(sticker_ids)
                    sent_sticker = bot.send_sticker(
                        chat_id=chat_id, sticker=random_sticker_id
                    )

                    # Function to delete the sticker after a certain delay
                    def delete_sticker_after_delay(chat_id, sticker_message_id, delay):
                        time.sleep(delay)
                        try:
                            bot.delete_message(
                                chat_id=chat_id, message_id=sticker_message_id
                            )
                        except telebot.apihelper.ApiException:
                            pass  # If the message is already deleted or any other issue occurs, just continue

                    # Create a thread to delete the sticker after a certain delay
                    thread_delete_sticker = threading.Thread(
                        target=delete_sticker_after_delay,
                        args=(chat_id, sent_sticker.message_id, 45),
                    )

                    # Start the thread
                    thread_delete_sticker.start()

    except Exception as e:
        print(f"Error: Unable to send the file. {str(e)}")


# Function to delete the sent batch documumentz
def delete_documents_thread(chat_id, sent_documents):
    while True:
        time.sleep(
            2
        )  # Wait for a short interval (e.g., 2 seconds) before checking again

        # Get the current time
        current_time = time.time()

        # List to store message IDs of documents to delete
        messages_to_delete = []

        # Check if any documents are older than 45 seconds
        for message_id, timestamp in sent_documents.items():
            if current_time - timestamp >= 300:
                messages_to_delete.append(message_id)

        # Delete the documents
        for message_id in messages_to_delete:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except telebot.apihelper.ApiException:
                pass  # If the message was already deleted by the user, just continue

        # Remove deleted documents from the dictionary
        sent_documents = {
            message_id: timestamp
            for message_id, timestamp in sent_documents.items()
            if message_id not in messages_to_delete
        }


# Handle button callback for continuing file sending
@bot.callback_query_handler(func=lambda call: call.data == "continue")
def handle_continue_callback(callback_query):
    chat_id = callback_query.message.chat.id
    search_data = search_progress.get(chat_id)

    if search_data:
        continue_message_id = (
            callback_query.message.message_id
        )  # Get the ID of the continue message
        try:
            bot.delete_message(chat_id=chat_id, message_id=continue_message_id)
        except telebot.apihelper.ApiException as e:
            pass

        send_selected_file(chat_id, None, None, send_all=True)


# Run the bot
while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Error: Unable to run the bot. {str(e)}")
