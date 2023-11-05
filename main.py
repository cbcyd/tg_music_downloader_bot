import logging
from pathlib import Path
import os
import shutil
import configparser

import streamrip

from .sql import read_client, update_or_create_client

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()                                     
config.read('config.ini')

token = config.get('TELEGRAM', 'BOT_TOKEN')
email_or_userid = config.get('QOBUZ', 'email_or_userid')
password_or_token = config.get('QOBUZ', 'password_or_token')
arl = config.get('DEEZER', 'ARL')

clients = []

clients.append(streamrip.clients.QobuzClient())
clients[0].login(email_or_userid=email_or_userid, password_or_token=password_or_token, use_auth_token=True)

clients.append(streamrip.clients.DeezerClient())
clients[1].login(arl=arl)

clients_names = ['Qobuz', 'Deezer']

def load_album(album_id, client_id):
    client = clients[client_id]
    my_album = streamrip.media.Album(client=client, id=album_id)
    my_album.load_meta()
    return my_album

def get_client_id(update):
    client_id = read_client(update.message.from_user.id)
    if not client_id:
        client_id = 0
        update_or_create_client(update.message.from_user.id, client_id)
    return client_id

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    client_id = get_client_id(update)
    await update.message.reply_text("Hi!", reply_markup=[[KeyboardButton('Deezer' if client_id else 'Qobuz')]])


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    client_id = get_client_id(update)
    await update.message.reply_text("Help!", reply_markup=[[KeyboardButton('Deezer' if client_id else 'Qobuz')]])


async def downloading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""

    client_id = get_client_id(update)

    album = load_album(update.message.text, client_id)
    meta = album.meta

    text = f"Name: {meta.album}\nArtist: {meta.albumartist}\nQuality: {meta.bit_depth}bit/{meta.sampling_rate}Hz\nMedia ID: {meta.id}\nRelease Year: {meta.year}"
    await update.message.reply_photo(photo=meta.cover_urls['original'], caption=text, )

    downloading_message = await update.message.reply_text('Downloading...', reply_markup=[[KeyboardButton('Deezer' if client_id else 'Qobuz')]])

    album.download(quality=4)

    await downloading_message.delete()

    album_path = album.folder
    for file_name in sorted(os.listdir(album_path)):
        if file_name.split('.')[-1] == 'flac':
            file_path = f'{album_path}/{file_name}'
            await update.message.reply_audio(Path(file_path), caption=file_name)
    
    shutil.rmtree(album_path)

    await update.message.reply_text('Done', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Search Again', switch_inline_query_current_chat='')]]))    

def inline_query_results(update, query):
    client_id = get_client_id(update)
    client = clients[client_id]
    results = []
    if client_id:

        albums = client.search(query, limit=50)
        for album in albums['data'][:50]:
    
            description = f"Title: {album['title']}, Artist: {album['artist']['name']}, Tracks Count: {album['nb_tracks']}"

            results.append(InlineQueryResultArticle(
                        id=album['id'],
                        title=album['title'],
                        input_message_content=InputTextMessageContent(album['id']),
                        thumbnail_url=album['cover_small'],
                        description=description
                    ))
    else:

        result = client.search(query, limit=50)
        for pages in result:
            
            for album in list(pages.values())[1]['items'][:50]:
                description = f"Title: {album['title']}, Artist: {album['artist']['name']}, Sample Rate: {album['maximum_sampling_rate']}, Bit Depth: {album['maximum_bit_depth']}, Tracks Count: {album['tracks_count']}"
                results.append(InlineQueryResultArticle(
                    id=album['id'],
                    title=album['title'],
                    input_message_content=InputTextMessageContent(album['id']),
                    #url=album['url'],
                    thumbnail_url=album['image']['thumbnail'],
                    description=description
                ))
            break
    return results



async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query

    if not query:  # empty query should not be handled
        return
    
    results = inline_query_results(update, query)

    await update.inline_query.answer(results)


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on inline queries - show corresponding inline results
    application.add_handler(InlineQueryHandler(inline_query))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloading))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()