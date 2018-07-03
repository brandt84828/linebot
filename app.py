import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)
#git add .
#git commit -am "make it better"
#git push heroku master


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('PtqO0jaXvr1db2hQA441OTQ00sPEnj579B5fKJhQRachyyXa86WyMdKLwYhjOdAVyRFyE2vykS5ofXgVseUBu9mWhyPMCWZpryasr2IyQyp9qDz+2lCQZrrCwsLgzY87qbqPULLfNaBGfXgmAajdmAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('7a6685fc2f39b661c6140fbe4918b534')

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

def yahoonews():
    url = requests.get('https://tw.yahoo.com/')
    if url.status_code == requests.codes.ok:
        soup = BeautifulSoup(url.text,'html.parser')
        content=""
        count=1
        stories=soup.find_all('a',class_='story-title')
        for s in stories:
            content = content + s.text + "\n" + s.get('href') + "\n" 
            if(count==5):
                break
            count=count+1
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    if event.message.text == "yahoonews":
        content = yahoonews()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    if event.message.text == "yahoo":
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text="yahhhhhh"))
       

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
