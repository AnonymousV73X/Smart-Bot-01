import telebot
import json
import re
import random
from jokes import jokes


# Create a Telebot instance
bot = telebot.TeleBot("6074675799:AAGorq7Par0IHhUu0C-bnBPs9lKPjOKT8oI")

# Create a dictionary to keep track of the user's search progress
search_progress = {}

# Define a list of sticker IDs
sticker_ids = [
    "CAACAgIAAxkBAAJ9nmS4PZw0mMONTT09ES3bTqkf5jELAALiBQACP5XMCnNlX6_emGTgLwQ",
    "CAACAgIAAxkBAAJ9c2S4O6cs9pH8KN7yhrDl7640xlcgAAIUBwACRvusBO7y0rmZcxR1LwQ",
    "CAACAgIAAxkBAAJ9dGS4O8sBCb3pcCdJvyahBA4_HJsZAAJZDgADLiFLVN-fb7SfsrwvBA",
    "CAACAgEAAxkBAAJ9dWS4O_IxnK7nMk9Ceq90E-PREv-IAALrAQACOA6CEbOGBM7hnEk5LwQ",
    "CAACAgIAAxkBAAJ9dmS4PB75fyCW_dvPGXUWpnCbSKfiAAJGAANSiZEj-P7l5ArVCh0vBA",
    "CAACAgUAAxkBAAJ9d2S4PD0lrqkRasfwS6-HWLTAgEF-AALEAgACBG2gVsF1Ng9n9CrHLwQ",
    "CAACAgIAAxkBAAJ9eGS4PHXzaXTvfOC1Cj5jrwruPr2WAAIsAQAC9wLID6abwCn6K4ldLwQ",
    "CAACAgIAAxkBAAJ9emS4PKd04AO7szmXcfv8CysxsJLAAAIoAQACUomRIxpSPL-bbi9uLwQ",
    "CAACAgIAAxkBAAJ9nmS4PZw0mMONTT09ES3bTqkf5jELAALiBQACP5XMCnNlX6_emGTgLwQ",
]


def limit_search_query_length(search_query, max_length):
    if len(search_query) > max_length:
        # Truncate the search query to the specified max length
        limited_search_query = search_query[:max_length]
        # Remove any incomplete words at the end of the truncated search query
        limited_search_query = limited_search_query.rsplit(" ", 1)[0]
        return limited_search_query
    return search_query


@bot.message_handler(commands=["start"])
def welcome(message):
    user = message.from_user

    photo_path = (
        "photo_2023-07-20_13-14-25.jpg"  # Replace with the actual path to your image
    )
    photo_caption = f"Welcome to Smart Entertainment, {user.first_name}! 😊\n\nI'm a simple file search bot. Send me the name of a Series or Movie, and I'll check my database for it."  # Caption for the image
    button_text = "Inline Search"  # Text for the button

    # Send the photo with caption and the inline keyboard
    bot.send_photo(
        chat_id=message.chat.id,
        photo=open(photo_path, "rb"),
        caption=photo_caption,
        reply_markup=create_button(button_text),
    )


@bot.message_handler(commands=["alive"])
def alive(message):
    user = message.from_user
    # Randomly select a joke from the array
    joke = random.choice(jokes)

    caption = f"Of Course I'm Alive, {user.first_name}! 😊\n\n {joke}\n\n Jokes aside 😁 What Series can I get you?"
    photo_path = (
        "photo_2023-07-20_13-15-28.jpg"  # Replace with the actual path to your image
    )

    # Send the photo with caption (without the button)
    bot.send_photo(
        chat_id=message.chat.id,
        photo=open(photo_path, "rb"),
        caption=caption,
    )


# Function to create a simple inline keyboard with a button
def create_button(button_text):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button = telebot.types.InlineKeyboardButton(
        button_text, callback_data="button_clicked"
    )
    keyboard.add(button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data == "button_clicked")
def handle_button_click(callback_query):
    # Get the chat ID and message ID to reply to the callback query
    chat_id = callback_query.message.chat.id
    # Show a pop-up to the user
    bot.answer_callback_query(
        callback_query_id=callback_query.id, text="Button Clicked!"
    )


