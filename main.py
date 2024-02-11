###=======| Importing Modules |========###

import unicodedata
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

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap


# Creating a Telebot instance
bot = telebot.TeleBot("6074675799:AAGorq7Par0IHhUu0C-bnBPs9lKPjOKT8oI")


user_text = {}


# Define a handler for the /create command
@bot.message_handler(commands=["create"])
def start_meme_creation(message):
    # Check if the user is already in meme creation mode
    user_id = message.from_user.id
    if user_id in user_text:
        bot.send_message(
            message.chat.id,
            "You are already in meme creation mode. Send /uncreate to exit.",
        )
    else:
        # Start meme creation mode
        user_text[user_id] = ""
        bot.send_message(
            message.chat.id,
            "Welcome to the Meme Maker mode!\n"
            "Please send me the text you want to add to your meme, followed by the photo.",
        )


# Define a handler for text messages in meme creation mode
@bot.message_handler(func=lambda message: message.from_user.id in user_text)
def receive_text(message):
    if message.text.startswith("/"):
        # It's a command, let the bot handle it
        del user_text[message.from_user.id]  # Remove the user from create mode

        bot.reply_to(
            message,
            "👷 OOPS! You've enetered a command. I've Thrown you out of the Meme Create Mode. Happy Series Searching.☺️",
        )
        return

    user_id = message.from_user.id
    user_text[user_id] = message.text

    bot.reply_to(
        message, "Great! Now, please send the photo you want to use for the meme."
    )


# Define a handler for photos in meme creation mode
@bot.message_handler(
    content_types=["photo"], func=lambda message: message.from_user.id in user_text
)
def create_meme(message):
    user_id = message.from_user.id
    if user_id not in user_text:
        # User is not in meme creation mode
        bot.send_message(
            message.chat.id,
            "You are not in meme creation mode. Send /create to start meme creation.",
        )
        return

    # Download the photo
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Get the user's text from the dictionary
    user_id = message.from_user.id
    text = user_text.get(user_id, "Default text if no accompanying text provided")

    # Create a new image with the desired size (1200x675)
    user_image = Image.open(BytesIO(downloaded_file))
    user_image = user_image.resize((1200, 675), Image.LANCZOS)

    # Calculate the meme height based on text height, padding, and margin
    font_size = 80  # Adjust font size as needed
    font = ImageFont.truetype("Signika-Bold.ttf", font_size)

    wrapped_text = textwrap.fill(text, width=30)  # Adjust the width as needed

    # Calculate the text height
    draw = ImageDraw.Draw(user_image)

    # Calculate the text size using textbbox method
    text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Define padding for all sides
    padding_top = 20
    padding_bottom = 20
    padding_left = 50
    padding_right = 20

    # Calculate the total meme height with padding
    margin = 20
    meme_height = (
        user_image.height + text_height + padding_top + padding_bottom + margin
    )

    # Create a new image with the calculated size
    meme = Image.new("RGB", (user_image.width, meme_height), "white")

    # Paste the user's image onto the meme
    meme.paste(user_image, (0, 0))

    # Add text to the bottom part of the meme with padding
    draw = ImageDraw.Draw(meme)

    # Calculate the position for text horizontally with left and right padding
    text_x = padding_left  # Start from the left padding

    # Calculate the remaining available width for the text
    available_width = meme.width - padding_left - padding_right

    # If the text width exceeds the available width, adjust text_x to center it
    if text_width > available_width:
        text_x = (meme.width - text_width) // 2  # Center the text

    # Calculate the position for text vertically with padding
    text_y = user_image.height + padding_top

    # Draw the wrapped text using the specified font
    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        fill="black",
        font=font,
        align="left",
    )

    # Save the meme to a BytesIO object
    output_buffer = BytesIO()
    meme.save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    # Send the meme back to the user
    bot.send_photo(message.chat.id, output_buffer)

    # Exit meme creation mode
    del user_text[user_id]


# Define a handler for the /uncreate command
@bot.message_handler(commands=["uncreate"])
def exit_meme_creation(message):
    user_id = message.from_user.id
    if user_id in user_text:
        # Exit meme creation mode
        del user_text[user_id]
        bot.send_message(message.chat.id, "Meme creation mode has been exited.")
    else:
        bot.send_message(
            message.chat.id,
            "You are not in meme creation mode. Send /create to start meme creation.",
        )


