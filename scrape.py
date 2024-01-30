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
URL = 'https://auto.ria.com/uk/car/used/{}'
options = Options()
options.add_argument('--headless')

PING_TIME = 300  # seconds
def try_open_url(driver: webdriver.Firefox, url: str):
    """Функція, яка відкриває сторінку. У випадку недоступності сайту тощо ініціює виключення"""

    start = datetime.datetime.now()

    while (datetime.datetime.now() - start).seconds < PING_TIME:
        try:
            driver.get(url)
            break
        except WebDriverException:
            trb_str = traceback.format_exc()
            time.sleep(5)

    else:
        raise RuntimeError(f"Scraping terminated: the site  {url}  is unavailable for {PING_TIME} seconds " \
                           f"see the following traceback:\n{trb_str}")


def page_not_found(driver: webdriver.Firefox) -> bool:
    """Якщо сторінка не існує, autoria.com показує сторінку із текстом '404 сторінку не знайдено'.
    У цьому разі повертаємо `True`, інакше `False`. Сторінка вже має бути відкрита"""

    try:
        driver.find_element(By.CLASS_NAME, "contains-404")
    except NoSuchElementException:
        return False
    
    return True

def open_url(driver: webdriver.Firefox, url: str) -> bool:
    """Відкриває сторінку і вертає `True`, якщо все вона знайдена, інакше вертає `False`"""


    try_open_url(driver, url)
    return not page_not_found(driver)

def prepare():
    """Створює та вертає драйвер і відкриває першу потрібну сторінку, а також закриває вікно з
    попередженням про куки"""

    driver = webdriver.Firefox(service=SERVICE, options=options)

    open_url(driver, URL.format(''))

    cookies_ok_button = WebDriverWait(driver, 3).until(  # cookies always pop up
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='c-notifier-close']"))
    )
    cookies_ok_button.click()

    return driver


def car_deleted(driver: webdriver.Firefox) -> bool:
    """Іноді машина є у фіді, але її вона вже продана."""

    try:
        driver.find_element(By.ID, "autoDeletedTopBlock")
    except NoSuchElementException:
        return False
    
    return True


def process_car(driver: webdriver.Firefox, car_url) -> dict:
    """Основна функція, яка витягує потрібні дані з особистої сторінки машини. Неприємн проблема - 
    іноді сайт вертав сторінки через інші cdn, які довше вантажились, і ці сторінки, на жаль, мають
    іншу розмітку, яку я, на жаль, не зміг протестувати, бо такий казус трапився лише кілька разів."""

    data = {}
    data['url'] = car_url
    data['rid'] = _get_last_num(car_url)

    try:
        data['title'] = driver.find_element(By.CSS_SELECTOR, "h1.head").text
    except NoSuchElementException:
        data['title'] = driver.find_element(By.ID, "sideTitleTitle").find_element(By.CSS_SELECTOR, "span.common-text.titleM").text

    try:
        try:
            p = driver.find_element(By.CLASS_NAME, "price_value").find_element(By.TAG_NAME, "strong").text
        except NoSuchElementException:
            p = driver.find_element(By.CLASS_NAME, "price_value--additional").text  # іноді головна ціна в гривнях, а не доларах
    except NoSuchElementException:
        p = driver.find_element(By.ID, "sidePrice").find_element(By.CSS_SELECTOR, "strong.common-text.titleL").text
    data['price_usd'] = _get_price(p)

    try:
        try:
            od = driver.find_element(By.CLASS_NAME, "base-information").text
        except NoSuchElementException:
            od = driver.find_element(By.ID, "basicInfoTableMainInfoLeft0") \
                        .find_element(By.CSS_SELECTOR, "span.common-text.body").text
    except NoSuchElementException:  # у машин може бути відсутній пробіг, але у вживаних таке, мабуть, не трапляється
        od = 0
    data['odometer'] = _get_first_num(od)


    try:
        data['username'] = driver.find_element(By.CLASS_NAME, "seller_info_name").text.strip()
    except NoSuchElementException:
        data['username'] = driver.find_element(By.ID, "sellerInfoUserName") \
                                 .find_element(By.CSS_SELECTOR, "span.common-text.titleM").text.strip()

    try:
        data['image_url'] = driver.find_element(By.CSS_SELECTOR, "img.outline.m-auto").get_attribute('src')
    except NoSuchElementException:
        data['image_url'] = driver.find_element(By.CLASS_NAME, "carousel-wrapper") \
                                .find_element(By.TAG_NAME, "img") \
                                .get_attribute('src')

    try:
        try:
            ic = driver.find_element(By.CSS_SELECTOR, "a.show-all.link-dotted").text
        except NoSuchElementException:

            # часом поля "Показати всі N фотографій нема"
            ic = driver.find_element(By.XPATH, '//*[@id="photosBlock"]/div[1]/div[2]/span/span[2]').text
    except NoSuchElementException:
        try:
            ic = driver.find_element(By.CLASS_NAME, "carousel-wrapper") \
                                        .find_element(By.CSS_SELECTOR, "span.common-badge.alpha.medium") \
                                        .find_elements(By.TAG_NAME, "span")[-1].text
        except NoSuchElementException:
            ic = 0
    data['images_count'] = _get_first_num(ic)

    try:
        try:
            data['car_number'] = driver.find_element(By.CSS_SELECTOR, "span.state-num.ua").text.strip()
        except NoSuchElementException:
            data['car_number'] = driver.find_element(By.CSS_SELECTOR, "div.car-number.ua") \
                                    .find_element(By.TAG_NAME, "span").text.strip()
    except NoSuchElementException:
        data['car_number'] = None  # може бути відсутній

    try:
        try:
            data['car_vin'] = driver.find_element(By.CSS_SELECTOR, "span.label-vin").text
        except NoSuchElementException:
            data['car_vin'] = driver.find_element(By.CSS_SELECTOR, "span.vin-code").text
    except NoSuchElementException:
        try:
            data['car_vin'] = driver.find_element(By.ID, "badgesVin") \
                                    .find_element(By.TAG_NAME, "span").text
        except NoSuchElementException:
            data['car_vin'] = None  # може бути відсутній

    try: 
        show_phone_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "phone_show_link")))
        show_phone_button.click()

        # Беремо тільки перший номер телефону, їх може бути декілька
        ph = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popup-successful-call-desk"))
        ).text

    except NoSuchElementException:
        show_phone_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "sl.conversion")))
        show_phone_button.click()

        # Беремо тільки перший номер телефону
        phone_popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popup-inner"))
        )

        ph = phone_popup.find_element(By.TAG_NAME, "span").text
    data["phone_number"] = _get_phone_number(ph)

    return data


