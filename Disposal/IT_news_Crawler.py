import requests
from bs4 import BeautifulSoup
import re
import feedparser
import pandas as pd
import datetime

#변수선언
if True:
       #변수
       #날짜와 경로
       day = datetime.date.today()
       file_path = './Data/News/News '+str(day)+'.csv'
       #저장과 불러오기 관련 변수
       data_count = 0
       frame = ''
       #비즈, 파이낸셜 , 디데일리, 한국,경향,아이,한경,동아
       #중앙일보는 주소가 존재하지 않음
       rss = ['http://www.fnnews.com/rss/new/fn_realnews_it.xml',
              'https://www.itbiznews.com/rss/S1N3.xml',
              'http://www.ddaily.co.kr/DATA/rss/ddaily_rss_itpolicy.xml',
              'https://rss.hankooki.com/daily/dh_it_tech.xml',
              'http://www.khan.co.kr/rss/rssdata/it_news.xml',
              'http://www.inews24.com/rss/news_it.xml',
              'https://rss.hankyung.com/feed/it.xml',
              'https://it.donga.com/feeds/rss/news/',
              ]

#텍스트 추출구조
#경향
def khan(soup):
       news_data = soup.select('#articleBody > p.content_text')
       data_def = preprocessing(str(news_data))
       return data_def
#아이뉴스
def inews(soup):
       news_data = soup.select('#articleBody > p')
       data_def = re.sub('아이뉴스(.+?)기자','',str(news_data))
       data_def = preprocessing(data_def)
       return data_def
#한경
def hankyung(soup):
       news_data = soup.select('#articletxt')
       data_def = preprocessing(str(news_data))
       return data_def
#동아일보
def donga(soup):
       news_data = soup.select('body > main > div > div.main-content.col-lg-8 > div.article > article > p')
       data_def = re.sub('IT동아(.+?)기자', '',str(news_data))
       data_def = preprocessing(data_def)
       return data_def
#it비즈
def itbiz(soup):
       news_data = soup.select('#article-view-content-div > p')
       data_def = preprocessing(str(news_data))
       return data_def
#파이낸셜
def fnnews(soup):
       news_data = soup.select('#article_content')[0].get_text()
       data_def = re.sub('\[(.+?)\]', '',str(news_data))
       data_def = re.sub('※(.+?)지', '',str(data_def))
       data_def = re.sub('/(.+?)뉴스1', '',str(data_def))
       data_def = preprocessing(data_def)
       return data_def
#디지털데일리
def ddaily(soup):
       data_def = soup.select('#news_body_area')[0].get_text()
       data_def = re.sub('디지털(.+?)기자', '',str(data_def))
       data_def = preprocessing(data_def)
       return data_def
#한국
def hankooki(soup):
       url_plu = soup
       url_plu = re.search('/(.+?)"', str(url_plu))
       url_plu = url_plu.group()
       url_plu = re.sub('"','',url_plu)
       main_url = 'http://daily.hankooki.com' + url_plu
       print(main_url)

       response = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
       soup = BeautifulSoup(response.content, 'html.parser')
       data = soup.select('#article-view-content-div > p')
       #개별 전처리
       data = re.sub('데일리(.+?)기자', '', str(data))
       data_def = preprocessing(data)
       return data_def

#전처리
def preprocessing(data):
       data_def = re.sub('<(.+?)>', '',str(data))
       data_def = re.sub('\r', '', str(data_def))
       data_def = re.sub('\t', '', str(data_def))
       data_def = re.sub('\n', '', str(data_def))
       data_def = re.sub('\f', '', str(data_def))
       data_def = re.sub('\v', '', str(data_def))
       data_def = re.sub('\[', '', str(data_def))
       data_def = re.sub('\]', '', str(data_def))
       data_def = data_def.strip()
       return data_def
#뉴스 종류별 회전
def ring(a, soup):
       #파이낸셜 , 비즈, 디데일리, 한국,경향,아이,한경,동아
       if a == 0 :
              data = fnnews(soup)
       elif a == 1 :
              data = itbiz(soup)
       elif a == 2 :
              data = ddaily(soup)
       elif a == 3 :
              data = hankooki(soup)
       elif a == 4:
              data = khan(soup)
       elif a == 5:
              data = inews(soup)
       elif a == 6:
              data = hankyung(soup)
       elif a == 7:
              data = donga(soup)
       return data

#저장
def save(data):
       global data_count, frame
       #데이터 추가
       frame.loc[data_count] = data
       frame.to_csv(file_path, encoding='utf-8-sig')
       data_count += 1

#데이터프레임(csv) 불러오기
def dataframe():
       global frame
       try:
              frame = pd.read_csv(file_path, index_col = 0)
       except:
              data = {
                     'text' : []
              }
              frame = pd.DataFrame(data)
              frame.to_csv(file_path, encoding='utf-8-sig')
       return frame

#rss주소를 돌아가면서 세팅하기, url_list 초기화
def News_main():
       # global url, url_list, response, soup
       frames = dataframe()
       for a in range(0, len(rss)) :
              url = feedparser.parse(rss[a])
              url_list = []
              #뉴스 url 불러오기
              for i in url.entries :
                     url_list.append(i.link)

              #수프 재세팅
              for j in range(0, len(url_list)) :
                     response = requests.get(url_list[j], headers={"User-Agent": "Mozilla/5.0"})
                     soups = BeautifulSoup(response.content, 'html.parser')
                     data = ring(a, soups)

                     print(data)
                     save(data)
       print(frames)

#메인
if __name__ == '__main__':
       News_main()
