from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re

from time import sleep 
from pprint import pprint
from datetime import date

from sqlalchemy.dialects.postgresql import insert, Insert
from sqlalchemy import delete

from model import Session, Car, CarSchema, FIELDS_TO_UPDATE

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
    return {f: getattr(stmt.excluded, f) for f in fields}

SERVICE = Service(r'D:\WebDrivers\geckodriver.exe')
URL = 'https://auto.ria.com/uk/car/used/{}'
# URL = 'https://auto.ria.com/uk/last/hour/{}'  # TODO
URL = 'https://auto.ria.com/uk/search/?indexName=auto&country.import.usa.not=-1&price.currency=1&top=1&abroad.not=-1&custom.not=-1&page={}&size=10&scrollToAuto=33294971'  # TODO
options = Options()
options.add_argument('--headless')


def prepare():
    driver = webdriver.Firefox(service=SERVICE, options=options)

    driver.get(URL.format(0))  # TODO:
    cookies_ok_button = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='c-notifier-close']"))
    )
    cookies_ok_button.click()

    return driver


def process_car(driver: webdriver.Firefox, car_url) -> dict:
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
            p = driver.find_element(By.CLASS_NAME, "price_value--additional").text
    except NoSuchElementException:
        p = driver.find_element(By.ID, "sidePrice").find_element(By.CSS_SELECTOR, "strong.common-text.titleL").text
    data['price_usd'] = _get_price(p)

    try:
        try:
            od = driver.find_element(By.CLASS_NAME, "base-information").text
            # number = odometer_element.find_element(By.TAG_NAME, "span").text
            # data['odometer'] = number + ' ' + odometer_element.text
        except NoSuchElementException:
            od = driver.find_element(By.ID, "basicInfoTableMainInfoLeft0") \
                        .find_element(By.CSS_SELECTOR, "span.common-text.body").text
    except NoSuchElementException:
        od = 0
    data['odometer'] = _get_first_num(od)


    try:
        data['username'] = driver.find_element(By.CLASS_NAME, "seller_info_name").text.strip()
    except NoSuchElementException:
        data['username'] = driver.find_element(By.ID, "sellerInfoUserName").find_element(By.CSS_SELECTOR, "span.common-text.titleM").text.strip()

    # data['image_url'] = driver.find_element(By.CLASS_NAME, "outline m-auto").get_attribute('src')
    try:
        data['image_url'] = driver.find_element(By.CSS_SELECTOR, "img.outline.m-auto").get_attribute('src')
    except NoSuchElementException:
        data['image_url'] = driver.find_element(By.CLASS_NAME, "carousel-wrapper") \
                                .find_element(By.TAG_NAME, "img") \
                                .get_attribute('src')

    # data['images_count'] = driver.find_element(By.CLASS_NAME, "show-all link-dotted").text
    # data['images_count'] = driver.find_element(By.CSS_SELECTOR, "a.show-all.link-dotted").text
    try:
        try:
            ic = driver.find_element(By.CSS_SELECTOR, "a.show-all.link-dotted").text
        except NoSuchElementException:
            ic = driver.find_element(By.XPATH, '//*[@id="photosBlock"]/div[1]/div[2]/span/span[2]').text
    except NoSuchElementException:
        try:
            ic = driver.find_element(By.CLASS_NAME, "carousel-wrapper") \
                                        .find_element(By.CSS_SELECTOR, "span.common-badge.alpha.medium") \
                                        .find_elements(By.TAG_NAME, "span")[-1].text
        except NoSuchElementException:
            ic = 0  # TODO
    data['images_count'] = _get_first_num(ic)

    try:
        try:
            data['car_number'] = driver.find_element(By.CSS_SELECTOR, "span.state-num.ua").text
        except NoSuchElementException:
            data['car_number'] = driver.find_element(By.CSS_SELECTOR, "div.car-number.ua") \
                                    .find_element(By.TAG_NAME, "span").text.strip()
    except NoSuchElementException:
        data['car_number'] = None

    try:
        try:
            # data['car_vin'] = driver.find_element(By.CLASS_NAME, "label-vin").text
            data['car_vin'] = driver.find_element(By.CSS_SELECTOR, "span.label-vin").text
        except NoSuchElementException:
            # data['car_vin'] = driver.find_element(By.CLASS_NAME, "vin-code").text
            data['car_vin'] = driver.find_element(By.CSS_SELECTOR, "span.vin-code").text
    except NoSuchElementException:
        try:
            data['car_vin'] = driver.find_element(By.ID, "badgesVin") \
                                    .find_element(By.TAG_NAME, "span").text
        except NoSuchElementException:
            data['car_vin'] = None

    try: 
        show_phone_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "phone_show_link")))
        show_phone_button.click()

        # Беремо тільки перший номер телефону
        ph = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popup-successful-call-desk"))
        ).text

    except NoSuchElementException:
        show_phone_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "sl.conversion")))
        show_phone_button.click()

        # Беремо тільки перший номер телефону
        phone_popup = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popup-inner"))
        )

        ph = phone_popup.find_element(By.TAG_NAME, "span").text
    data["phone_number"] = _get_phone_number(ph)

    return data

def main():
    try:
        driver = prepare()
        i = 0
        data = []
        schema = CarSchema()
        today = date.today()
        rids_met = set()
        with Session.begin() as session:
            while True:
                data = []
                # if i == 4: break  # TODO: REMOVE

                if i == 1:  # TODO
                    btn = driver.find_element(By.ID, "paginationChangeSize")
                    btn.click()

                    show_max = driver.find_elements(By.ID, "paginationSizeOptions")[-1]  # TODO
                    show_max.click()
                elif i > 1:
                    driver.get(URL.format(f'?page={i + 1}'))
                    try:
                        driver.find_element(By.CLASS_NAME, "contains-404")
                    except NoSuchElementException:
                        pass
                    else:
                        break

                i += 1

                elements = driver.find_elements(By.CLASS_NAME, "m-link-ticket")
                if not elements:  # TODO
                    break

                urls = [e.get_attribute('href') for e in elements]
                print('\n', f'Urls len:  {len(urls)}')
                print('\n', f'Set  len:  {len(set(urls))}', '\n')
                for url in urls:
                    driver.get(url)
                    raw_data = process_car(driver, url)
                    pprint(raw_data)
                    data.append(schema.load(raw_data))
                    rid = data[-1]['rid']
                    if rid in rids_met:
                        continue

                    rids_met.add(data[-1]['rid'])

                    # pprint(data)
                
                # upsert
                insert_stmt = insert(Car).values(data)
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[Car.rid],
                    set_=build_upsert_dict(FIELDS_TO_UPDATE, insert_stmt)
                )

                session.execute(upsert_stmt)
                
            session.execute(delete(Car).where(Car.update_date < today))

    finally:
        driver.quit()


from subprocess import PIPE,Popen

def dump_database(host_name, database_name, user_name, database_password):
    command = r'"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -h {0} -d {1} -U {2} -p 5432 -Fc -f database.dmp'\
    .format(host_name, database_name, user_name)
    p = Popen(command, shell=True, stdin=PIPE)
    return p.communicate('{}'.format(database_password).encode())

main()
dump_database('localhost', 'car', 'postgres', 'postgres')