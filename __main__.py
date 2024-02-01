import os
import time

import schedule
from dotenv import load_dotenv

from .scrape import scrape as base_scrape
from .model import db_url
from .backup import backup as base_backup
from .argparser import parser

load_dotenv()  # завантажуємо змінні середовища з .env

SCRAPING_TIME = os.getenv("SCRAPING_TIME", "12:00")
BACKUP_TIME = os.getenv("BACKUP_TIME", "15:00")

BACKUP_DIR = 'dumps'
backup_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
# backup_dir_path = os.path.join((os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
if not os.path.exists(backup_dir_path):  # створюємо теку для дампів, якщо її нема
    os.mkdir(backup_dir_path)


args = parser.parse_args()
s = args.scrape
b = args.backup
a = args.all or (s and b)
p = args.pages

# роботи для планувальника
backup = lambda: base_backup(db_url, backup_dir_path)
scrape = lambda: base_scrape(p)

# schedule.every().day.at(SCRAPING_TIME).do(base_scrape)
schedule.every().day.at(SCRAPING_TIME).do(scrape)  # оскільки поточний скрейпінг всіх сторінко триватиме дуже довго
                                                   # то суто заради наочності будемо прочісувати лише перші args.pages
                                                   # сторінок
schedule.every().day.at(BACKUP_TIME).do(backup)

print("\nThe program has started!\n")

msg = 'Running {} now'
if a:
    print(msg.format('scraping and backuping'))
    scrape()
    backup()
elif s:
    print(msg.format('scraping'))
    scrape()
elif b:
    print(msg.format('backuping'))
    backup()

print('\nStarting the scheduler: ')
print('\tSCRAPING_TIME: ', SCRAPING_TIME)
print('\tBACKUP_TIME: ', BACKUP_TIME, '\n')


while True:
    schedule.run_pending()
    time.sleep(1)
