from datetime import datetime, date

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, sessionmaker
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from marshmallow import Schema, fields, validate, post_load

engine = create_engine(f'postgresql+psycopg2://postgres:postgres@localhost/car')

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Car(Base):
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

    # sold_removed: Mapped[bool]
    update_date: Mapped[date]

Base.metadata.create_all(engine)

class CarSchema(Schema):
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

    # sold_removed = fields.Bool(load_only=True, load_default=False)
    update_date = fields.Date(load_default=date.today())

FIELDS_TO_UPDATE = 'url title price_usd username odometer phone_number image_url images_count car_number car_vin update_date'.split()
from pprint import pprint
d = dict(url='url',
         title='title',
         rid='gkfgd',
         price_usd=1500,
         username=None,
         odometer=1000,
         phone_number='+380',
         image_url='image_url',
         images_count=100,
         car_number=None,
         car_vin='berebfiefbli',
        #  datetime_found=datetime.now().isoformat()
         )
s = CarSchema()
pprint(set(s.load(d).keys() - {'datetime_found', 'rid', 'id'})   == set(FIELDS_TO_UPDATE))