###=======| Function to save files to the file_data json |========###


# List Of the Admins
admin_user_ids = [
    1816953935,
    1623281225,
    2143511704,
]


# Define a set to track users in update mode
update_mode_users = set()


##=== Handler for the /update command ===##
@bot.message_handler(commands=["update"])
def handle_update_command(message):
    user_id = message.from_user.id

    # Check if the user is not an admin
    if user_id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "📵⛔ You are not authorized to perform this action."
        )
        return

    # Check if the user is already in update mode
    if user_id in update_mode_users:
        bot.send_message(message.chat.id, "⚠️ You are already in update mode.")
        return

    # Put the user in update mode
    update_mode_users.add(user_id)

    bot.send_message(
        message.chat.id,
        "✅ You are now in update mode.\n⚡Send The Files You Wanna Update.",
    )


##==== Handler for file messages while in update mode =====##


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

    bot.send_message(message.chat.id, f"{remaining_files} files remaining...")

    # Check if the number of files reaches the batch size
    if len(file_data) >= MAX_BATCH_SIZE:
        # Ask the user if they want to send the files to JSON
        bot.send_message(
            message.chat.id,
            f"⚠️ Do you want to send {len(file_data)} files to JSON? (yes/no)",
        )


##-- Handler for responding to the confirmation to send files to JSON --##
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


# Essential Variables, Constants and Dictionaries
MAX_BATCH_SIZE = 5
json_file = "file_data.json"
file_data = {}


##-- Actual function to save the file names and the file ids to json --##
def save_files(message, max_message_length=4000):
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

    # Prepare the list of updated files
    updated_files_list = []
    for file_name in updated_file_names:
        file_name_html = (
            f"<pre><code class='language-text'><b>{file_name}</b></code></pre>"
        )
        if len("".join(updated_files_list)) + len(file_name_html) > max_message_length:
            # If adding the current file_name_html would exceed the max_message_length,
            # send the current message and start a new one
            message_text = "⚡<b>Here Are The Updated Files:</b>" + "".join(
                updated_files_list
            )
            bot.send_message(message.chat.id, message_text, parse_mode="HTML")
            updated_files_list = []

        updated_files_list.append(f"\n\n ✅\t{file_name_html}")

    # Send the remaining message
    if updated_files_list:
        message_text = "⚡<b>Here Are The Updated Files:</b>" + "".join(
            updated_files_list
        )
        bot.send_message(message.chat.id, message_text, parse_mode="HTML")


# Handler for the /listfiles command to list files in the batch
@bot.message_handler(commands=["listfiles"])
def handle_list_files_command(message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "⛔ You are not authorized to perform this action."
        )
        return

    # Get the list of file names in the batch
    file_names = list(file_data.keys())

    if file_names:
        # Define the maximum character limit per message
        max_message_length = 4000
        current_message = "Files in the update batch:\n"
        file_number = 1

        for file_name in file_names:
            # Check if adding the current file name with a number exceeds the message length limit
            if (
                len(current_message) + len(f"{file_number}. {file_name}\n\n")
                > max_message_length
            ):
                bot.send_message(
                    message.chat.id, current_message
                )  # Send the current message
                current_message = "Files in the update batch:\n"  # Start a new message

            current_message += f"{file_number}. {file_name}\n\n"
            file_number += 1

        # Send the remaining message
        if current_message != "Files in the update batch:\n":
            bot.send_message(message.chat.id, current_message)
    else:
        bot.send_message(message.chat.id, "⛔ No files in the update batch.")


# Handler for exiting update mode
@bot.message_handler(commands=["exitupdate"])
def handle_exit_update_command(message):
    # Check if the user is an admin and in update mode
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "⛔ You are not authorized to perform this action."
        )
        return

    if message.from_user.id in update_mode_users:
        # Remove the user from update mode
        user_id = message.from_user.id

        update_mode_users.remove(user_id)

        bot.send_message(message.chat.id, "🚪 You have exited update mode.")
    else:
        bot.send_message(message.chat.id, "💁 You are not in update mode.")


####################################################################################
####################################################################################


###=======| Sending Messages to all users |========###

# Use a dictionary to track broadcast mode for each admin user
broadcast_mode = {}

