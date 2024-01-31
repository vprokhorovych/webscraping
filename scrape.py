from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re

import time
from datetime import date
import datetime
import traceback

from sqlalchemy.dialects.postgresql import insert, Insert
from sqlalchemy import delete

from model import Session, Car, CarSchema, FIELDS_TO_UPDATE

# нижче - допоміжні функції для витягування ціни з тексту тощо
def _get_price(text: str) -> int:
    text = text.replace(' ', '')
    return int(text[:text.find('$')])

pattern = re.compile(r'\d+')
def _get_first_num(text: str) -> int:
    match = pattern.search(text)
    return int(match.group()) if match else 0

def _get_last_num(text: str) -> str:
    return pattern.findall(text)[-1]

def _get_phone_number(text: str) -> str:
    return '+38' + ''.join(c for c in text if c.isdigit)

def build_upsert_dict(fields: list[str], stmt: Insert) -> dict:
    """Будує словник полів, які треба оновити під"""
    return {f: getattr(stmt.excluded, f) for f in fields}


SERVICE = Service(r'D:\WebDrivers\geckodriver.exe')
# URL = 'https://auto.ria.com/uk/car/used/{}'
URL = 'https://auto.ria.com/uk/search/?indexName=auto&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page={}&size=100'
options = Options()
options.add_argument('--headless')

PING_TIME = 5  # seconds
def try_open_url(driver: webdriver.Firefox, url: str):
    """Функція, яка відкриває сторінку. У випадку недоступності сайту тощо ініціює виключення"""

    start = time.time()

    while time.time() - start < PING_TIME:
        try:
            driver.get(url)
            break
        except WebDriverException:
            trb_str = traceback.format_exc()
            time.sleep(1)

    else:
        raise RuntimeError(f"Scraping terminated: the site  {url}  is unavailable for {PING_TIME} seconds " \
                           f"see the following traceback:\n{trb_str}")


def page_404(driver: webdriver.Firefox) -> bool:
    """Повертає `True`, якщо сторінка містить повідомлення про помилку 404, інакше `False`.
    Сторінка вже має бути відкрита.
    """

    try:  # сайт відкриває сторінку із текстом про помилку 404 ...
        driver.find_element(By.CLASS_NAME, "contains-404")
        return True
    except NoSuchElementException:
        return False
    
    # try:  # ... або сайт показує кілька машин та текст "Вас також можуть зацікавити"
    #     driver.find_element(By.ID, "searchResults").find_element(By.CSS_SELECTOR, "section.ticket-item ")
    # except NoSuchElementException:
    #     return False

def empty_page(driver: webdriver.Firefox) -> bool:
    """Повертає `True`, якщо сторінка не містить машин, інакше `False`.
    Сторінка вже має бути відкрита.
    """

    return not bool(driver.find_elements(By.CLASS_NAME, "m-link-ticket"))


def open_url(driver: webdriver.Firefox, url: str) -> bool:
    """Відкриває сторінку і вертає `True`, якщо вона не 404, інакше вертає `False`"""

    try_open_url(driver, url)
    return not page_404(driver)


def prepare(url):
    """Створює та вертає драйвер і відкриває сторінку із адресою `url`, а також закриває
    стандартне вікно з попередженням про використання куків"""

    driver = webdriver.Firefox(service=SERVICE, options=options)

    # driver.capabilities['timeouts']['pageLoad'] = 8000  # вебдрайвер чекатиме завантаження сторінки 
    #                                                     # щонайбільше 8 секунд
    driver.set_page_load_timeout(30)

    open_url(driver, url)

    cookies_ok_button = WebDriverWait(driver, 3).until(  # драйвер новий, тому з'явиться попередження про куки 
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='c-notifier-close']"))
    )
    cookies_ok_button.click()

    return driver


def car_deleted(driver: webdriver.Firefox) -> bool:
    """Іноді машина є у фіді, але вона вже продана. У цьому разі майже всі потрібні нам поля відсутні,
    але є відповідне попередження."""

    try:
        driver.find_element(By.ID, "autoDeletedTopBlock")
    except NoSuchElementException:
        return False
    
    return True


