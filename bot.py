import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
import logging
import os
# Replace with your actual bot token and admin user ID
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID"))  # Replace with your Telegram User ID as an integer

# Enable logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

# Store channel IDs where the bot is admin (and should listen)
CHANNEL_IDS = []  #  Bot must be an admin to get updates

def start(update: telegram.Update, context: CallbackContext) -> None:
    """Sends a welcome message when the /start command is issued."""
    update.message.reply_text('Hello! I will notify you about reactions to posts in the channels I manage.')
    update.message.reply_text('Add me to the group or channel and give me admin rights!')

def add_channel(update: telegram.Update, context: CallbackContext) -> None:
    """Adds a channel to the list of monitored channels."""
    try:
        channel_id = int(context.args[0])  # Get channel ID from command argument
        if channel_id not in CHANNEL_IDS:
            CHANNEL_IDS.append(channel_id)
            update.message.reply_text(f"Channel ID {channel_id} added to monitoring list.")
        else:
            update.message.reply_text("Channel already being monitored.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /addchannel <channel_id>")

def remove_channel(update: telegram.Update, context: CallbackContext) -> None:
    """Removes a channel from the list of monitored channels."""
    try:
        channel_id = int(context.args[0])
        if channel_id in CHANNEL_IDS:
            CHANNEL_IDS.remove(channel_id)
            update.message.reply_text(f"Channel ID {channel_id} removed from monitoring list.")
        else:
            update.message.reply_text("Channel not in monitoring list.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /removechannel <channel_id>")



def reaction_handler(update: telegram.Update, context: CallbackContext) -> None:
    """Handles message reaction updates."""

    if update.message_reaction:
        reaction = update.message_reaction
        chat_id = reaction.chat.id

        # Check if the bot is monitoring this channel
        if chat_id in CHANNEL_IDS:
            user = reaction.user
            message_id = reaction.message_id

            # Extract the reaction emoji (if available)
            reaction_type = None
            if reaction.new_reaction and reaction.new_reaction[0].type == 'emoji':
                reaction_type = reaction.new_reaction[0].emoji
            elif reaction.old_reaction and reaction.old_reaction[0].type == 'emoji':
                reaction_type = reaction.old_reaction[0].emoji

            # Construct user link (using username if available, otherwise ID)
            user_link = f"tg://user?id={user.id}"  # Fallback to ID

            if user.username:
                user_link = f"https://t.me/{user.username}"


            message = (
                f"⚠️ Reaction Update in Channel {chat_id}:\n"
                f"User: {user.first_name} {user.last_name or ''} (@{user.username or user.id})\n"
                f"User ID: {user.id}\n"
                f"User Link: {user_link}\n"
                f"Message ID: {message_id}\n"
                f"Reaction: {reaction_type or 'Unknown'}\n"
            )

            context.bot.send_message(chat_id=ADMIN_USER_ID, text=message)
        else:
            logger.info(f"Reaction in unmonitored channel: {chat_id}")


def error_handler(update: telegram.Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')


def main() -> None:
    """Start the bot."""
    updater = Updater(BOT_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addchannel", add_channel, pass_args=True))
    dp.add_handler(CommandHandler("removechannel", remove_channel, pass_args=True))

    dp.add_handler(MessageHandler(Filters.update.message_reaction, reaction_handler))

    dp.add_error_handler(error_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
