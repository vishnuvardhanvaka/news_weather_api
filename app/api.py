from fastapi import FastAPI,Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import math


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    'https://infospherenews.vercel.app',
    'https://ai-avatar-live-stream.vercel.app'
]

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.google.com/'
}

def getMarketTrends(companies):
  market_trends=[]
  for company in companies:
    url = f"https://www.google.com/search?q={company} shares price today"
    # print(url)
    # html = requests.get(url).content
    # soup = BeautifulSoup(html, 'html.parser')
    # url='https://www.google.com/finance/quote/'+company+':NASDAQ'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        company_name = soup.find('div', attrs={'class': 'PZPZlf ssJ7i B5dxMb'}).text.strip()
        last_trade_value = soup.find('span', attrs={'class': 'IsqQVc NprOob wT3VGc'}).text.strip()
        absolute_change_value = soup.find('span', attrs={'jsname': 'qRSVye'}).text.strip()
        change = soup.find('span', attrs={'class': 'jBBUv'}).get('aria-label')
        if 'Down by ' in change:
          sign='negative'
          percentage=change.split('Down by ')[1].strip()
        elif 'Up by ' in change:
          sign='positive'
          percentage=change.split('Up by ')[1].strip()
        else:
          sign=''
          percentage='0'

        company_data={
            'company_name':company_name,
            'last_trade_value':last_trade_value,
            'sign':sign,
            'percentage':percentage,
            'absolute_change_value':absolute_change_value
        }
        market_trends.append(company_data)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
  return market_trends


def getWeatherData(city):
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
# weather_data=getWeatherData(city)
# print(weather_data)


def get_redirected_url(original_url):
  try:
      response = requests.head(original_url, allow_redirects=True)
      if response.status_code == 200:
          return response.url
      else:
          print(f"Failed to retrieve redirected URL for {original_url}. Status code: {response.status_code}")
          return original_url
  except Exception as e:
      print(f"Error occurred while retrieving redirected URL for {original_url}: {str(e)}")
      return original_url

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
      # img=get_redirected_url(img)
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
        'imageUrl':img,
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

@app.post('/getWeather/')
async def getWeather(city: Optional[str] = Form('Ithavaram')):
  latest_city_weahter=getWeatherData(city)
  return {'success':True,'weatherData':latest_city_weahter}

@app.get('/getMarketDetails')
async def getMarketDetails(companies: Optional[list] = Form(['TSLA','AMZN','AAPL','MSFT'])):
  # companies=['TSLA','AMZN','AAPL','MSFT']
  market_trends=getMarketTrends(companies)
  return {'success':True,'market_trends':market_trends}
