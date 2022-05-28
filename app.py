#載入LineBot所需要的模組
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('rBdXfRQqtY6avy9CJ3Ttenas9mkSoBGquP/qISdSUDfaDIndkKWlDRe4uvz2T5PKJ3f9EbfilzJB7n6Mn5oF//xZtBF5KQEhOdFFuUlgaqJ8LZ1McPOuCzrB9hOZuqLeT0cF+5zd1ZdnH+2gUuXsrgdB04t89/1O/w1cDnyilFU=')

# 必須放上自己的Channel Secret
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
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token,message)

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
                    thumbnail_image_url ="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.businesstoday.com.tw%2Farticle%2Fcategory%2F80402%2Fpost%2F201903070027%2F&psig=AOvVaw2hAu8vUyuViCXrbJiy3jMo&ust=1653827300633000&source=images&cd=vfe&ved=0CAwQjRxqFwoTCLi_5_qYgvgCFQAAAAAdAAAAABAD",
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
                    thumbnail_image_url ="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.businesstoday.com.tw%2Farticle%2Fcategory%2F80402%2Fpost%2F201903070027%2F&psig=AOvVaw2hAu8vUyuViCXrbJiy3jMo&ust=1653827300633000&source=images&cd=vfe&ved=0CAwQjRxqFwoTCLi_5_qYgvgCFQAAAAAdAAAAABAD",
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
                    thumbnail_image_url ="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.businesstoday.com.tw%2Farticle%2Fcategory%2F80402%2Fpost%2F201903070027%2F&psig=AOvVaw2hAu8vUyuViCXrbJiy3jMo&ust=1653827300633000&source=images&cd=vfe&ved=0CAwQjRxqFwoTCLi_5_qYgvgCFQAAAAAdAAAAABAD",
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
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
#主程式
import os 
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)