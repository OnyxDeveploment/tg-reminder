import logging
import os
import schedule
import time
import threading
import asyncio
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

# Configure logging with file handler and rotation
log_file = "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=BOT_TOKEN)

# Async function to send the daily group reminder message
async def send_group_check_message():
    try:
        await bot.send_message(
            chat_id=USER_CHAT_ID,
            text="בצע ספירת קבוצות יומית"
        )
        logger.info("Sent 'בצע ספירת קבוצות יומית' message to group.")
    except Exception as e:
        logger.error(f"Error sending daily message: {e}")

# Async function to send the weekly WhatsApp call reminder message
async def send_whatsapp_check_message():
    try:
        await bot.send_message(
            chat_id=USER_CHAT_ID,
            text="בצע בדיקת שיחות וואצאפ"
        )
        logger.info("Sent 'בצע בדיקת שיחות וואצאפ' message to group.")
    except Exception as e:
        logger.error(f"Error sending weekly message: {e}")

# Wrapper functions for scheduling
def schedule_daily_message():
    asyncio.run(send_group_check_message())

def schedule_weekly_message():
    asyncio.run(send_whatsapp_check_message())

# Schedule the tasks and capture jobs for easy access
daily_job = schedule.every().day.at("10:00").do(schedule_daily_message)  # Daily message at 10 AM
weekly_job = schedule.every().sunday.at("10:00").do(schedule_weekly_message)  # Weekly message on Sunday at 10 AM

# Function to get remaining time for each job
def get_next_run_info():
    daily_next_run = daily_job.next_run if daily_job else None
    weekly_next_run = weekly_job.next_run if weekly_job else None
    
    daily_remaining = daily_next_run - datetime.now() if daily_next_run else None
    weekly_remaining = weekly_next_run - datetime.now() if weekly_next_run else None

    return {
        'daily': (daily_next_run, str(daily_remaining).split('.')[0] if daily_remaining else None),
        'weekly': (weekly_next_run, str(weekly_remaining).split('.')[0] if weekly_remaining else None)
    }

# Run the schedule in a separate thread with countdown display for both reminders
def run_scheduler():
    while True:
        try:
            schedule.run_pending()

            # Get remaining time for both daily and weekly reminders
            next_run_info = get_next_run_info()
            
            # Display countdown for both daily and weekly reminders with each on a new line
            daily_info = (
                f"Next group reminder at: {next_run_info['daily'][0]} | Countdown: {next_run_info['daily'][1]}"
                if next_run_info['daily'][0] else "No daily reminder scheduled"
            )
            weekly_info = (
                f"Next WhatsApp reminder at: {next_run_info['weekly'][0]} | Countdown: {next_run_info['weekly'][1]}"
                if next_run_info['weekly'][0] else "No weekly reminder scheduled"
            )
            
            # Clear the screen and print each reminder on a new line
            os.system('cls' if os.name == 'nt' else 'clear')
            print(daily_info)
            print(weekly_info)

            # Update every second
            time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            time.sleep(5)  # Wait a bit before retrying to avoid repeated errors

# Main function to start the scheduler thread
def main():
    try:
        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        scheduler_thread.join()  # Keep the main thread active
    except Exception as e:
        logger.critical(f"Failed to start the scheduler: {e}")

if __name__ == '__main__':
    main()
