import os

from datetime import date

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from marshmallow import Schema, fields

from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv  ("DB_USER", 'postgres')
db_passwd = os.getenv("DB_PASSWD", 'postgres')
db_host = os.getenv  ("DB_HOST", 'localhost')
db_port = os.getenv  ("DB_PORT", '5432')
db_name = os.getenv  ("DB_NAME", 'car')

db_url = f'{db_user}:{db_passwd}@{db_host}:{db_port}/{db_name}'
engine = create_engine('postgresql+psycopg2://' + db_url)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Car(Base):
    """Поле `rid` - це унікальний ідентифікатор ТЗ, який міститься в його url. Наприклад,
    у цієї машини
     
    https://auto.ria.com/uk/auto_bmw_x5_35943113.html
    
    `rid == 35943113`.

    Насправді, звісно, це моє припущення, що це число відіграє роль первинного ключа в БД
    AutoRia, але я майже переконаний, що це так (принаймні, я не бачив, аби порушувалося вимога
    унікальності в моїй БД). Потреба в `rid` пояснюється тим, що всі потрібні поля (назва, vin-код тощо)
    можуть мінятися, повторюватися чи бути відсутніми, і тому може бути проблема, що нам треба оновити запис, але ми не
    можемо його оновити в БД, бо не зрозуміло, по якому полю цей запис шукати - і саме `rid` грає цю роль.
    Можна було б взяти кілька полів, і їх оголосити унікальними, але це гірший підхід.
    """
    __tablename__ = 'car'

    id: Mapped[int] = mapped_column(primary_key=True)
    rid: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]
    title: Mapped[str]
    price_usd: Mapped[int]
    username: Mapped[Optional[str]]
    odometer: Mapped[int]
    phone_number: Mapped[str]
    image_url: Mapped[str]
    images_count: Mapped[int]
    car_number: Mapped[Optional[str]]
    car_vin: Mapped[Optional[str]]
    datetime_found: Mapped[date]

    update_date: Mapped[date]  # остання дата оновлення запису


Base.metadata.create_all(engine)


class CarSchema(Schema):
    """Строго кажучи, без схеми можна було б обійтися, бо поля витягуються в `process_car`,
    і їх не потрібно модифікувати. Але схема видасть помилку, якщо якесь required поле відсутнє"""

    id = fields.Int(dump_only=True)
    rid = fields.Str(required=True)
    url = fields.Str(required=True)
    title = fields.Str(required=True)
    price_usd = fields.Int(required=True)
    username = fields.Str(allow_none=True)
    odometer = fields.Int(required=True)
    phone_number = fields.Str(required=True)
    image_url = fields.Str(required=True)
    images_count = fields.Int(required=True)
    car_number = fields.Str(allow_none=True)
    car_vin = fields.Str(allow_none=True)
    datetime_found = fields.Date(load_default=date.today())

    update_date = fields.Date(load_default=date.today())

# Поля, які оновлюємо в UDPATE частині UPSERT
FIELDS_TO_UPDATE = 'url title price_usd username odometer phone_number image_url images_count car_number car_vin update_date'.split()

