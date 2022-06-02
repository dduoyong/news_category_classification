import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import *
from tensorflow.keras.layers import *

X_train, X_test, Y_train, Y_test = np.load(
    './crawling_data/news_data_max_17_wordsize_5786.npy',
    allow_pickle=True)

print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)


#model 만들기

model = Sequential()
model.add(Embedding(5786, 300, input_length= 17))
#model이 단어들의 의미를 학습 5786 단어 개수만큼의 차원공간에 단어를 배치
#단어의 개수가 5786이니 5786차원
#embedding layer 비슷한 의미의 단어들을 식별하기 위한 과정
#300은 5786의 차원, 차원이 커질수록 데이터가 희소해짐
# -> 차원의 수에 비례하여 데이터가 증가되어야 하는데 데이터가 희소해지면 학습이 잘 안됨
#차원이 늘어날수록 데이터끼리의 간극이 넓어짐
#차원축소의 알고리즘을 이용해서 5786의 차원을 300 차원으로 줄여줌
#차원의 저주를 극.복.
model.add(Conv1D(32, kernel_size= 5, padding='same', activation= 'relu'))
#Conv 문장은 이미지와 달리 1차원이지만 문장의 앞뒤관계가 이미지 2차원처럼 존재함
#Conv1D로 사용
model.add(MaxPool1D(pool_size=1))
#pool size = 1 하나주면 제일 큰 값, 즉, 의미가 없음 안하겠다는 의미인데 자동으로 따라감 Maxpool할 때
model.add(LSTM(128, activation='tanh', return_sequences=True))
#return_sequences=True
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh'))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128, activation= 'relu'))
model.add(Dense(6, activation='softmax'))
#다중분류기는 somax
model.summary()

model.compile(loss= 'categorical_crossentropy',
              optimizer='adam', metrics=['accuracy'])
fit_hist = model.fit(X_train, Y_train, batch_size=128,
                     epochs=10, validation_data=(X_test, Y_test))
model.save('./models/news_category_classification_model{}.h5'.format(
    fit_hist.history['val_accuracy'][-1]))
plt.plot(fit_hist.history['val_accuracy'], label= 'val_accuracy')
plt.plot(fit_hist.history['accuracy'], label= 'accuracy')
plt.legend()
plt.show()
