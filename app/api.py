from fastapi import FastAPI,Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
from bs4 import BeautifulSoup
import ast
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup


origins = [
    "http://localhost:3000",
    'https://infospherenews.vercel.app',
    'https://infosphereweb.vercel.app',
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.google.com/'
}

genai.configure(api_key="AIzaSyCWna-D27sTjqf3IuIBgd_BD5ZFfvIfQrA")

generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
]
model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def getMarketTrends(companies):
  market_trends=[]
  for company in companies:
    url = f"https://www.google.com/search?q={company}+shares+price+today"
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

def getCryptNewsData():
  cryptoUrl='https://crypto.news/news/'
  response=requests.get(cryptoUrl)
  soup=BeautifulSoup(response.text,'html.parser')
  # print(soup)
  allCrypto=soup.find(class_='alm-listing alm-ajax post-archive__items')
  # print(allCrypto)
  subCrypto=allCrypto.find_all(class_='post-loop')
  # print(len(subCrypto))
  crypto_data=[]
  for crypto in subCrypto:
    figure=crypto.find('figure')
    img_url=figure.find('img').get('src')
    heading=crypto.find(class_='post-loop__header').text.strip()
    link=crypto.find('a').get('href')
    time=crypto.find('time').text.strip()
    r2=requests.get(link)
    s2=BeautifulSoup(r2.text,'html.parser')
    content_div=s2.find(class_='post-detail__content blocks')
    data='\n'.join([content.text for content in content_div.find_all('p')])
    # print(data)
    crypto_data.append({
        'heading':heading,
        'time':time,
        'imgUrl':img_url,
        'content':data
    })
  return crypto_data

def getWeatherData(city):
  city='-'.join(city.split(' '))
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Referer': 'https://www.google.com/'
  }
  url = f"https://www.google.com/search?q={city}-weather-today"
  # print(url)
  response = requests.get(url, headers=headers)
  all_details={}
  if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      
      city_data = soup.find('div', attrs={'class': 'vk_sh vk_gy GlhITe'}).text.strip().split(',')
      cityName=city_data[0].strip()
      all_details['cityName']=cityName

      timeList = soup.find('div', attrs={'id': 'wob_dts'}).text.strip().split(' ')
      day,time=timeList[0].strip(),timeList[1].strip()
      all_details['day']=day
      all_details['time']=time

      imgUrl = soup.find('img', attrs={'id': 'wob_tci'}).get('src')
      all_details['imgUrl']='https:'+imgUrl

      temperature = soup.find('span', attrs={'id': 'wob_ttm'}).text.strip()+'°'+'C'
      all_details['temperature']=temperature

      fTemp = soup.find('span', attrs={'id': 'wob_tm'}).text.strip()+'°'+'F'
      all_details['fTemp']=fTemp

      skyDesc = soup.find('span', attrs={'id': 'wob_dc'}).text.strip()
      all_details['skyDesc']=skyDesc

      details_container = soup.find('div', attrs={'class': 'wtsRwe'})
      list_of_details=details_container.find_all('div')
      
      Precipitation=list_of_details[0].text.split(': ')[1]
      all_details['precipitation']=Precipitation
      Humidity=list_of_details[1].text.split(': ')[1]
      all_details['humidity']=Humidity
      Wind=list_of_details[2].text.split('mph')[1]
      all_details['wind']=Wind
      
      # print(all_details)
      return all_details

  else:
    return all_details
# city='Vijaywada'
# weather_data=getCompleteWeather(city)
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

def scrap(typ):
  urlS = 'https://www.prnewswire.com/news-releases/'+typ
  response = requests.get(urlS)
  soup = BeautifulSoup(response.content, 'html.parser')
  links = []
  for news_item in soup.find_all('a', class_='newsreleaseconsolidatelink display-outline w-100'):
    links.append(news_item['href'])

  root = 'https://www.prnewswire.com'
  count = 1
  newsDict = {}
  for sub_link in links:
    if count <= 15:
      al = str(root+sub_link)
      headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
      res = requests.get(al, headers=headers)
      doc = BeautifulSoup(res.content, 'html.parser')
      head = doc.find('h1')
      head = head.text.strip()
      content = doc.find('div', class_='col-lg-10 col-lg-offset-1')
      content = content.text.strip()
      print("\n Headline: "+head+"\n Content: "+content+"\n")
      newsDict[head]=content
      prompt_parts = [
            f"As an anchor for an English speaking news channel, present the news in about a minute long summary with the short headline {head} and its content as {content}. Make sure to use only the neccessary details as a professional news anchor would do but also be as elaborative as possible. Word it as if you are speaking the result as an actual anchor and add some humanness to the result as well. Do not include any useless symbols, just the speech content.",
            ]
      response = model.generate_content(prompt_parts)
      newsDict[head]= response.text
      # print("\n PROMPT RES OF "+str(count)+" : \n")
      # print(promtRes)
      count = count + 1
      break
  return newsDict

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}

@app.get("/latest")
async def index():
   latest = 'news-releases-list/'
   res = scrap(latest)
   return res

@app.get("/business")
async def business():
   bus_url = 'financial-services-latest-news/financial-services-latest-news-list/'
   res = scrap(bus_url)
   return res

@app.get("/entertainment")
async def entertainment():
   ent = 'entertainment-media-latest-news/entertainment-media-latest-news-list/'
   res = scrap(ent)
   return res

@app.get("/sports")
async def sports():
   sp = 'sports-latest-news/sports-latest-news-list/'
   res = scrap(sp)
   return res

@app.get("/health")
async def health():
   hl = 'health-latest-news/health-latest-news-list/'
   res = scrap(hl)
   return res

@app.get("/technology")
async def technology():
   tech = 'consumer-technology-latest-news/consumer-technology-latest-news-list/'
   res = scrap(tech)
   return res

@app.get("/science")
async def science():
   sci = 'energy-latest-news/energy-latest-news-list/'
   res = scrap(sci)
   return res

@app.get("/environment")
async def environment():
   env = 'environment-latest-news/environment-latest-news-list/'
   res = scrap(env)
   return res

@app.get("/crypto")
async def crypto():
   cry = 'financial-services-latest-news/cryptocurrency-list/'
   res = scrap(cry)
   return res

@app.get('/getLatestHeadlines')
async def getLatestHeadlines():
  latest_news_headlines=getHeadlines()
  return {'success':True,'headlines':latest_news_headlines}

@app.get('/getCryptNews')
async def getCryptNews():
  cryptoNews=getCryptNewsData()
  return {'success':True,'cryptoNews':cryptoNews}

@app.post('/getWeather/')
async def getWeather(city: Optional[str] = Form('Vijaywada')):
  latest_city_weahter=getWeatherData(city)
  return {'success':True,'weatherData':latest_city_weahter}

@app.post('/getMarketDetails/')
async def getMarketDetails(companies: Optional[str] =Form("['TSLA','AMZN','AAPL','MSFT']")):
  # companies=['TSLA','AMZN','AAPL','MSFT']
  companies = ast.literal_eval(companies)
  market_trends=getMarketTrends(companies)
  return {'success':True,'market_trends':market_trends}
