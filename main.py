import json
from linebot import LineBotApi
from linebot.models import TextSendMessage
import requests
from bs4 import BeautifulSoup
import re

# 設定情報読み込み
with open("settings.json", encoding="utf-8") as f:
    res = json.load(f)

# チャネルアクセストークン
CH_TOKEN = res["CH_TOKEN"]
# userID
USER_ID = res["USER_ID"]
# 天気予報URL
URL = "https://tenki.jp/forecast/5/26/5110/23100/"

def get_page_info():
    """ 読み込みページ情報取得(URLにリクエストしてBeautifulSoupで整形) """
    res = requests.get(URL)
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
        天気                     ： {1}
        最高気温(℃)              ： {2}
        最低気温(℃)              ： {3}
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

def main():
    """ LINE BOTメイン処理 """

    # 天気予報ページ情報取得
    soup = get_page_info()

    # ページタイトル
    page_title = soup.title.text
    m = re.search(".*天気", page_title)
    weather_title = m.group(0) # 名古屋市の今日明日の天気

    # 今日明日の天気予報情報
    weather_list = get_weather_info(soup)

    # LINE BOTメッセージ
    msg = create_msg(weather_title, weather_list)
    messages = TextSendMessage(text=msg)
    line_bot_api = LineBotApi(CH_TOKEN)
    line_bot_api.push_message(USER_ID, messages=messages)

if __name__ == "__main__":
    main()