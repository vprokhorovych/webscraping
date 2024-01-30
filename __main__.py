import os
import time

import schedule
from dotenv import load_dotenv

from scrape import scrape
from model import db_url
from backup import backup as base_backup


load_dotenv()

# SCRAPING_TIME = os.getenv("SCRAPING_TIME", "12:00")
# BACKUP_TIME = os.getenv("BACKUP_TIME", "15:00")
SCRAPING_TIME = ("17:44")
BACKUP_TIME = ("17:45")
print(SCRAPING_TIME, BACKUP_TIME)
BACKUP_DIR = 'dumps'
backup_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
if not os.path.exists(backup_dir_path):
    os.mkdir(backup_dir_path)

backup = lambda: base_backup(db_url, backup_dir_path)

schedule.every().day.at(SCRAPING_TIME).do(scrape)
schedule.every().day.at(BACKUP_TIME).do(backup)

while True:
    schedule.run_pending()
    time.sleep(1)