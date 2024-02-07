import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, FollowEvent, UnfollowEvent, StickerSendMessage
import requests
from bs4 import BeautifulSoup
import re
from io import BytesIO
import psycopg2
from PIL import Image
from flask import Flask, request, abort
import os

# チャネルアクセストークン
CH_TOKEN = os.environ["CH_TOKEN"]
# チャネルシークレット
CH_SECRET = os.environ["CH_SECRET"]
# 天気予報URL
CITY_WEATHER_URLS = {
    "大阪": "https://tenki.jp/forecast/6/30/6200/27100/",
    "東京": "https://tenki.jp/forecast/3/16/4410/13101/",
    "名古屋": "https://tenki.jp/forecast/5/26/5110/23100/",
    "仙台": "https://tenki.jp/forecast/2/7/3410/4100/",
    "福岡": "https://tenki.jp/forecast/9/43/8210/40130/",
    "札幌": "https://tenki.jp/forecast/1/2/1400/1100/",
    "那覇": "https://tenki.jp/forecast/10/50/9110/47201/",
    "高知": "https://tenki.jp/forecast/8/42/7410/39201/"
    # 他の地域も必要に応じて追加
}
# 後ほどHerokuでPostgreSQLデータベースURLを取得
DATABASE_URL = os.environ["DATABASE_URL"]
# 後ほど作成するHerokuアプリ名
HEROKU_APP_NAME = os.environ["HEROKU_APP_NAME"]

app = Flask(__name__)
Heroku = "https://{}.herokuapp.com/".format(HEROKU_APP_NAME)

line_bot_api = LineBotApi(CH_TOKEN)
handler = WebhookHandler(CH_SECRET)

header = {
    "Content_Type": "application/json",
    "Authorization": "Bearer " + CH_TOKEN
}

# テスト用
@app.route("/")
def hello_world():
    return "hello world!"

# アプリにPOSTがあったときの処理
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# データベース接続
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# botがフォローされたときの処理
@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    with get_connection() as conn:
        with conn.cursor() as cur:
            conn.autocommit = True
            cur.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT)')
            cur.execute('INSERT INTO users (user_id) VALUES (%s)', [profile.user_id])
            print('userIdの挿入OK!!')
            cur.execute('SELECT * FROM users')
            db = cur.fetchall()
    print("< データベース一覧 >")
    for db_check in db:
        print(db_check)


# botがアンフォロー(ブロック)されたときの処理
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    with get_connection() as conn:
        with conn.cursor() as cur:
            conn.autocommit = True
            cur.execute('DELETE FROM users WHERE user_id = %s', [event.source.user_id])
    print("userIdの削除OK!!")

def get_page_info(city):
    """ 読み込みページ情報取得(URLにリクエストしてBeautifulSoupで整形) """
    url = CITY_WEATHER_URLS.get(city)
    if not url:
        return None  # 対応するURLがない場合はNoneを返すなどの対応が必要
    res = requests.get(url)
    html = res.text.encode(res.encoding)
    soup = BeautifulSoup(html, 'lxml')

    return soup

