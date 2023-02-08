# 'C:\\Users\\dda28\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumBarunGothic.ttf'
import os
import sys
import urllib.request
import json
from konlpy.tag import Okt
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from wordcloud import ImageColorGenerator
from flask import Flask, render_template, request, redirect, url_for

client_id = "46yv2d51AbFNL0xgc2ot"
client_secret = "rCGEDjxgRv"
jsonStr = []

def naver_search(category, title):

   for i in range(1, 1000, 100):
      url = f"https://openapi.naver.com/v1/search/{category}.json?query={title}&start={i}&display=100" # JSON 결과
      # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
      request = urllib.request.Request(url)
      request.add_header("X-Naver-Client-Id",client_id)
      request.add_header("X-Naver-Client-Secret",client_secret)
      response = urllib.request.urlopen(request)
      rescode = response.getcode()
      if(rescode==200):
         response_body = response.read()
         jsonStr.append(response_body.decode('utf-8'))
      else:
         print("Error Code:" + rescode)
   text_list = []
   for i in range(0, 10, 1):
      result = json.loads(jsonStr[i])
      for j in range(0, len(result['items']), 1):
         text_list.append(result['items'][j]['description'])
   
   text = ','.join(text_list)
   text = text.replace(',','')

   okt = Okt()
   line = []
   line = okt.pos(text)
   n_adj = []
   for word, tag in line:
      if tag in ['Noun','Adjective']:
         if len(word)>1:
            n_adj.append(word)
   
   # print(n_adj) -> word cloud만 나오게 하기 위하여 일시적으로 주석처리. //
   
   global stop_words
   stop_words = set(stop_words.split(' '))
   n_adj = [word for word in n_adj if not word in stop_words] # 불용어를 제외한 단어만 남기기
   # 가장 많이 나온 단어 100개 저장
   counts = Counter(n_adj)
   global tags
   tags = counts.most_common(100) # 상위 갯수만 전달.
   # print(tags) #-> 빈도수를 확인하고 싶을 경우에는 주석 해제

   #시각화
   path =  'C:\\Users\\dda28\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumBarunGothic.ttf' # 폰트가 저장되어 있는 위치
   masking_image = np.array(Image.open('C:/Users/dda28/바탕 화면/naver_scrapper/rainbow_apple.jpg'))
   word_cloud = WordCloud(font_path = path, background_color = 'black', max_font_size = 400, mask=masking_image, width=600, height=400).generate_from_frequencies(dict(tags))
   # word_cloud 의 Argument 에는 colormap='coolwarm' 를 제외하였다. 왜냐하면 이미지의 색상을 그대로 text color 에 generate 하기 위해서
   image_colors = ImageColorGenerator(masking_image)
   word_cloud = word_cloud.recolor(color_func=image_colors)
   plt.figure(figsize=(10,8), facecolor='black')
   plt.imshow(word_cloud,interpolation='bilinear') # 선형보간법 이라고도 한다.
   plt.axis('off')
   plt.savefig('./static/img/result.png') #-> 파일로 저장하고자 할 경우에는 주석 해제 
   plt.show()
   jsonStr.clear()
   n_adj.clear()
   tags = counts.most_common(10) # 상위 10개의 검색어는 html에 표기해주기 위해서 추가.

# 검색
# encText = urllib.parse.quote("종도형") # 검색할 주제어 입력
# encCategory = urllib.parse.quote('news') # news, blog 등등 게시위치 지정
# stop_words = '' # -> 제외할 단어 , 띄어쓰기 단위로 입력
# search(encCategory,encText)


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

stop_words = ''
encText = ''
encCategory = ''
tags = []

@app.route("/", methods= ['GET','POST'])
def home():
    global stop_words, encText, encCategory
    stop_words = ''
    encCategory = ''
    encText = ''
    return render_template("index.html")

@app.route("/search")
def search():
    global stop_words, encText, encCategory
    stop_words = ''
    encCategory = ''
    encText = ''
    keyword = request.args.get("keyword")
    category = request.args.get("category")
    removeText = request.args.get("removeText")
    encText = urllib.parse.quote(keyword)
    encCategory = urllib.parse.quote(category)
    stop_words = removeText
    naver_search(encCategory,encText)
    return render_template("search.html",keyword = keyword, tags = tags)

if __name__ == "__main__":
    app.run('0.0.0.0')