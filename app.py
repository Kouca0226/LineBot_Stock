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

app = Flask(__name__)

line_bot_api = LineBotApi('rBdXfRQqtY6avy9CJ3Ttenas9mkSoBGquP/qISdSUDfaDIndkKWlDRe4uvz2T5PKJ3f9EbfilzJB7n6Mn5oF//xZtBF5KQEhOdFFuUlgaqJ8LZ1McPOuCzrB9hOZuqLeT0cF+5zd1ZdnH+2gUuXsrgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f40eb4fe030cdece35f592631b9e184a')
line_bot_api.push_message('U82a41664b4a103c31ae2be046358f484', TextSendMessage(text='程式運行中\n在股票名稱或代碼前加上「股票 」即可查詢\n(ex.股票 台積電)'))

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
                                QuickReplyButton(action=MessageAction(label="及時股價", text="及時股價 " + message[3:]))
                                ]))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif '及時股價 ' in message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(price(message[5:])))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("錯誤指令\n(ex.股票 台積電)"))

def price(inp):
    try:
        try:
            out = get_stock(get_stockid(inp))
        except:
            out = get_stock(inp)
    except:
        return "查無此股票"
    return out

def get_stock(stockn):
    url = "https://tw.stock.yahoo.com/quote/" + stockn
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'lxml')

    # 找到區塊
    title1 = sp.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)').text
    title2 = sp.find('span', class_='C($c-icon) Fz(24px) Mend(20px)').text
    title = ("%s(%s)" %(title1, title2))

    try:
        data = sp.find('div', class_='D(f) Ai(fe) Mb(4px)')
        if (str(data)[100] == 'u'):
            trend = 'up'
        else:
            trend = 'down'
        price1 = sp.find('span', class_='Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-'+ trend +')').text
        price = ('即時股價：'+price1)
        percent = sp.find('span', class_='Jc(fe) Fz(20px) Lh(1.2) Fw(b) D(f) Ai(c) C($c-trend-'+ trend +')').text
        dprice = sp.find('span', class_='Fz(20px) Fw(b) Lh(1.2) Mend(4px) D(f) Ai(c) C($c-trend-'+ trend +')').text
        if (trend == 'up'):
            t = ("走勢：上漲%s %s" %(dprice ,percent))
        else:
            t = ("走勢：下跌%s %s" %(dprice ,percent))
    except:
        price = sp.find('span', class_='Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c)').text
        price = ('即時股價：'+price)

        percent = sp.find('span', class_='Jc(fe) Fz(20px) Lh(1.2) Fw(b) D(f) Ai(c)').text
        dprice = sp.find('span', class_='Fz(20px) Fw(b) Lh(1.2) Mend(4px) D(f) Ai(c)').text
        t = ("走勢：平盤%s %s" %(dprice ,percent))
    
    out = ("%s\n%s\n%s" %(title, price, t))
    return (out)

def get_stockid(name):
    url = 'https://isin.twse.com.tw/isin/single_main.jsp?owncode=&stockname=' + name
    r = requests.get(url)
    try:
        df = pd.read_html(r.text)
        n = 0
        while(1):
            if(df[0][3][n] == name):
                return df[0][2][n]
            else :
                n += 1
    except:
        return "查無此股票"

#主程式
import os 
if __name__ == "__main__":
    while(1):
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)