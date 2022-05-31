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

app = Flask(__name__)

line_bot_api = LineBotApi('rBdXfRQqtY6avy9CJ3Ttenas9mkSoBGquP/qISdSUDfaDIndkKWlDRe4uvz2T5PKJ3f9EbfilzJB7n6Mn5oF//xZtBF5KQEhOdFFuUlgaqJ8LZ1McPOuCzrB9hOZuqLeT0cF+5zd1ZdnH+2gUuXsrgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f40eb4fe030cdece35f592631b9e184a')
line_bot_api.push_message('U82a41664b4a103c31ae2be046358f484', TextSendMessage(text='你可以開始了'))

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
        buttons_template_message = TemplateSendMessage(
        alt_text = "股票資訊",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title = message + " 股票資訊",
                    text ="請點選想查詢的股票資訊",
                    actions =[
                        MessageAction(
                            label= message[3:] + " 個股資訊",
                            text= "個股資訊 " + message[3:]),
                        MessageAction(
                            label= message[3:] + " 個股新聞",
                            text= "個股新聞 " + message[3:])
                    ]
                ),
                CarouselColumn(
                    title = message[3:] + " 股票資訊",
                    text ="請點選想查詢的股票資訊",
                    actions =[
                        MessageAction(
                            label= message[3:] + " 最新分鐘圖",
                            text= "最新分鐘圖 " + message[3:]),
                        MessageAction(
                            label= message[3:] + " 日線圖",
                            text= "日線圖 " + message[3:]),
                    ]
                ),
                CarouselColumn(
                    title = message[3:] + " 股利資訊",
                    text ="請點選想查詢的股票資訊",
                    actions =[
                        MessageAction(
                            label= message[3:] + " 平均股利",
                            text= "平均股利 " + message[3:]),
                        MessageAction(
                            label= message[3:] + " 歷年股利",
                            text= "歷年股利 " + message[3:])
                    ]
                ),
            ]
        )
    )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    elif '大戶籌碼 ' in message:
        flex_message = TextSendMessage(text="請選擇要顯示的買賣超資訊",
                                quick_reply=QuickReply(items=[
                                QuickReplyButton(action=MessageAction(label="最新法人", text="最新法人買賣超 " + message[5:])),
                                QuickReplyButton(action=MessageAction(label="歷年法人", text="歷年法人買賣超 " + message[5:])),
                                QuickReplyButton(action=MessageAction(label="外資", text="外資買賣超 " + message[5:])),
                                QuickReplyButton(action=MessageAction(label="投信", text="投信買賣超 " + message[5:])),
                                QuickReplyButton(action=MessageAction(label="自營商", text="自營商買賣超 " + message[5:])),
                                QuickReplyButton(action=MessageAction(label="三大法人", text="三大法人買賣超 " + message[5:]))
                            ]))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif '# ' in message:
        line_bot_api.reply_message(event.reply_token, message[1:])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("錯誤指令\n請輸入「help」查詢"))

def get_stock(stockn):
    url = "https://tw.stock.yahoo.com/quote/" + stockn
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'lxml')

    # 找到區塊
    title1 = sp.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)').text
    title2 = sp.find('span', class_='C($c-icon) Fz(24px) Mend(20px)').text
    title = ("%s(%s)" %(title1, title2))

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
    
    out = ("%s\n%s\n%s" %(title, price, t))
    return (out)
#主程式
import os 
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)