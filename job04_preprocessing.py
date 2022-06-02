#기사 헤드라인 제목 자연어 처리

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

pd.set_option('display.unicode.east_asian_width', True)
df = pd.read_csv('./crawling_data/naver_news_titles20220526.csv')
# print(df.head())
# df.info()

#category -> y, title->x
#onehot encoding

X = df['titles']
Y = df['category']

encoder = LabelEncoder()
labeled_Y = encoder.fit_transform(Y)
# print(labeled_Y[:3])
#Y값을 라벨링해서 처음 3개만 찍어봤더니, 3 3 3 => Politics
#Politics가 3인 이유: 오름차순 C E I P
#label encoder의 리스트 기준은 오름차순
label = encoder.classes_
# print(label)
with open('./models/encoder.pickle', 'wb') as f :
    pickle.dump(encoder, f)

onehot_Y = to_categorical(labeled_Y)
print(onehot_Y)

#onehot encoder  0과 1로 바꿔주기

#자연어처리 X를
#바뀐 숫자를 토큰으로 만들어주기
#각 형태소의 단어를 어떻게 라벨링 해주었는지 매칭 정보를 내가 갖고 있어야 매칭 해줌
#fitting을 하고 나면 dict로 가지게 됨
#가방은 1, 치약은 3 등 이런식의 형태로
#우리가 갖고 있는 모든 뉴스의 제목들 문장은 모든 형태소를 라벨링하고 그 라벨링 정보를 dict로 갖기
#morphs는 그냥 형태소로 잘라준다, Tokenizer의 morphs의 역할
#java와 python의 연결통로 j pype -> java 설치 필요
okt = Okt()
# okt_morph_X = okt.morphs(X[6], stem= True)
# #stem은 했던, 했고 등의 형태소를 하다로 원형의 형태로 바꿔줌
# print(okt_morph_X)

#X의 길이만큼 for문 돌리기
for i in range(len(X)) :
    X[i] = okt.morphs(X[i], stem=True)
# print(X[:10]) #10개만 뽑아보기

#제목들의 의미를 학습해서 정치인지 경제인지 섹션 분류
#학습 시켜 기사분류 하는데에 있어 '은', '는', '이', '가' 등의 주격 조사는 중요하지 않음
#뉴스 카테고리와 연관없는 단어들은 제거하기

stopwords = pd.read_csv('./crawling_data/stopwords.csv', index_col = 0)
#stopwords 파일 안에 이름없는 인덱스가 포함되어 있음 , index_col=0은 0번 column이 인덱스다!
#stopwords가 DataFrame의 형태

for j in range(len(X)):
    words = []
    for i in range(len(X[j])):
        if len(X[j][i]) > 1:
            if X[j][i]not in list(stopwords['stopword']):
                words.append(X[j][i])
    X[j] = ' '.join(words)

print(X)
# print(words)

#if len(X[j][i]) > 1: 한글자 이상을 버릴 예정이고
#숫자로 바꿔줄 거임 tokenizer

token = Tokenizer()
token.fit_on_texts(X)
#단어사전 dict 만들어서 문장을 token들의 sequetial한 데이터로 만들어 줌
#fit_on_texts를 하면  token이 단어 사전을 갖게 되고 label을 갖게 해주고
#단어 사전에 있는 값들을 list로 만들어서
#같은 형태소는 같은 값으로 라벨링
tokened_X = token.texts_to_sequences(X)
# print(tokened_X)
# print(len(tokened_X))
wordsize = len(token.word_index) + 1
# print(token.word_index)
# print(wordsize)
#word_index는 token의 유니크한 단어가 어떻게 이루어지는지 dict 형태로 출력
#단어의 길이를 알고 싶으면 len(tokened_X.word_index) + 1 -> 모델에게 전체 단어 개수를 줘야하는데 token에서 0을 안쓰니 1을 더해줌

#modeling할 때 입력 값의 값들이 다 같아야 함 5/ 4/ 3/ 이러면 하나로 통일해줘야 함
#문장 중 제일 긴 문장(즉, 형태소가 제일 많은 문장)을 기준으로 맞춰주기, 모자라는 개수 0으로 앞에서부터 채워주기
#LSTM
#문장 값이 몇개의 형태소로 이루어져 있는지, 제일 긴 문장이 몇인지 알아보기 위해 'max'

with open('./models/news_token.pickle', 'wb') as f:
    pickle.dump(token, f)

max = 0
for i in range(len(tokened_X)):
    if max < len(tokened_X[i]):
        max = len(tokened_X[i])
print(max)

#0으로 채워주기 padding
X_pad = pad_sequences(tokened_X, max)
print(X_pad)

#학습 시킬 때 결과와 test_size = test = 10%, train = 90%
X_train, X_test, Y_train, Y_test = train_test_split(
    X_pad, onehot_Y, test_size=0.1)
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)

xy = X_train, X_test, Y_train, Y_test
np.save('./crawling_data/news_data_max_{}_wordsize_{}'.format(max, wordsize), xy)
#word_index가 있어야 새로운 데이터한테 모델을 줄 때도 tokenizer가 있어야함 그래서 저장 필요
