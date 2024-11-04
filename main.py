import logging
import os
import schedule
import time
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables from .env file
load_dotenv()

# Get token and chat ID from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_CHAT_ID = os.getenv('USER_CHAT_ID')

# Validate environment variables
if not BOT_TOKEN or not USER_CHAT_ID:
    raise ValueError("BOT_TOKEN and USER_CHAT_ID must be set in the .env file")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=BOT_TOKEN)

# Function to send the reminder message
def send_reminder_message():
    try:
        bot.send_message(
            chat_id=USER_CHAT_ID,
            text="תבדוק כמה קבוצות יש לך"
        )
        logger.info("Sent 'תבדוק כמה קבוצות יש לך' message to group.")
    except Exception as e:
        logger.error(f"Error sending message: {e}")

# Schedule the task to run every 24 Hours
# schedule.every(10).minutes.do(send_reminder_message)
schedule.every(24).hours.do(send_reminder_message)

# Function to calculate the remaining time until the next job
def get_time_until_next_run():
    next_run = schedule.next_run()
    if next_run:
        remaining_time = next_run - datetime.now()
        return remaining_time if remaining_time.total_seconds() > 0 else timedelta(0)
    return None

# Run the schedule in a separate thread with countdown display
def run_scheduler():
    while True:
        schedule.run_pending()

        # Get the time remaining until the next run
        remaining_time = get_time_until_next_run()
        countdown = str(remaining_time).split(".")[0] if remaining_time else "No next run scheduled"
        
        # Display the countdown in the terminal, updating in real time
        print(f"\rNext reminder in: {countdown}", end="")

        # Update every second
        time.sleep(1)

if __name__ == '__main__':
    # Send an initial message when the bot starts
    send_reminder_message()
    # Start the scheduler with countdown display
    run_scheduler()