# Load file data from JSON
def load_file_data():
    try:
        with open("file_data.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data


# Handle search queries
@bot.message_handler(func=lambda message: True)
def handle_search(message):
    search_query = message.text.lower()

    search_query = limit_search_query_length(search_query, max_length=100)

    # Replace commas, underscores, exclamation marks, and full stops with spaces
    search_query = re.sub(r"[,_!\.\-]", " ", search_query)

    # Load file data
    file_data = load_file_data()

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
        if "   " in normalized_file_name:
            normalized_file_name = normalized_file_name.replace("   ", " ")

        if "  " in normalized_file_name:
            normalized_file_name = normalized_file_name.replace("  ", " ")

        if search_query in normalized_file_name:
            for file_id in file_ids:
                results.append((file_name, file_id))

    # Remove duplicates from the results
    results = list(set(results))

    # Sort results based on file name while ignoring special characters and spaces
    results = sorted(
        results, key=lambda x: re.sub(r"[%!_.\- ]", "", x[0]).lower(), reverse=True
    )

    # Send search results to user
    num_results = len(results)
    if num_results == 0:
        # Construct the message text with search query suggestions in Markdown format
        message_text = f"🙅‍♂️\t\tSorry, '{search_query.title()}' Not Found!\n\nPlease Check Your Spelling or Use The Correct Search Syntax i.e \n*Baymax*\n*Baymax S01*\n*Baymax S01E02*"

        # Send the message in Markdown format
        bot.send_message(
            chat_id=message.chat.id, text=message_text, parse_mode="Markdown"
        )

    else:
        search_progress[message.chat.id] = {
            "results": results,
            "index": 0,
        }  # Store the search results and starting index in the search_progress dictionary
        send_files_keyboard(message.chat.id)


# Send an inline keyboard with the available files to the user
def send_files_keyboard(chat_id):
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

        message_text = f"🔎\t\t{num_results} Search Results Found 😎: "

        if "message_id" in search_data:
            # Edit the existing message with updated keyboard
            bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=search_data["message_id"],
                reply_markup=keyboard,
            )
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
            send_selected_file(chat_id, None, None, send_all=True)
        elif callback_query.data == "previous":
            current_page = max(current_page - 1, 0)
            search_data["current_page"] = current_page
            search_progress[chat_id] = search_data
            send_files_keyboard(chat_id)
        elif callback_query.data == "next":
            current_page = min(current_page + 1, num_pages)
            search_data["current_page"] = current_page
            search_progress[chat_id] = search_data
            send_files_keyboard(chat_id)
        else:
            index = int(callback_query.data.split("_")[1])
            file_name, file_id = results[index]
            send_selected_file(chat_id, file_name, file_id)


# Send the selected file or all files to the user
def send_selected_file(
    chat_id, file_name, file_id, send_all=False, continue_message_id=None
):
    try:
        if not send_all:
            # Send the selected file
            # Modify the caption
            caption = re.sub(r"\s+|[,.\[\]_]", ".", file_name)
            caption = re.sub(
                r"\.+", ".", caption
            )  # Replace multiple periods with a single period
            caption = caption.strip(".")  # Remove leading/trailing periods

            bot.send_document(chat_id=chat_id, document=file_id, caption=caption)
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

                        bot.send_document(
                            chat_id=chat_id,
                            document=round_file_id,
                            caption=round_caption,
                        )

                    index += 10

                    # Delete the continue message if it exists
                    if continue_message_id:
                        bot.delete_message(
                            chat_id=chat_id, message_id=continue_message_id
                        )
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
                    if "message_id" in search_data:
                        bot.edit_message_reply_markup(
                            chat_id=chat_id,
                            message_id=search_data["message_id"],
                            reply_markup=None,
                        )
                        del search_data["message_id"]
                    # All files have been sent
                    random_sticker_id = random.choice(sticker_ids)
                    bot.send_sticker(chat_id=chat_id, sticker=random_sticker_id)

    except Exception as e:
        print(f"Error: Unable to send the file. {str(e)}")


# Handle button callback for continuing file sending
@bot.callback_query_handler(func=lambda call: call.data == "continue")
def handle_continue_callback(callback_query):
    chat_id = callback_query.message.chat.id
    search_data = search_progress.get(chat_id)

    if search_data:
        continue_message_id = (
            callback_query.message.message_id
        )  # Get the ID of the continue message
        bot.delete_message(
            chat_id=chat_id, message_id=continue_message_id
        )  # Delete the continue message
        send_selected_file(chat_id, None, None, send_all=True)


# Handle button callback for sending the selected file or all files
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("file_") or call.data == "send_all"
)
def handle_file_callback(callback_query):
    chat_id = callback_query.message.chat.id
    search_data = search_progress.get(chat_id)

    if search_data:
        results = search_data["results"]
        index = (
            int(callback_query.data.split("_")[1])
            if callback_query.data.startswith("file_")
            else None
        )

        if callback_query.data == "send_all":
            send_selected_file(chat_id, None, None, send_all=True)

        else:
            file_name, file_id = results[index]
            send_selected_file(chat_id, file_name, file_id)


# Run the bot
while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Error: Unable to run the bot. {str(e)}")
