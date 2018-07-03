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

def apple_news():
    target_url = 'https://tw.appledaily.com/new/realtime'
    print('Start parsing appleNews....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('.rtddt a'), 0):
        if index == 5:
            return content
        link = data['href']
        content += '{}\n\n'.format(link)
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)#event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        message)
    if event.message.text == "蘋果即時新聞":
        content = apple_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
