from fastapi import FastAPI,Form
from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import math


app = FastAPI()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}

# importing the library
import requests
from bs4 import BeautifulSoup
import math

def getWeather(city):
  url = "https://www.google.com/search?q="+city+"-weather"
  html = requests.get(url).content
  soup = BeautifulSoup(html, 'html.parser')
  Ftemp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
  temperature_fahrenheit = float(Ftemp.split('°')[0])
  Ctemp=f'{math.ceil(((float(temperature_fahrenheit) - 32) * 5 / 9))}'+'°'+'C'
  str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
  cityName = soup.find('span', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text.split(',')[0]
  data = str.split('\n')
  time = data[0]
  sky = data[1]
  listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
  strd = listdiv[5].text
  pos = strd.find('Wind')
  other_data = strd[pos:]
#   print("City Name is", cityName)
#   print("Temperature is", Ctemp)
#   print("Time: ", time)
#   print("Sky Description: ", sky)
#   print(other_data)

  weather_data={
      'cityName':cityName,
      'temperature':Ctemp,
      'Time':time,
      'skyDesc':sky,
      'other_data':other_data
  }
  return weather_data

# city = "Itavaram"
# weather_data=getWeather(city)
# print(weather_data)



def getHeadlines():
  url='https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRFZxYUdjU0JXVnVMVWRDR2dKSlRpZ0FQAQ?hl=en-IN&gl=IN&ceid=IN%3Aen'
  root_url='https://news.google.com'
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  headlines_data=[]
  headline_boxes=soup.find_all(class_='W8yrY')
#   print(len(headline_boxes))
  for headline_box in headline_boxes:
    article=headline_box.find(class_='IBr9hb')
    figure=article.find('figure')
    img='None'
    if figure:
      img=root_url+figure.find('img').get('src').split('=-')[0]
    # print(img)
    article_link_container=article.find('a',class_='gPFEn')
    article_link=root_url+article_link_container.get('href')
    article_headline=article_link_container.text
    # print(article_headline)
    # print(article_link)
    time=article.find(class_='hvbAAd').text
    article_datetime=article.find(class_='hvbAAd').get('datetime')
    article_from=article.find(class_='msvBD zC7z7b')
    if article_from:
      article_from=article_from.get('src')
    else:
      article_from='None'
    # print(time)
    headline={
        'title':article_headline,
        'article_link':article_link,
        'article_from':article_from,
        'img_url':img,
        'time_text':time,
        'datetime':article_datetime
    }
    headlines_data.append(headline)
    # print('----------------------')
  sorted_headlines = sorted(headlines_data, key=lambda x: x['datetime'],reverse=True)
  return sorted_headlines

# latest_news_headlines=getHeadlines()
# import json
# prt=json.dumps(latest_news_headlines, indent=4)
# print(prt)

@app.get('/getLatestHeadlines')
async def getLatestHeadlines():
  latest_news_headlines=getHeadlines()
  return {'success':True,'headlines':latest_news_headlines}

@app.get('/getWeather/')
async def getWeather(city: Optional[str] = Form('Ithavaram')):
  latest_city_weahter=getWeather(city)
  return {'success':True,'weatherData':latest_city_weahter}

