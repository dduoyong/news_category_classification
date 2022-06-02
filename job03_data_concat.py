import pandas as pd
import glob
import datetime

data_path = glob.glob('./crawling_data/*') #* 파일 싹 다 가져오기
print(data_path)


# df = pd.DataFrame()
# for path in data_path[1:] :
#     df_temp = pd.read_csv(path)
#     df = pd.concat([df, df_temp], ignore_index=True)
# df.dropna(inplace = True)
# df.reset_index(inplace= True, drop=True)
#
# print(df.head())
# print(df.tail())
# print(df['category'].value_counts())
# df.info()
# df.to_csv('./crawling_data/naver_news_titles{}.csv'.format(
#     datetime.datetime.now().strftime('%Y%m%d')), index = False)

#에러 없었을 때
df = pd.read_csv('./crawling_data/crawling_data.csv')
df_headline = pd.read_csv('./crawling_data/naver_headline_news20220525.csv')
df_all = pd.concat([df, df_headline], ignore_index=True)
df.to_csv('./crawling_data/naver_news_titles{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index = False)

print(df_all.head())
print(df_all.tail())
print(df_all['category'].value_counts())
df_all.info()
