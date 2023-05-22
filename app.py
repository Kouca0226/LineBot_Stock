#載入LineBot所需要的模組
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests
from bs4 import BeautifulSoup
import pandas as pd
import twstock

app = Flask(__name__)

line_bot_api = LineBotApi('rBdXfRQqtY6avy9CJ3Ttenas9mkSoBGquP/qISdSUDfaDIndkKWlDRe4uvz2T5PKJ3f9EbfilzJB7n6Mn5oF//xZtBF5KQEhOdFFuUlgaqJ8LZ1McPOuCzrB9hOZuqLeT0cF+5zd1ZdnH+2gUuXsrgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('233ca46476caadae5a8393607276921a')
line_bot_api.push_message('U82a41664b4a103c31ae2be046358f484', TextSendMessage(text='程式運行中\n在股票名稱或代碼前加上「股票 」即可查詢\n(ex.股票 台積電 or 股票 2330)'))

data = {"台積電":"2330"}

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#訊息傳遞區塊
import re
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = text = event.message.text
    if "股票 " in message:
        flex_message = TextSendMessage(text="請選擇相關資訊",
                                quick_reply=QuickReply(items=[
                                QuickReplyButton(action=MessageAction(label="基本資料", text="基本資料 " + message[3:])),
                                QuickReplyButton(action=MessageAction(label="相關新聞", text="相關新聞 " + message[3:])),
                                QuickReplyButton(action=MessageAction(label="個股公告", text="個股公告 " + message[3:]))
                                ]))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif '基本資料 ' in message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(price(message[5:])))
    elif '相關新聞 ' in message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(news(message[5:])))
    elif '個股公告 ' in message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(announcement(message[5:])))
    elif '#' in message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(str(data)))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("錯誤指令\n(ex.股票 台積電 or 股票 2330)"))

def price(inp):
    try:
        try:
            out = get_stock(get_stockid(inp))
        except:
            out = get_stock(inp)
    except:
        return "查無此股票"
    return out
def news(inp):
    try:
        try:
            out = get_news(get_stockid(inp))
        except:
            out = get_news(inp)
    except:
        return "查無此股票"
    return out

def announcement(inp):
    try:
        try:
            out = get_announcement(get_stockid(inp))
        except:
            out = get_announcement(inp)
    except:
        return "查無此股票"
    return out

def get_stock(id):
    stock = twstock.realtime.get(id)
    stock1 = twstock.Stock(id)
    rate = round((float(stock['realtime']['latest_trade_price'])/float(stock1.price[-2])-1)*100, 2)
    if (rate<0):
      f = "下跌"
      rate = -rate
    elif (rate>0):
      f = "上漲"
    else:
      f = "平盤"
    if (stock['success']):
        return "股票名稱：" + stock['info']['name'] + "\n股票代碼：" + stock['info']['code'] + "\n公司全名：" + stock['info']['fullname'] + "\n即時股價：" + stock['realtime']['latest_trade_price'] + str("\n走勢：%s%.2f"%(f, rate)) + "%\n開盤價：" + stock['realtime']['open'] + "\n最高價：" + stock['realtime']['high'] + "\n最低價：" + stock['realtime']['low'] + "\n總成交量：" + stock['realtime']['accumulate_trade_volume'] + "張"
    else:
        return "查無此股票"

def get_stockid(name):
    url = 'https://isin.twse.com.tw/isin/single_main.jsp?owncode=&stockname=' + name
    r = requests.get(url)
    if(name in data):
        return data.get(name)
    try:
        df = pd.read_html(r.text)
        n = 0
        while(1):
            if(df[0][3][n] == name):
                data.setdefault(name, df[0][2][n])
                return df[0][2][n]
            else :
                n += 1
    except:
        return "查無此股票"
def get_news(id):
    content = ""
    url = "https://tw.stock.yahoo.com/quote/"+ id +"/news"
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'lxml')
    data = sp.find_all("a", {"class": "Fw(b) Fz(20px) Fz(16px)--mobile Lh(23px) Lh(1.38)--mobile C($c-primary-text)! C($c-active-text)!:h LineClamp(2,46px)!--mobile LineClamp(2,46px)!--sm1024 mega-item-header-link Td(n) C(#0078ff):h C(#000) LineClamp(2,46px) LineClamp(2,38px)--sm1024 not-isInStreamVideoEnabled"}, limit= 5)
    for d in data:
        title = d.text
        href = d.get("href")
        content += "{}\n{}\n".format(title, href)
    
    return content

def get_announcement(id):
    content = ""
    url = "https://tw.stock.yahoo.com/quote/"+ id +"/announcement"
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'lxml')
    data = sp.find_all("a", {"class": "Fw(b) Fz(20px) Fz(16px)--mobile Lh(23px) Lh(1.38)--mobile C($c-primary-text)! C($c-active-text)!:h LineClamp(2,46px)!--mobile LineClamp(2,46px)!--sm1024 mega-item-header-link Td(n) C(#0078ff):h C(#000) LineClamp(2,46px) LineClamp(2,38px)--sm1024 not-isInStreamVideoEnabled"}, limit = 5)
    for d in data:
        title = d.text
        href = d.get("href")
        content += "{}\n{}\n".format(title, href)
    
    return content

#主程式
import os 
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)