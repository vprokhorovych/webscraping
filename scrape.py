import re
import time
from datetime import date
import traceback

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy.dialects.postgresql import insert, Insert
from sqlalchemy import delete

from .model import Session, Car, CarSchema, FIELDS_TO_UPDATE

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
# URL = 'https://auto.ria.com/uk/search/?indexName=auto&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page={}&size=100'
URL = 'https://auto.ria.com/uk/search/?indexName=auto&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page={}&size=10'
MAIN_PAGE_URL = 'https://auto.ria.com/uk'
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


def open_url(driver: webdriver.Firefox, url: str) -> bool:
    """Відкриває сторінку і вертає `True`, якщо вона не 404, інакше вертає `False`"""

    try_open_url(driver, url)
    return not page_404(driver)


def prepare(url):
    """Створює та вертає драйвер і відкриває сторінку із адресою `url`, а також закриває
    стандартне вікно з попередженням про використання куків"""

    driver = webdriver.Firefox(service=SERVICE, options=options)

    driver.set_page_load_timeout(10)  # завантажуємо сторінку щонайбільше 10 секунд

    open_url(driver, url)

    cookies_ok_button = WebDriverWait(driver, 3).until(  # драйвер новий, тому з'явиться попередження про куки 
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='c-notifier-close']"))
    )
    cookies_ok_button.click()

    return driver


# У цілому, можна було б просто шукати в картці машини у фіді елемент "Продано", і замість двох
# функцій нижче обмежитися однією. Але теоретично може бути ситуація, що якусь машину випадково
# позначили проданою, і поки я дійду до її url-a, цю мітку видалять. Саме для такого випадку потрібна
# функція `car_deleted`. Якщо ж машина продана давно, але ще є у фіді, то її url збігатиметься з адресою
# головної сторінки `MAIN_PAGE_URL` (таке буває), і тому отримати її актуальний стан - неможливо (хоча, найімовірніше,
# якщо машину давно продали, то це не є помилка), тому потрібна функція `redirect_to_main_page`

def car_deleted(driver: webdriver.Firefox) -> bool:
    """Іноді машина є у фіді, але вона вже продана. У цьому разі майже всі потрібні нам поля відсутні,
    але на сторінці є відповідне попередження."""

    try:
        driver.find_element(By.ID, "autoDeletedTopBlock")
    except NoSuchElementException:
        return False
    
    return True


def redirect_to_main_page(url):
    """Іноді машина є у фіді, але вона вже продана досить давно (наприклад, годин 5 тому), і її `url`
    тоді збігається із `MAIN_PAGE_URL`. У такому разі ми не повинні скрейпити цей `url`."""

    return url == MAIN_PAGE_URL


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


def scrape(pages: int = None):
    """Бігаємо по сторінках, визначаємо urls всіх вживаних машин, зображених на даній сторінці,
    запам'ятовуємо їх, потім заходимо по кожному url-у, і беремо звідти необхідну інфу. Після цього
    робимо bulk upsert отриманих даних (оновлюючи `update_date` - це дуже важливо), і йдемо до
    наступної сторінки. Як все проскрейпили, видаляємо з БД ті записи, у яких `update_date` менша 
    за поточну дату (це машини, яких уже нема у фіді).
    
    Крім того, доводиться замінювати драйвер - після кількох сот відкритих сторінок (а іноді просто після кількох -
    на щастя, це дуже рідко трапляється) браузер просто припиняє відкривати нові сторінки (схожу поведінку
    я спостерігав і звичайному браузері) заразом споживаючи кілька гігабайтів оперативки. Можна було б чистити
    кеш, але простіше створити новий драйвер.
    """

    try:
        print(f'Pages to scrape: {pages if pages else "all"}')
        i = 0
        driver = prepare(URL.format(i))
        data = []
        schema = CarSchema()
        today = date.today()
        # rids_met = set()  # Оскільки autoria.com оновлює дані, то може трапитися таке, що ми проглянули машину Х,
        #                   # а поки ми дійшли до кінця поточної сторінки, нові машини витіснили Х на наступну сторінку,
        #                   # і ми знову будемо працювати з Х. З іншого боку, може трапитися таке, що ми обробили Х, 
        #                   # і поки ми працювали з рештою сторінки, Х змінили, і вона з'явилася далі, і тоді ми втратимо
        #                   # змогу оновити в БД запис про Х (але ціною довшої роботи програми). Важко сказати, який підхід
        #                   # кращий чи правильніший. Якщо повторів буде дуже багато, то, звісно, треба кожен запис оброблювати
        #                   # один раз, інакше час роботи виросте в рази. Але повтори трапляються рідко, тому я оновлюю записи
        total = 0
        start = time.time()
        with Session() as session:
            for i in range(pages or int(1e9)):  # pages == або додатній int, або None
                data = []  # зібрані дані усіх машин із поточної сторінки

                if i >= 1:  
                    if not open_url(driver, URL.format(i)):
                        break

                elements = driver.find_elements(By.CLASS_NAME, "m-link-ticket")
                if not elements:
                    break  # більше машин нема, ми закінчили
                
                # викидаємо беззмістовні адреси
                urls = [url for e in elements if not redirect_to_main_page(url := e.get_attribute('href'))]

                # власне скрейпінг
                for url in urls:
                    print(url)

                    try:
                        if not open_url(driver, url):  # якщо раптом сторінка припинила існувати
                            continue
                    except RuntimeError:  # драйвер більше не може відкривати сторінки
                        driver.quit()
                        print('\nDriver refreshing\n')
                        driver = prepare(url)

                    if car_deleted(driver):  # якщо машина вже продана, але ще у фіді із власною сторінкою
                        continue

                    try:
                        # car_data = schema.load(process_car(driver, url))
                        data.append(schema.load(process_car(driver, url)))
                    except NoSuchElementException:  # якщо інша розмітка - пропускаємо цей запис
                        continue


                    # rid = car_data['rid']
                    # if rid in rids_met:
                    #     continue

                    # data.append(car_data)
                    # rids_met.add(rid)

                
                # bulk upsert
                insert_stmt = insert(Car).values(data)
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[Car.rid],
                    set_=build_upsert_dict(FIELDS_TO_UPDATE, insert_stmt)
                )

                session.execute(upsert_stmt)
                session.commit()

                total += len(urls)
                print(f'\nProcessed {total} cars and {i + 1} pages in  {time.time() - start} seconds\n')

            session.execute(delete(Car).where(Car.update_date < today))  # видалити машини, яких уже нема на сайті
            session.commit()

            print(f"Scraping finished successfully\n\tTotal time:  {time.time() - start}\n\tCars scraped:  {total}")

    finally:
        driver.quit()
