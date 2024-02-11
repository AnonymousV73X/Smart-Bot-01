import telebot
import json
import re
import random
from jokes import jokes
import time
import threading
from difflib import SequenceMatcher


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
    "CAACAgIAAxkBAAKeomS7lUciGWGOgIyOVYB1MWiwNQknAALuFAAC41VQSThLiq0CE2G8LwQ",
    "CAACAgIAAxkBAAKepWS7le-C9MRT5hcxpmcFtk8PNICuAAI_FgACzP64SpLMhLQUJjbpLwQ",
]

not_found_stickers = [
    "CAACAgIAAxkBAAKeo2S7laTyntXOsPsqOxKztakS9cL2AAJiFQACfZpQSbTG3o8XjtAyLwQ",
    "CAACAgIAAxkBAAKepGS7lcvlNdFWU4OW1AFKPVfdWAGPAAKgFwAC37QgSSCArCK7IMbJLwQ",
    "CAACAgIAAxkBAAKermS7lopXgaM-oW3rfDLVz5MLDlCuAALnCgACTQ8ISfqT241rZLjtLwQ",
    "CAACAgIAAxkBAAKer2S7lqTB7RRDAAEc17SKstv2uLk_mgAC5xMAAoQ4cElqKsK5hR_0gC8E",
    "CAACAgIAAxkBAAKesmS7lswysMiop1T02QJXzxBPvxt6AAJ4FQAC10xwSZU-kJWavP47LwQ",
    "CAACAgIAAxkBAAKes2S7lvzwI3ZYgi3gSjMRTEm0PgfJAAKDGAACXuk4SVhqIE0ojg7uLwQ",
]

hello_stickers = [
    "CAACAgIAAxkBAAKepmS7ljuaEfYSY9WSTnxNXxtcUeIwAAKsEwACOJ4hS9HIZVrp3vjbLwQ",
    "CAACAgIAAxkBAAKep2S7ljsY8LRXFoJoLhGrkkx57_sKAALlDAACqFTBSPxg3fTAdQLKLwQ",
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

    # Send the photo with caption and the inline keyboard
    bot.send_photo(
        chat_id=message.chat.id,
        photo=open(photo_path, "rb"),
        caption=photo_caption,
    )

    # Send a random sticker from the hello_stickers list
    random_sticker_id = random.choice(hello_stickers)
    bot.send_sticker(chat_id=message.chat.id, sticker=random_sticker_id)


@bot.message_handler(commands=["alive"])
def alive(message):
    user = message.from_user
    # Randomly select a joke from the array
    joke = random.choice(jokes)

    caption = f"Of Course I'm Alive, {user.first_name}! 😊\n\n {joke}\n\n Okay jokes aside 😁\n What Series can I get you?"
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


# Load file data from JSON
def load_file_data():
    try:
        with open("file_data.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data
  
  
# Function to calculate similarity score between two strings using SequenceMatcher
def similarity_score(a, b):
    return SequenceMatcher(None, a, b).ratio()


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

# Handle search queries
@bot.message_handler(func=lambda message: True)
def handle_search(message):
    chat_id = message.chat.id

    # Check if there's a previous inline keyboard message and delete it (if possible)
    search_data = search_progress.get(chat_id, {})
    if "message_id" in search_data:
        try:
            bot.delete_message(chat_id=chat_id, message_id=search_data["message_id"])
        except telebot.apihelper.ApiException as e:
            pass

        del search_data["message_id"]

    search_query = message.text.lower()

    search_query = limit_search_query_length(search_query, max_length=100)

    # Replace commas, underscores, exclamation marks, and full stops with spaces
    search_query = re.sub(r"[,_!\.\-]", " ", search_query)

    # Load file data
    file_data = load_file_data()  # Assuming the 'load_file_data()' function exists to load file data

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

    # Sort results based on file name while ignoring special characters and spaces
    results = sorted(
        results, key=lambda x: re.sub(r"[^\w]", "", x[0]).lower(), reverse=True
    )

    # Send search results to user
    num_results = len(results)
    if num_results == 0:
        # Suggest similar file names using a similarity score algorithm
        file_name_scores = [
            (file_name, similarity_score(search_query, file_name.lower()))
            for file_name in file_data
        ]

        # Sort the file names based on similarity scores in descending order
        file_name_scores = sorted(file_name_scores, key=lambda x: x[1], reverse=True)

        # Select the top 5 suggestions
        top_suggestions = [file_name for file_name, _ in file_name_scores[:5]]

        # Construct the message text with search query suggestions in Markdown format
        message_text = f"🙅‍♂️\t\tSorry, '{search_query.title()}' Not Found!\n\nPlease Check Your Spelling or Use The Correct Search Syntax i.e \n*Baymax*\n*Baymax S01*\n*Baymax S01E02*\n\nHere are some suggestions:"

        # Create the inline keyboard with the suggestions as buttons
        keyboard = telebot.types.InlineKeyboardMarkup()

        for suggestion in top_suggestions:
            keyboard.add(
                telebot.types.InlineKeyboardButton(suggestion, callback_data=suggestion)
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
            delay=30  # Set the desired delay in seconds before deleting the messages
        )

    else:
        # Store the search results and starting index in the search_progress dictionary
        search_progress[message.chat.id] = {
            "results": results,
            "index": 0,
        }

        # Send the files keyboard
        send_files_keyboard(message.chat.id)

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
                time.sleep(40)
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

                # After the loop, periodically check and delete documents older than 45 seconds
                while sent_documents:
                    # Wait for a short interval (e.g., 5 seconds) before checking again
                    time.sleep(5)

                    # Get the current time
                    current_time = time.time()

                    # List to store message IDs of documents to delete
                    messages_to_delete = []

                    # Check if any documents are older than 45 seconds
                    for message_id, timestamp in sent_documents.items():
                        if current_time - timestamp >= 45:
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
        try:
            bot.delete_message(chat_id=chat_id, message_id=continue_message_id)
        except telebot.apihelper.ApiException as e:
            pass

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
