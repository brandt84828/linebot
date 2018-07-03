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
    if url.status_code == requests.codes.ok:#檢查有無成功連上
        soup = BeautifulSoup(url.text,'html.parser')
        content=""
        count=1#用來算index
        stories=soup.find_all('a',class_='story-title')#用html直接找
        for s in stories:
            content = content + s.text + "\n\n" + s.get('href') + "\n" #取超連結合成字串 
            if(count==5):
                break
            count=count+1
    return content

def movie():
    url = 'http://www.atmovies.com.tw/movie/next/0/'
    res=requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('ul.filmNextListAll a')):#use css to select
        if index == 20:#取前20的電影
            break;
        title = data.text.replace('\t', '').replace('\r', '')#t歸位 r取消tab
        link = "http://www.atmovies.com.tw" + data['href'] #取出超連結
        content += '{}\n{}\n'.format(title, link)
    return content

def apple_news():
    url='https://tw.appledaily.com/new/realtime'
    res=requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')
    content = ""
    for index, data in enumerate(soup.select('.rtddt a'), 0):#use CSs
        if index == 5:
            break;
        title=data.text[9:]
        link = data['href']#find href 
        content += '{}{}\n'.format(title,link) 
    return content

def technews():
    target_url = 'https://technews.tw/'
    rs = requests.session()#保有cookie
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('article div h1.entry-title a')):
        if index == 10:#取10
            break;
        title = data.text
        link = data['href']#在a標籤內取得˙href
        content += '{}\n{}\n\n'.format(title, link)
    return content

def PttBeauty():
    res=requests.get('https://www.ptt.cc/bbs/Beauty/index.html')
    soup = BeautifulSoup(res.text,'html.parser')
    content=""
    pageweb=soup.find_all('a',class_='btn wide')
    pageweb1=str(pageweb[1].get('href'))
    page=re.search('\d+',pageweb1).group()#利用正則表達抓出數字 group回傳抓到的 默認為0
    for index,data in enumerate(soup.select('.title a'),0):
        if "公告" in data.text:
            break
        title = data.text
        link = "https://www.ptt.cc" + data['href'] #取出超連結
        content += '{}\n{}\n'.format(title, link)
    return content

def beautyimg():
    #目標頁面
    res = requests.get('https://www.ptt.cc/bbs/Beauty/index.html')
    soup = BeautifulSoup(res.text, 'lxml')
    #使用迴圈進入到目標頁面中的每個主題頁面
    imglist=[]
    for article in soup.select('.title a'):
        url = 'https://www.ptt.cc' + article['href']
        if "公告" in article.text:
            break;
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'lxml')
        img=soup.select('.imgur-embed-pub a')
        for item in img:
            imglist.append(item['href'])
        
    return imglist[random.randint(0,len(imglist))] 


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    if event.message.text == "yahoo":
        content = yahoonews()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    
    if event.message.text == "movie":
        content = movie()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    
    if event.message.text == "apple":
        content = apple_news()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0     
    
    if event.message.text == "tech":
        content = technews()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0 
    
    if event.message.text == "pttbeauty":
        content = PttBeauty()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0  
    
    if event.message.text == "draw":
        content = beautyimg()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