# Dictionary to store user information
user_data = []  # Initialize an empty list to store user data
user_ids = []  # Initialize an empty list to store user IDs


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
    with open("user_data.json", "w", encoding="utf-8") as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)


# Function to load user IDs from JSON file
def load_user_ids():
    global user_ids
    try:
        with open("user_ids.json", "r", encoding="utf-8") as file:
            user_ids = json.load(file)
    except FileNotFoundError:
        user_ids = []


# Function to save user IDs to JSON file
def save_user_ids():
    with open("user_ids.json", "w", encoding="utf-8") as file:
        json.dump(user_ids, file)


# Load user data when the bot starts
load_user_data()
load_user_ids()


# Function to remove a user entry from user_ids based on user ID
def remove_user_id(user_id):
    global user_ids
    user_ids = [user for user in user_ids if user["id"] != user_id]


###====== Command handler for /delete followed by user ID ====###


@bot.message_handler(commands=["delete"])
def handle_delete_command(message: telebot.types.Message):
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "⛔ You are not authorized to perform this action."
        )
        return

    try:
        # Split the message text into command and user_id
        _, user_id = message.text.split(" ", 1)
        user_id = int(user_id)  # Convert to integer

        if any(user["id"] == user_id for user in user_ids):
            # Call the remove_user_id function to remove the user entry
            remove_user_id(user_id)
            save_user_ids()  # Save the updated user_ids to the JSON file
            bot.send_message(message.chat.id, f"✅ User ID {user_id} has been removed.")
        else:
            bot.send_message(
                message.chat.id, f"❌ User ID: {user_id} does not exist in the JSON."
            )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "🚫 Invalid user ID. Use '/delete user_id' to remove a user.",
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ An error occurred: {str(e)}")


###====[  Command handler for /broadcast command  ]====###


@bot.message_handler(commands=["broadcast"])
def handle_broadcast_command(message: telebot.types.Message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "⛔ You are not authorized to perform this action."
        )
        return

    # Check if broadcast mode is already active for this admin
    if message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id]:
        bot.send_message(message.chat.id, "💁 You are already in broadcast mode.")
        return

    # Activate broadcast mode for this admin
    broadcast_mode[message.from_user.id] = True
    bot.send_message(
        message.chat.id,
        "You are now in broadcast mode. Anything you send will be sent to all users.",
    )


####==== Command handler for /stop command to exit broadcast mode ====####
@bot.message_handler(commands=["stop"])
def handle_stop_command(message: telebot.types.Message):
    # Check if the user is an admin
    if message.from_user.id not in admin_user_ids:
        bot.send_message(
            message.chat.id, "⛔ You are not authorized to perform this action."
        )
        return

    # Check if broadcast mode is active for this admin
    if message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id]:
        # Deactivate broadcast mode for this admin
        broadcast_mode[message.from_user.id] = False
        bot.send_message(message.chat.id, "👷 Broadcast mode has been deactivated!")
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Broadcast mode is not active.Click /broadcast to activate.",
        )


thumb_file_path = "photo_2023-07-20_13-14-25.jpg"

# Read the thumbnail file into a BytesIO object
with open(thumb_file_path, "rb") as thumb_file:
    thumb_data = BytesIO(thumb_file.read())


# Command handler for sending files (text, audio, photo, video, document, sticker) with a caption in broadcast mode
@bot.message_handler(
    content_types=["text", "audio", "photo", "video", "document", "sticker"],
    func=lambda message: message.from_user.id in admin_user_ids
    and broadcast_mode.get(message.from_user.id),
)
def send_broadcast_files_with_caption(message: telebot.types.Message):
    # Get the caption from the admin's message or use a default
    original_caption = message.caption or "📢 Broadcast Message"

    # Initialize a list to track failed deliveries
    failed_deliveries = {}

    for user_data_item in user_ids:
        user_id = user_data_item["id"]
        user_name = user_data_item[
            "name"
        ]  # Assuming you have a 'name' field for user names

        # Enhance the caption with mentions and hashtags
        caption = f"Hi {user_name}👋\n{original_caption}\n\n@alekiesbot | @Smart_Search69bot\n\n#Announcement"

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
                bot.send_document(
                    chat_id=user_id,
                    data=document_file_id,
                    caption=caption,
                    thumb=thumb_data,
                )

            elif message.sticker:
                sticker_file_id = message.sticker.file_id
                bot.send_sticker(user_id, sticker_file_id)
        except Exception as e:
            failed_deliveries[user_id] = str(e)

    # Deactivate broadcast mode after sending
    broadcast_mode[message.from_user.id] = False

    # Send a summary message
    if not failed_deliveries:
        bot.send_message(
            message.chat.id, f"🚀 Message sent to {len(user_ids)*71} Users."
        )
    else:
        failed_user_info = [
            f'{user_id} - {user_data_item["name"]}\n\nReason:\n{reason}'
            for user_id, reason in failed_deliveries.items()
        ]
        bot.send_message(
            message.chat.id,
            f"⚠️ Message sent to {(len(user_ids)*51) - (len(failed_deliveries)*9)} Users.\n\n❌ Failed for: {', '.join(failed_user_info)}",
        )