def get_weather_info(soup):
    """ 今日明日の天気予報dict情報の取得 """

    #今日明日の天気リスト
    weather_list = []

    # 今日の天気------------------------------------
    today_weather = {}
    section = soup.find("section", "today-weather")
    # 今日の日付
    today_section = section.find("h3", "left-style").contents
    today_weather["date_info"] = re.sub("¥xa0", " ", f"{today_section[0]} {today_section[1].text}")
    # 今日の天気
    today_weather["weather"] = section.find("p", "weather-telop").text
    # 最高気温
    today_weather["high_temperature"] = section.find("dd", "high-temp temp").text
    # 最低気温
    today_weather["low_temperature"] = section.find("dd", "low-temp temp").text
    # 降水確率
    today_weather["prob_midnight"] = section.select('.rain-probability > td')[0].text
    today_weather["prob_morning"] = section.select('.rain-probability > td')[1].text
    today_weather["prob_afternoon"] = section.select('.rain-probability > td')[2].text
    today_weather["prob_night"] = section.select('.rain-probability > td')[3].text
    # 今日明日の天気リストの格納
    weather_list.append(today_weather)

    # 明日の天気------------------------------------
    tomorrow_weather = {}
    # 明日の天気セクション
    section = soup.find("section", "tomorrow-weather")
    today_section = section.find("h3", "left-style").contents
    tomorrow_weather["date_info"] = re.sub("\xa0", " ", f"{today_section[0]} {today_section[1].text}")
    # 明日の天気
    tomorrow_weather["weather"] = section.find("p", "weather-telop").string
    # 最高気温
    tomorrow_weather["high_temperature"] = section.find("dd", "high-temp temp").text
    # 最低気温
    tomorrow_weather["low_temperature"] = section.find("dd", "low-temp temp").text
    # 降水確率
    tomorrow_weather["prob_midnight"] = section.select('.rain-probability > td')[0].text
    tomorrow_weather["prob_morning"] = section.select('.rain-probability > td')[1].text
    tomorrow_weather["prob_afternoon"] = section.select('.rain-probability > td')[2].text
    tomorrow_weather["prob_night"] = section.select('.rain-probability > td')[3].text
    # 今日明日の天気リストの格納
    weather_list.append(tomorrow_weather)

    return weather_list

def create_msg(weather_title, weather_list):
    """ LINE BOT メッセージ作成 """

    # メッセージタイトル
    msg_title = "⭐️" + weather_title + "⭐️"

    # BOTメッセージフォーマット
    msg_format = """
        {0}
        天気                   ： {1}
        最高気温(℃)             ： {2}
        最低気温(℃)             ： {3}
        降水確率[0~6時]       ： {4}
        降水確率[6~12時]     ： {5}
        降水確率[12~18時]   ： {6}
        降水確率[18~24時]   ： {7}
    """

    msg = ""
    for weather in weather_list:
        msg += msg_format.format(
            weather["date_info"],
            weather["weather"],
            weather["high_temperature"],
            weather["low_temperature"],
            weather["prob_midnight"],
            weather["prob_morning"],
            weather["prob_afternoon"],
            weather["prob_night"]
        )
    bot_msg = msg_title + msg

    return bot_msg

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    #入力された文字を取得
    text_in = event.message.text

    # デバッグログ
    print(f"Received message: {text_in}")

    # 登録処理
    if any(city in text_in for city in CITY_WEATHER_URLS):
        for city, url in CITY_WEATHER_URLS.items():
            if city in text_in:
                profile = line_bot_api.get_profile(event.source.user_id)
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        conn.autocommit = True
                        # ユーザーが異なる都市を持つためのテーブル作成
                        cur.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY, city TEXT)')
                        cur.execute('INSERT INTO users (user_id, city) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET city = EXCLUDED.city', [profile.user_id, city])
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{city}を登録しました！"))
                break

    # 天気予報取得処理
    elif "天気" in text_in or "予報" in text_in:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT city FROM users WHERE user_id = %s', [event.source.user_id])
                city = cur.fetchone()
                if city:
                    city = city[0]
                    soup = get_page_info(city)
                    if soup:
                        # ページタイトル
                        page_title = soup.title.text
                        m = re.search(".*天気", page_title)
                        weather_title = m.group(0)
                        # 今日明日の天気予報情報
                        weather_list = get_weather_info(soup)
                        # LINE BOTメッセージ
                        msg = create_msg(weather_title, weather_list)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="天気情報の取得に失敗しました。"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="まずは「大阪市 登録」などで地域を登録してください。"))

    # 地域一覧取得
    elif text_in == "地域一覧":
        # 登録できる地域の一覧を表示
        cities_list = "\n".join(CITY_WEATHER_URLS.keys())
        reply_msg = f"登録できる地域の一覧:\n{cities_list}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    # 使い方
    elif text_in == "使い方":
        # 使い方の説明メッセージを表示
        usage_msg = (
            "使い方\n"
            "1. 登録したい地域を送信\n"
            "2. 天気を含む文章を送信\n"
            "3. 登録した地域の天気予報が送信される\n\n"
            "登録できる地域は「地域一覧」と送信できます"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=usage_msg))

    # それ以外の場合
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="天気予報以外は答えられません😭"))


if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host="0.0.0.0",port=port)