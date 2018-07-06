import requests
import re
from bs4 import BeautifulSoup
import random
import time
import json
import configparser
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
from linebot.models import *
#git add .
#git commit -am "make it better"
#git push heroku master


app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

# Channel Access Token
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
# Channel Secret
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
client_id = config['imgur_api']['Client_ID']
client_secret = config['imgur_api']['Client_Secret']
album_id = config['imgur_api']['Album_ID']

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
            content = content + s.text + "\n" + s.get('href') + "\n\n" #取超連結合成字串 
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

def img():
    url='https://docs.google.com/spreadsheets/d/e/2PACX-1vQeVDkvUJclURb7YNkEocyMmZc0nfLCagrE0p7JFOkPwDEL-SJLd519gkMicdl17-C2wgjc7jnZalfO/pubhtml'
    res = requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')
    imglist=[]
    for index,img in enumerate(soup.select('.softmerge-inner a'),0):
        imglist.append(img.text)
        
    return imglist[random.randint(0,len(imglist))]

def air():
    url='https://taqm.epa.gov.tw/taqm/tw/Aqi/Yun-Chia-Nan.aspx?type=all&fm=AqiMap'
    ress=requests.session()
    res=ress.get(url)
    soup = BeautifulSoup(res.text,'html.parser')
    name1=soup.find(id='ctl04_gvAll_ctl54_linkSite').text
    name=re.search('\S*',name1).group()#正則表達抓空白前的字串
    AQI=soup.find(id='ctl04_gvAll_ctl54_labPSI').text
    PM25=soup.find(id='ctl04_gvAll_ctl54_labPM25').text
    level=""
    if int(AQI) >=300:
        level="有害"
    elif int(AQI)<300 and int(AQI)>=200:
        level="非常不良"
    elif int(AQI)<200 and int(AQI)>=101:
        level="不良"
    elif int(AQI)>50 and int(AQI)<=100:
        level="普通"
    else:
        level="良好"
    result=name+":"+level+"  "+"空氣品質指標為"+AQI+"   PM2.5為"+PM25
    return result

def weather():
    url='http://opendata.epa.gov.tw/ws/Data/ATM00698/?%24skip=0&%24top=1000&format=json&token=IfhCJYj7b0iN186BYwq/bQ'
    res=requests.get(url)#爬gov opendata
    data=json.loads(res.text)#載入json資料
    
    for info in data:
        if info['SiteName']=="臺南":#抓取臺南最新資料
            result="地點:臺南"+"  "+"發佈單位:"+info['Unit']+"  "+"天氣:"+info['Weather']+"  "+"溫度:"+info['Temperature']+"  "+"風向:"+info['WindDirection']+"  "+"風力:"+info['WindPower']+"  "+"濕度:"+info['Moisture']+"  "+"資料時間:"+info['DataCreationDate']
            return result
            break;
    return 0

def typhoonday():
    url='http://typhoon.ws/lifeinfo/stop_working'
    ress=requests.Session()
    headers = {'user-agent': 'my-app/0.0.1'}
    res=ress.get(url,headers=headers)#use header to solve Http406error
    res.encoding = 'UTF-8'#解決亂碼
    content=""
    soup=BeautifulSoup(res.text,'html.parser')
    table=soup.select('table.data_table_line')
    #for rows in table[0].find_all('tr'): #分解table to tr and td
    #    for cells in rows.find_all('td'):
    #        print(cells.contents[0])  #type is tag so can't not use text >>content get list
    for index,data in enumerate(table,0):
        content=content+data.text
    return content.replace("\n\n","\n").replace("\n\n\n","\n\n") #解決跨行

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)    

    if event.message.text == "抽":
        client = ImgurClient(client_id, client_secret)
        images = client.get_album_images(album_id)
        index = random.randint(0, len(images) - 1)
        url = images[index].link
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        
    if event.message.text == "停班停課":
        content = typhoonday()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    
    if event.message.text == "weather":
        content = weather()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    
    if event.message.text == "air":
        content = air()
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text=content))
        return 0
    
    if event.message.text == "draw":
        content=img()
        line_bot_api.reply_message(
            event.reply_token,
        ImageSendMessage(original_content_url=content, preview_image_url=content))
        return 0    
    
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

    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
