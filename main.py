from flask import Flask
from flask import request, render_template, session as flSession
import alchemy_db
import models_db
from sqlalchemy import select
from sqlalchemy.orm import Session


app = Flask(__name__)
app.secret_key = 'super-puper-secret'


@app.route("/", methods=['GET', 'POST'])
def login_user_1():
    if request.method == 'POST':
        with Session(alchemy_db.engine) as session:
            query = select(models_db.User).filter(models_db.User.username == request.form['username'])
            result = session.execute(query).fetchall()
            if result:
                flSession['username'] = request.form['username']
            else:
                return render_template('index.html', username='Invalid username or password')
            return render_template('index.html', username=flSession['username'])
    else:
        return render_template('login_form.html')


@app.route("/login", methods=['GET', 'POST'])
def login_user_2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return f"Hello {username}! Please complete the registration"

    return render_template('login_form.html')


@app.route("/logout", methods=['GET'])
def logout():
    flSession.pop('username', None)
    return "Logout is completed"


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        with Session(alchemy_db.engine) as session:
            record = models_db.User(username=username,
                                    password=password,
                                    email=email,
                                    first_name=first_name,
                                    last_name=last_name,
                                    )
            session.add(record)
            session.commit()

        return "Registration is successful"

    return render_template('registration_form.html')


@app.route("/user_page", methods=['GET'])
def index():
    if 'username' in flSession:
        return f'Logged in as {flSession["username"]}'
    return 'You are not logged in'


@app.route("/currency", methods=['GET', 'POST'])
def currency_converter():
    buy_rate = 4
    sale_rate = 5
    if request.method == 'POST':
        user_bank = request.form['bank']
        user_currency_1 = request.form['currency_1']
        user_date = request.form['date']
        user_currency_2 = request.form['currency_2']

        with Session(alchemy_db.engine) as session:
            statement_1 = select(models_db.DB_model).filter_by(bank=user_bank, date_exchange=user_date,
                                                               currency=user_currency_1)
            user_request_1 = session.scalars(statement_1).all()
            statement_2 = select(models_db.DB_model).filter_by(bank=user_bank, date_exchange=user_date,
                                                               currency=user_currency_2)
            user_request_2 = session.scalars(statement_2).all()

        buy_rate_1, sale_rate_1 = user_request_1[buy_rate], user_request_1[sale_rate]
        buy_rate_2, sale_rate_2 = user_request_2[buy_rate], user_request_2[sale_rate]
        cur_exchange_buy = round(buy_rate_2 / buy_rate_1, 2)
        cur_exchange_sale = round(sale_rate_2 / sale_rate_1, 2)

        return render_template('form.html',
                               cur_exchange_buy=cur_exchange_buy,
                               cur_exchange_sale=cur_exchange_sale,
                               user_currency_1=user_currency_1,
                               user_currency_2=user_currency_2,
                               username=flSession['username'],
                               )
    else:
        return render_template('form.html', username=flSession['username'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