def scrape():
    """Бігаємо по сторінках, визначаємо urls всіх вживаних машин, зображених на даній сторінці,
    запам'ятовуємо їх, потім заходимо по кожному url-у, і беремо звідти необхідну інфу. Після цього
    робимо bulk upsert отриманих даних (оновлюючи `update_date` - це дуже важливо), і йдемо до
    наступної сторінки. Як все проскрейпили, видаляємо з БД ті записи, у яких `update_date` менша 
    за поточну дату (це машини, яких уже нема у фіді)."""

    try:
        driver = prepare()
        i = 0
        data = []
        schema = CarSchema()
        today = date.today()
        rids_met = set()  # оскільки autoria.com оновлює дані, то може трапитися таке, що ми проглянули машину Х,
                          # а поки ми дійшли до кінця поточної сторінки, нові машини витіснили Х на наступну сторінку,
                          # і ми знову будемо працювати з Х
        
        with Session.begin() as session:
            while True:
                data = []

                # if i == 2: break 

                if i >= 1:  
                    if not open_url(driver, URL.format(f'?page={i + 1}')):
                        break  # більше машин нема, ми закінчили
                    if i == 1:  # показуємо по 100 машин на сторінку
                                # найперша сторінка не має опції вибору, тому
                                # робимо це тут
                        
                        btn = driver.find_element(By.ID, "paginationChangeSize")
                        ActionChains(driver).move_to_element(btn)
                        btn.click()

                        show_max = driver.find_elements(By.ID, "paginationSizeOptions")[-1]  # останній елемент - найбільший
                        # print(show_max.text)
                        ActionChains(driver).move_to_element(show_max)
                        # time.sleep(5)
                        show_max.click()

                i += 1

                elements = driver.find_elements(By.CLASS_NAME, "m-link-ticket")
                if not elements:  # про всяк випадок
                    break

                urls = [e.get_attribute('href') for e in elements]  
                # print('\n', f'Urls len:  {len(urls)}')
                # print('\n', f'Set  len:  {len(set(urls))}', '\n')
                for url in urls:
                    
                    if not open_url(driver, url):
                        continue
                    if car_deleted(driver):
                        continue

                    raw_data = process_car(driver, url)

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
            
            session.execute(delete(Car).where(Car.update_date < today))
            print("Scraing finished successfully)")

    finally:
        driver.quit()

