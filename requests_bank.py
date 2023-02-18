import requests
import datetime
from sqlalchemy.orm import Session
import alchemy_db
import models_db


def get_privatbank_data():
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    db_date = datetime.datetime.now().strftime('%Y-%m-%d')
    r = requests.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={current_date}')

    currency_info = r.json()

    saleRate_USD = 0
    purchaseRate_USD = 0

    for c in currency_info['exchangeRate']:
        if c['currency'] == 'USD':
            saleRate_USD = c['saleRate']
            purchaseRate_USD = c['purchaseRate']

    with Session(alchemy_db.engine) as session:
        for c in currency_info['exchangeRate']:
            currency_name = c['currency']
            if c.get('saleRate'):
                saleRate_currency = c['saleRate'] / saleRate_USD
                purchaseRate_currency = c['purchaseRate'] / purchaseRate_USD
                print(f'{currency_name} {saleRate_currency} {purchaseRate_currency}')
                record = models_db.DB_model(
                    bank='PrivatBank',
                    currency=currency_name,
                    date_exchange=db_date,
                    buy_rate=purchaseRate_currency,
                    sale_rate=saleRate_currency,
                )
                session.add(record)
                session.commit()

        UAH = models_db.DB_model(
            bank='PrivatBank',
            currency='UAH',
            date_exchange=db_date,
            buy_rate=1 / purchaseRate_USD,
            sale_rate=1 / saleRate_USD,
        )
        session.add(UAH)
        session.commit()