def process_car(driver: webdriver.Firefox, car_url) -> dict:
    """Основна функція, яка витягує потрібні дані з особистої сторінки машини. Неприємна проблема - 
    вряди-годи сайт вертав сторінки через інші cdn. У цьому разі завантаження триває довше, а сторінки мають
    іншу розмітку, яку я, на жаль, не зміг протестувати, бо такий казус трапився лише кілька разів. """

    data = {}
    data['url'] = car_url
    data['rid'] = _get_last_num(car_url)

    # перша частина відповідає 'нормальному' завантаженню сторінок, друга - 'повільному'
    try:
        t = driver.find_element(By.CSS_SELECTOR, "h1.head")
    except NoSuchElementException:
        t = driver.find_element(By.ID, "sideTitleTitle").find_element(By.CSS_SELECTOR, "span.common-text.titleM")
    data['title'] = t.text

    try:
        p = driver.find_element(By.CLASS_NAME, "price_value").find_element(By.TAG_NAME, "strong").text
        if '$' in p:
            data['price_usd'] = _get_price(p)
        else:  # іноді головна ціна в гривнях, а не доларах
            p = driver.find_element(By.CLASS_NAME, "price_value--additional") \
                      .find_element(By.XPATH, ".//span[@data-currency='USD']").text
            data['price_usd'] = _get_price(p + '$')  # int (125 000) -> ValueError
            
    except NoSuchElementException:
        p = driver.find_element(By.ID, "sidePrice").find_element(By.CSS_SELECTOR, "strong.common-text.titleL").text
        data['price_usd'] = _get_price(p)

    try:
        try:
            od = driver.find_element(By.CLASS_NAME, "base-information")
        except NoSuchElementException:
            od = driver.find_element(By.ID, "basicInfoTableMainInfoLeft0") \
                        .find_element(By.CSS_SELECTOR, "span.common-text.body")
    except NoSuchElementException:  # у машин може бути відсутній пробіг, але у вживаних таке, мабуть, не трапляється
        od = None
    data['odometer'] = _get_first_num(od.text) if od is not None else 0


    try:
        u = driver.find_element(By.CLASS_NAME, "seller_info_name")
    except NoSuchElementException:
        u = driver.find_element(By.ID, "sellerInfoUserName") \
                  .find_element(By.CSS_SELECTOR, "span.common-text.titleM")
    data['username'] = u.text.strip()

    try:
        iu = driver.find_element(By.CSS_SELECTOR, "img.outline.m-auto")
    except NoSuchElementException:
        iu = driver.find_element(By.CLASS_NAME, "carousel-wrapper") \
                                .find_element(By.TAG_NAME, "img")
    data['image_url'] = iu.get_attribute('src')

    try:
        try:
            ic = driver.find_element(By.CSS_SELECTOR, "a.show-all.link-dotted")
        except NoSuchElementException:

            # часом поля "Показати всі N фотографій" нема
            ic = driver.find_element(By.XPATH, '//*[@id="photosBlock"]/div[1]/div[2]/span/span[2]')
    except NoSuchElementException:
        try:
            ic = driver.find_element(By.CLASS_NAME, "carousel-wrapper") \
                                        .find_element(By.CSS_SELECTOR, "span.common-badge.alpha.medium") \
                                        .find_elements(By.TAG_NAME, "span")[-1]
        except NoSuchElementException:
            ic = None
    data['images_count'] = _get_first_num(ic.text if ic is not None else '0')

    try:
        try:
            cn = driver.find_element(By.CSS_SELECTOR, "span.state-num.ua")
        except NoSuchElementException:
            cn = driver.find_element(By.CSS_SELECTOR, "div.car-number.ua") \
                                       .find_element(By.TAG_NAME, "span")
    except NoSuchElementException:
        cn = None  # може бути відсутній
    data['car_number'] = cn.text.strip() if cn is not None else None

    try:
        try:  # перевірений і звичайний vin-code відрізняються
            cv = driver.find_element(By.CSS_SELECTOR, "span.label-vin")
        except NoSuchElementException:
            cv = driver.find_element(By.CSS_SELECTOR, "span.vin-code") 
    except NoSuchElementException:
        try:
            cv = driver.find_element(By.ID, "badgesVin") \
                       .find_element(By.TAG_NAME, "span")
        except NoSuchElementException:
            cv = None  # може бути відсутній
    data['car_vin'] = cv.text if cv is not None else None

    try: 
        show_phone_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "phone_show_link")))
        show_phone_button.click()

        # Беремо тільки перший номер телефону, їх може бути декілька
        ph = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popup-successful-call-desk"))
        )

    except NoSuchElementException:
        show_phone_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "sl.conversion")))
        show_phone_button.click()

        phone_popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popup-inner"))
        )

        ph = phone_popup.find_element(By.TAG_NAME, "span")
    data["phone_number"] = _get_phone_number(ph.text)

    return data


