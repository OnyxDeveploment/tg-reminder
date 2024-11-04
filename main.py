import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler
import schedule
import time
import threading
import pytz
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get token and chat ID from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_CHAT_ID = os.getenv('USER_CHAT_ID')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot and updater
bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)

# Set Israel timezone
ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')

# Bot command to start the bot
def start(update: Update, context):
    update.message.reply_text("Alert bot started! You will receive updates.")

# Function to send daily alert for group check
def send_daily_group_check():
    bot.send_message(
        chat_id=USER_CHAT_ID,
        text="Telegram Alert: Check how many groups you have"
    )
    print("Telegram alert sent: Check how many groups you have")

# Function to send weekly alert for WhatsApp call check
def send_weekly_whatsapp_call_check():
    bot.send_message(
        chat_id=USER_CHAT_ID,
        text="Telegram Alert: Check calls in WhatsApp"
    )
    print("Telegram alert sent: Check calls in WhatsApp")

# Scheduler functions
def schedule_daily_task():
    # Set the time in Israel timezone for the daily group check at 9 AM
    target_time = datetime.now(ISRAEL_TIMEZONE).replace(hour=9, minute=0, second=0, microsecond=0)
    schedule.every().day.at(target_time.strftime("%H:%M")).do(send_daily_group_check)

def schedule_weekly_task():
    # Set the time in Israel timezone for the weekly WhatsApp call check on Sunday at 9 AM
    target_time = datetime.now(ISRAEL_TIMEZONE).replace(hour=9, minute=0, second=0, microsecond=0)
    schedule.every().sunday.at(target_time.strftime("%H:%M")).do(send_weekly_whatsapp_call_check)

# Function to get the next run times for both daily and weekly tasks
def get_next_run_info():
    daily_next_run = schedule.get_jobs()[0].next_run if len(schedule.get_jobs()) > 0 else None
    weekly_next_run = schedule.get_jobs()[1].next_run if len(schedule.get_jobs()) > 1 else None
    
    # Calculate remaining time for each task
    daily_remaining = daily_next_run - datetime.now() if daily_next_run else None
    weekly_remaining = weekly_next_run - datetime.now() if weekly_next_run else None

    return {
        'daily': (daily_next_run, str(daily_remaining).split('.')[0] if daily_remaining else None),
        'weekly': (weekly_next_run, str(weekly_remaining).split('.')[0] if weekly_remaining else None)
    }

# Run the schedule in a separate thread with countdown display
def run_scheduler():
    while True:
        schedule.run_pending()

        # Get next run info for both daily and weekly tasks
        next_run_info = get_next_run_info()
        
        # Format display information for each alert
        daily_info = (
            f"Daily alert scheduled at: {next_run_info['daily'][0]} | Countdown: {next_run_info['daily'][1]}"
            if next_run_info['daily'][0] else "No daily alert scheduled"
        )
        weekly_info = (
            f"Weekly alert scheduled at: {next_run_info['weekly'][0]} | Countdown: {next_run_info['weekly'][1]}"
            if next_run_info['weekly'][0] else "No weekly alert scheduled"
        )
        
        # Display both alerts in the terminal on a single line, updating in real time
        output_line = f"{daily_info}    {weekly_info}"
        print(f"\r{output_line}", end='')

        # Update every second
        time.sleep(1)

def main():
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))

    # Schedule the tasks
    schedule_daily_task()
    schedule_weekly_task()

    # Start the scheduler thread
    threading.Thread(target=run_scheduler, daemon=True).start()

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
