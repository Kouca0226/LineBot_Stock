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
    if '股票 ' in message:
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
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

#主程式
import os 
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)