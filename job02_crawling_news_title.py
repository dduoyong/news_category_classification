#브라우저 긁어와서 각 섹션 별 페이지 수 파악하기
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

category = ['Politics', 'Economic', 'Social', 'Culture', 'World', 'IT']
# pages = [283, 379, 447, 78, 111, 66]
pages = [110, 110, 110, 78, 110, 66]
#한 페이지당 뉴스 기사 20개, *110 => 2200
#데이터의 불균형을 맞추기 위해 최대 110으로 맞춰줌
#페이지 기반 url
url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100#&date=%2000:00:00&page=1'

options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR')
options.add_argument('--no--sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('disable-gpu')
driver = webdriver.Chrome('./chromedriver', options=options)
df_titles = pd.DataFrame()

for i in range(0, 6): #섹션별로 페이지 주소 한자리가 달라짐 10{}
    titles = []
    for j in range(1, pages[i]+1): #안에 페이지 당 20개의 기사가 있음, 페이지 별로 주소가 달라짐
        url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=10{}#&date=%2000:00:00&page={}'.format(i, j)
        driver.get(url)
        time.sleep(0.2)
            #delay 2seconds 2초마다 페이지 다음으로 넘어가기
        #copy>Xpath해서 적절한 경로로 news title 가져오기
        # // *[ @ id = "section_body"] / ul[1] / li[1] / dl / dt[2] / a 첫번째 기사
        # // *[ @ id = "section_body"] / ul[1] / li[2] / dl / dt[2] / a
        # // *[ @ id = "section_body"] / ul[1] / li[3] / dl / dt[2] / a
        # // *[ @ id = "section_body"] / ul[1] / li[4] / dl / dt[2] / a
        # // *[ @ id = "section_body"] / ul[1] / li[5] / dl / dt[2] / a
        # // *[ @ id = "section_body"] / ul[2] / li[1] / dl / dt[2] / a 여섯번째 기사
        # // *[ @ id = "section_body"] / ul[3] / li[1] / dl / dt[2] / a 열한번째 기사
        # // *[ @ id = "section_body"] / ul[4] / li[5] / dl / dt[2] / a 스무번째 기사

        #총 20개를 긁어오기 위해서 이중 for문을 씀
        for k in range(1, 5):
            for l in range(1, 6):
                x_path = '// *[ @ id = "section_body"] / ul[{}] / li[{}] / dl / dt[2] / a'.format(k, l)
                # title = driver.find_element_by_xpath('// *[ @ id = "section_body"] / ul[1] / li[5] / dl / dt[2] / a ').text
            try:
                title = driver.find_element_by_xpath(x_path).text #x_path를 찾아서 텍스트만 가져옴
                title = re.compile('[^가-힣 ]').sub('', title)
                #한글 이외의 문자는 title에서 ''로 제외시켜 빼겠다
                titles.append(title)
            except NoSuchElementException as e:
                time.sleep(0.5)
                try:
                    title = driver.find_element_by_xpath(x_path).text
                    title = re.compile('[^가-힣 ]').sub('', title)
                    titles.append(title)
                except:
                    try:
                        x_path = '// *[ @ id = "section_body"] / ul[{}] / li[{}] / dl / dt / a '.format(k, l)
                        title = re.compile('[^가-힣 ]').sub('', title)
                        titles.append(title)
                    except:
                        print('no such element')
                    # print(e)
                    # print(category[i], 'page', k*l)
                #k와 l을 곱하여
                #j페이지의 몇번째 기사인지는 k*l
                #NoSuchElementException -> X_path가 없음
            except StaleElementReferenceException as e:
                print(e)
                print(category[i], 'page', k * l)
                #로딩이 안되는 경우 -> StaleElementReferenceException
            except:
                print('error')
        if j % 30 == 0:
            #j 30으로 나눈 나머지가 0이다, 30페이지마다 저장하기
            # print('save', len(titles))
            df_section_titles = pd.DataFrame(titles, columns=['titles'])
            df_section_titles['category'] = category[i]
            df_titles = pd.concat([df_titles, df_section_titles], ignore_index=True)
            #그래야 합쳐질 때, concat할 때 같은 인덱스가 안생김 -> ignore_index
            df_titles.to_csv('./crawling_data/crawling_data_{}_{}.csv'.format(category[i], j), index = False)
            #어떤 카테고리의 몇 페이지부터 몇 페이지의 자료인지
            titles =[]

    df_section_titles = pd.DataFrame(titles, columns=['titles'])
    df_section_titles['category'] = category[i]
    df_titles = pd.concat([df_titles, df_section_titles], ignore_index=True)
    # 그래야 합쳐질 때, concat할 때 같은 인덱스가 안생김 -> ignore_index
    df_titles.to_csv('./crawling_data/crawling_data_{}_{}.csv'.format(category[i], j), index=False)
    # 어떤 카테고리의 몇 페이지부터 몇 페이지의 자료인지
    titles = []

#30의 배수 기사 이후의  기사들
df_section_titles = pd.DataFrame(titles, columns=['titles'])
df_section_titles['category'] = category[i]
df_titles = pd.concat([df_titles, df_section_titles], ignore_index=True)
df_titles.to_csv(('./crawling_data/naver_news_titles{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index = False)

driver.close()
#browser창이 닫힘
#저장을 여러 번 해주면서 안전장치를 둠