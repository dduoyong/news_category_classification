#오늘의 뉴스 받아다가 전처리하기
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
#scikit-learn으로 터미널 pip install
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import pickle
from tensorflow.keras.models import load_model

pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', 20)
#column수가 많으면 ....으로 생략되는데 20까지는 생략하지 말고 다 보여달라
df = pd.read_csv('./crawling_data/naver_headline_news20220527.csv')
# print(df.head())
# df.info()

#category -> y, title->x
#onehot encoding

X = df['titles']
Y = df['category']

with open('./models/encoder.pickle', 'rb') as f:
    encoder = pickle.load(f)


labeled_Y = encoder.transform(Y)
label = encoder.classes_
with open('./models/encoder.pickle', 'wb') as f :
    pickle.dump(encoder, f)

onehot_Y = to_categorical(labeled_Y)
print(onehot_Y)

okt = Okt()

for i in range(len(X)) :
    X[i] = okt.morphs(X[i], stem=True)

stopwords = pd.read_csv('./crawling_data/stopwords.csv', index_col = 0)

for j in range(len(X)):
    words = []
    for i in range(len(X[j])):
        if len(X[j][i]) > 1:
            if X[j][i]not in list(stopwords['stopword']):
                words.append(X[j][i])
    X[j] = ' '.join(words)

with open('./models/news_token.pickle', 'rb') as f:
    token = pickle.load(f)

tokened_X = token.texts_to_sequences(X)
# print(tokened_X[:5])
for i in range(len(tokened_X)):
    if len(tokened_X[i]) > 17 :
        tokened_X[i] = tokened_X[i][:17]

X_pad = pad_sequences(tokened_X, 17)
print((X_pad[:5]))

model = load_model('./models/news_category_classification_model0.6025640964508057.h5')
preds = model.predict(X_pad)
predicts = []
for pred in preds:
    most = label[np.argmax(pred)]
    pred[np.argmax(pred)] = 0
    #제일 큰 값
    second = label[np.argmax(pred)]
    #두번째 큰 값
    predicts.append([most, second])
df['predict'] = predicts

print(df.head(30))

df['OX'] = 0
for i in range(len(df)):
    if df.loc[i, 'category'] in df.loc[i, 'predict']:
        df.loc[i, 'OX'] = 'O'
    else:
        df.loc[i, 'OX'] = 'X'

print(df.head(30))

print(df['OX'].value_counts())
print(df['OX'].value_counts()/len(df))
#value counts를 전체 개수로 나눠보기

for i in range(len(df)):
    if df['category'][i] not in df['predict'][i]:
        print(df.iloc[i])
        #df.loc[i, 'category'] i번째의 category column 값과 뜻이 똑같음

#기사 내용까지 crawling했다면 accuracy가 올라갔을 터
#노래 장르 분류, 영화 장르 줄거리 분류