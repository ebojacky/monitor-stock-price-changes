import requests
import os
import datetime
from twilio.rest import Client

STOCK = "TSLA"
STOCK_KEY = os.environ['alphavantage_key']
STOCK_URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&" \
            f"symbol={STOCK}" \
            f"&apikey={STOCK_KEY}"


def get_stock_percentage_change():
    stock_response = requests.get(STOCK_URL)
    stock_response.raise_for_status()

    stock_data = (stock_response.json()["Time Series (Daily)"])
    last_two_days = list(stock_response.json()["Time Series (Daily)"])[:2]
    last_two_days_stock_closing = []
    for day in last_two_days:
        last_two_days_stock_closing.append(stock_data[day]["4. close"])
    x = float(last_two_days_stock_closing[0])
    y = float(last_two_days_stock_closing[1])
    return 100 * (x - y) / x


NEWS_SEARCH = "Tesla Inc"
NEWS_API_KEY = os.environ['newsapi_key']
NEWS_DATE = datetime.date.today() - datetime.timedelta(days=1)
NEWS_URL = f"https://newsapi.org/v2/everything?" \
           f"q={NEWS_SEARCH}&" \
           f"apiKey={NEWS_API_KEY}&" \
           f"to={NEWS_DATE}&" \
           f"sortby=relevance"


def get_top_news():
    news_response = requests.get(NEWS_URL)
    news_response.raise_for_status()
    i = 1
    news_dic = {}
    for news in news_response.json()["articles"][:3]:
        news_dic[i] = {"title": news["title"], "description": news["description"], "url": news["url"]}
        i += 1
    return news_dic


ACCOUNT_SID = os.environ['twilio_account_sid']
AUTH_TOKEN = os.environ['twilio_auth_token']
TWILIO_PHONE_NUMBER = os.environ['twilio_virtual_number']
MY_PHONE_NUMBER = os.environ['my_phone_msisdn']


def send_top_news_as_sms(stock_change, news_dic):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for key, news in news_dic.items():
        text = f"{stock_change}\n{news['title']}\n{news['description']}\n{news['url']}"
        print(text)
        message = client.messages.create(
            body=text,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(message.status)


change_in_stock = get_stock_percentage_change()
print(change_in_stock)
if change_in_stock >= 0:
    change_in_stock = "🔺" + str(round(change_in_stock, 2)) + "%"
else:
    change_in_stock = "🔻" + str(round(change_in_stock, 2)) + "%"
print(change_in_stock)

top_news = get_top_news()
print(top_news)
send_top_news_as_sms(change_in_stock, top_news)