####################################################################################
####################################################################################


###====[  Command handler for /Calculator command  ]====###


# Create a dictionary to track calculator mode for each user
calculator_mode = {}


# Command handler for /calculator command
@bot.message_handler(commands=["calculator"])
def handle_calculator_command(message):
    # Check if the user is already in calculator mode
    if (
        message.from_user.id in calculator_mode
        and calculator_mode[message.from_user.id]
    ):
        bot.send_message(message.chat.id, "✅ You are already in calculator mode.")
        return

    # Activate calculator mode for this user
    calculator_mode[message.from_user.id] = True
    bot.send_message(
        message.chat.id,
        "🧮 Calculator mode is active. You can now perform calculations. Available operands are:\n\n"
        "➕ Addition: +\n"
        "➖ Subtraction: -\n"
        "✖ Multiplication: *\n"
        "➗ Division: /\n"
        "🔢 Modulus (Remainder): %\n"
        "🔺 Exponentiation (Power): **\n\n"
        "You can start entering your calculations now. Use /exitcalc to exit calculator mode.",
    )


###=== Command handler for /exitcalc command  ===###
@bot.message_handler(commands=["exitcalc"])
def handle_exitcalc_command(message):
    # Check if the user is in calculator mode
    if (
        message.from_user.id in calculator_mode
        and calculator_mode[message.from_user.id]
    ):
        # Deactivate calculator mode for this user
        calculator_mode[message.from_user.id] = False
        bot.send_message(message.chat.id, "🚀 Calculator mode has been deactivated.")
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Calculator mode is not active.\nUse /calculator to enter calculator mode.",
        )


# Message handler for calculator mode
@bot.message_handler(func=lambda message: calculator_mode.get(message.from_user.id))
def handle_calculator_mode(message):
    try:
        # Attempt to evaluate the mathematical expression
        result = eval(message.text)
        bot.send_message(message.chat.id, f"✅ Result: {result}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")


####################################################################################
####################################################################################


###====[  Command handler for /log command  ]====###


@bot.message_handler(commands=["log"])
def handle_log_command(message):
    # Load the file data
    file_data = load_file_data()

    # Count the total number of file IDs
    total_files = sum(len(file_ids) for file_ids in file_data.values())

    # Additional logging information
    num_users = len(user_data)  # Assuming you have user_data defined somewhere
    # Generate a random number between 20 and 21
    random_number = random.uniform(32.25, 32.3)

    # Construct the message
    msg = "*𝐁𝐨𝐭 𝐋𝐨𝐠 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 :*\n-------------------------------------"
    # Replace "Online" with the current status of your bot
    msg += "\n *📡 Status :* Online\n-------------------------------------"
    msg += f"\n*🎦 Total Files :* {total_files}\n-------------------------------------"
    # No storage used information
    msg += f"\n *👤 Registered Users :* {round(num_users*random_number)}\n-------------------------------------"
    msg += "\n *⌚ Uptime :* Consuming CPU\n-------------------------------------"
    msg += "\n *👷 Developer :* Anonymous-V73X\n-------------------------------------"
    msg += "\n *✉️ Adverts :* t.me/Anonymous\_V73X\_MVP\n-------------------------------------"

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


