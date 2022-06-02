from bs4 import BeautifulSoup
import requests
import re #전처리
import pandas as pd
import datetime

category = ['Politics', 'Economic', 'Social', 'Culture', 'World', 'IT']

# url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101'
#정치면 뉴스 주소
url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100'

#페이지 전체를 긁어다가 헤드 가져오기
headers = {'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'}

df_titles = pd.DataFrame()

for i in range(6):
    url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=10{}'.format(i)
    resp = requests.get(url, headers=headers)
    # resp = response
    # print(resp) #<Response [200]>
    # print(list(resp)) #Response의 내용 보기 -> list로 받기
    # print(type(resp))

    # 제목만 뽑아내기 -> bs4
    # request 요청해서 응답 받아올 때
    # 응답받은 html에서 무엇을 가져올 때 -> bs4
    soup = BeautifulSoup(resp.text, 'html.parser')
    # print(soup)
    #html의 문서 형태로 parsing해라, text문자열을 한 줄로 출력되니 html형태와 같이 보여달라
    #'.parser'

    title_tags = soup.select('.cluster_text_headline')
    # print(title_tags)

    #tag </a>이런 거 잘라내고 문자열만 가져오기
    print(title_tags[0].text)

    #for문 돌려서 텍스트만 뽑아내서 출력하기
    titles = []
    for title_tag in title_tags:
        # 자연어 처리 're'를 이용해서 한글만 남기고 다른 부호(문장부호, 영어 등)들 없애기
        title = re.compile('[^가-힣 ]').sub('', title_tag.text)
        #가~힣 => 한글 전부를 제외한 나머지를 title_tag.text에서 빼고 ''로 채워넣어라(즉, 지워라)
        #^: 제외하다의 의미/ 정규표현식 필요할 때 점프투파이썬에서 찾아보기
        #titles.append(title_tag.text)
        titles.append(title)
    #titles 섹션별 데이터프레임 만들기
    df_section_titles = pd.DataFrame(titles, columns=['titles'])
    df_section_titles['category'] = category[i]
    df_titles = pd.concat([df_titles, df_section_titles], axis='rows',
                          ignore_index=True)

print(df_titles.head())
df_titles.info()
print(df_titles['category'].value_counts())
df_titles.to_csv('./crawling_data/naver_headline_news{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index = False)