def scrape():
    """Бігаємо по сторінках, визначаємо urls всіх вживаних машин, зображених на даній сторінці,
    запам'ятовуємо їх, потім заходимо по кожному url-у, і беремо звідти необхідну інфу. Після цього
    робимо bulk upsert отриманих даних (оновлюючи `update_date` - це дуже важливо), і йдемо до
    наступної сторінки. Як все проскрейпили, видаляємо з БД ті записи, у яких `update_date` менша 
    за поточну дату (це машини, яких уже нема у фіді).
    
    Крім того, доводиться замінювати драйвер - після кількох сот відкритих сторінок браузер просто
    припиняє відкривати нові сторінки (схожу поведінку я спостерігав і звичайному браузері) заразом
    споживаючи кілька гігабайтів оперативки. Можна було б чистити кеш, але простіше свторити новий драйвер"""

    try:
        i = 0
        driver = prepare(URL.format(i))
        data = []
        schema = CarSchema()
        today = date.today()
        rids_met = set()  # оскільки autoria.com оновлює дані, то може трапитися таке, що ми проглянули машину Х,
                          # а поки ми дійшли до кінця поточної сторінки, нові машини витіснили Х на наступну сторінку,
                          # і ми знову будемо працювати з Х
        total = 0
        start = time.time()
        with Session() as session:
            while True:
                data = []

                # if i == 2: break 

                if i >= 1:  
                    if not open_url(driver, URL.format(i)) or empty_page(driver):
                        break  # більше машин нема, ми закінчили

                i += 1

                elements = driver.find_elements(By.CLASS_NAME, "m-link-ticket")

                urls = [e.get_attribute('href') for e in elements]  
                # print('\n', f'Urls len:  {len(urls)}')
                # print('\n', f'Set  len:  {len(set(urls))}', '\n')
                for url in urls:
                    print(url)

                    try:
                        if not open_url(driver, url):  # якщо раптом сторінка припинила існувати
                            continue
                    except RuntimeError:  # драйвер більше не може відкривати сторінки
                        driver.quit()
                        print('\nDriver refreshing\n')
                        driver = prepare(url)

                    if car_deleted(driver):  # якщо машина вже продана
                        continue

                    # if url == 'https://auto.ria.com/uk/auto_mercedes_benz_gl_class_35952891.html':
                    #     1
                    try:
                        raw_data = process_car(driver, url)
                    except NoSuchElementException:  # якщо інша розмітка - пропускаємо цей запис
                        continue

                    data.append(schema.load(raw_data))

                    rid = data[-1]['rid']
                    if rid in rids_met:
                        continue

                    rids_met.add(rid)

                
                # bulk upsert
                insert_stmt = insert(Car).values(data)
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[Car.rid],
                    set_=build_upsert_dict(FIELDS_TO_UPDATE, insert_stmt)
                )

                session.execute(upsert_stmt)
                session.commit()

                total += len(urls)
                print(f'\nProcessed {total} cars in  {time.time() - start} seconds\n')

            session.execute(delete(Car).where(Car.update_date < today))  # видалити машини, яких уже нема на сайті
            session.commit()

            print(f"Scraping finished successfully; total time:  {time.time() - start}")

    finally:
        driver.quit()

import os
from model import db_url
from backup import backup
BACKUP_DIR = 'dumps'
backup_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
if not os.path.exists(backup_dir_path):
    os.mkdir(backup_dir_path)

scrape()
backup(db_url, backup_dir_path)