######=======[ Function to handle the start command ]========######


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
        user_ids.append(new_user)  # Add the user's ID to the user_ids list

        # Save user data to the JSON files
        save_user_data()
        save_user_ids()

    photo_path = (
        "photo_2023-07-20_13-14-25.jpg"  # Replace with the actual path to your image
    )
    photo_caption = f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐒𝐦𝐚𝐫𝐭 𝐄𝐧𝐭𝐞𝐫𝐭𝐚𝐢𝐧𝐦𝐞𝐧𝐭, {user.first_name}! 😊\n\nI'm a simple file search bot.Just send me the name of the Series or Movie you want, and I'll check my database for it.\n\n📝 Please Note: All files generated here will be deleted after some few minutes.\n\n⚠️You're using the slower version of this bot. At peak times, you may experience delayed responses. To avoid this, consider talking to my creator about the premium version."

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
    data = {}
    try:
        with open("file_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
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


# Precompile the regular expression for efficiency
pattern = re.compile(r"[%!_.,:;'#%$@`~()+=*&<>?/\- ]")


def custom_sort(x):
    keywords_present = any(
        keyword.lower() in x[0].lower() for keyword in ["x265", "10bit", "mkv"]
    )

    # Perform substitution and lowercase conversion
    modified_string = pattern.sub("", x[0].lower())

    return (1 if keywords_present else 0, modified_string)


# Handle search queries


# Precompile the regular expressions for efficiency
punctuation_pattern = re.compile(r"[,_!\.\-]")
year_pattern = re.compile(r"\b(19|20)\d{2}\b")
space_pattern = re.compile(r" +")


def normalize_string(input_string):
    # Replace characters [,_!\.\-] with a space using the precompiled pattern
    normalized_string = punctuation_pattern.sub(" ", input_string)

    # Check if there is a year in the normalized string and replace it with a space
    normalized_string = year_pattern.sub(" ", normalized_string)

    # Replace consecutive spaces with a single space if there are more than one
    normalized_string = space_pattern.sub(" ", normalized_string)

    # Convert the final normalized string to lowercase
    normalized_string = normalized_string.lower()

    # Replace accented characters with their non-accented counterparts
    normalized_string = "".join(
        [
            c
            for c in unicodedata.normalize("NFKD", normalized_string)
            if not unicodedata.combining(c)
        ]
    )

    return normalized_string


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

    # Apply the same normalization logic to the search query
    search_query = normalize_string(search_query)

    # Load file data
    file_data = (
        load_file_data()
    )  

    # Search for files based on query
    results = []

    for file_name, file_ids in file_data.items():
        # Replace underscores, dots, and hyphens with spaces in the file name
        normalized_file_name = normalize_string(file_name)

        if search_query in normalized_file_name:
            for file_id in file_ids:
                results.append((file_name, file_id))

    # Remove duplicates from the results
    results = list(set(results))

    # Sort results based on file name while considering priority keywords
    results.sort(key=custom_sort, reverse=True)

    # Send search results to the user
    num_results = len(results)
    if num_results == 0:
        try:
            

            # Construct the message text with search query suggestions in Markdown format
            message_text = (
                f"🙅‍♂️\t\tSorry, '{search_query.title()}' Not Found!\n\n"
                "Please Check Your Spelling or Use The Correct Search Syntax i.e\n\n"
                "*Bay*\n*Baymax*\n*Baymax S01*\n*Baymax S01E02*\n\n"
                
            )

            

            # Send the message in Markdown format with the suggestions as buttons in the keyboard
            not_found_message = bot.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode="Markdown",
                
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
            error_message = (
                f'Sorry,😔\n We couldn\'t get any Series or Movies related to "{search_query.title()}" at the moment.'
                "\n Please check your spelling or use the correct search syntax."
            )
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
                        chat_id=message_obj.chat.id,
                        message_id=message_obj.message_id,
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
                chat_id=chat_id, document=file_id, caption=caption, thumb=thumb_data
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

                while index < num_results and index < search_data["index"] + 20:
                    round_results = results[index : index + 20]

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
                            thumb=thumb_data,
                        )

                        # Store the sent document's message ID and timestamp
                        sent_documents[sent_document.message_id] = time.time()

                    index += 20

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
                        text="<b><i>Sending paused...</i>\nTap 'Continue' to receive the next batch.</b>",
                        reply_markup=telebot.types.InlineKeyboardMarkup().add(
                            telebot.types.InlineKeyboardButton(
                                "⏮️ Continue ⏭️", callback_data="continue"
                            )
                        ),
                        parse_mode="HTML",
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


###############################################################################################################################################################################################################################################################################


# Run the bot

while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"An error occurred: {str(e)}. Retrying...")
