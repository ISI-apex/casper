import tensorflow as tf
import numpy as np
import pandas as pd
import time
from sklearn import preprocessing
from scipy.stats import spearmanr

FILENAME = "halide_FFT.csv"

data = np.array(pd.read_csv(FILENAME))

train_data = data[:100]
test_data = data[100:]


train_feature = np.array(train_data[:, [1, 2, 3, 4]])


train_label = np.array(train_data[:, [0]])


test_x = np.array(test_data[:, [1, 2, 3, 4]])


print(test_data.shape)

x = tf.placeholder(tf.float32, [None, 4])
y = tf.placeholder(tf.float32, [None, 1])  
train_feature = preprocessing.scale(train_feature)  
test_xs = preprocessing.scale(test_x)  

print(test_xs.shape)


L1 = tf.layers.dense(x, 5, tf.nn.relu)
L2 = tf.layers.dense(x, 5, tf.nn.relu)


prediction = tf.layers.dense(L2,1)



# mean
loss = tf.reduce_mean(tf.square(y - prediction))

#mean, loss = tf.nn.moments(tf.square(y - prediction), 0) #?

saver = tf.train.Saver()


train_step = tf.train.AdamOptimizer(0.01).minimize(loss)


total_parameters = 0
for variable in tf.trainable_variables():

    shape = variable.get_shape()
    print(shape)
    print(len(shape))
    variable_parameters = 1
    for dim in shape:
        print(dim)
        variable_parameters *= dim.value
    print(variable_parameters)
    total_parameters += variable_parameters
print("total parameters: ", total_parameters)

with tf.Session() as sess:

    sess.run(tf.global_variables_initializer())



    print(sess.run(loss, feed_dict={x: train_feature, y: train_label}))

    for i in range(5000):
        sess.run(train_step, feed_dict={x: train_feature, y: train_label})
        if i % 200 == 0:
            print(i)
            print(sess.run(loss, feed_dict={x: train_feature, y: train_label}))

    inference_start = time.clock()
    prd = sess.run(prediction, feed_dict={x: test_xs})
    inference_end = time.clock()

    print('Inference time:', (inference_end - inference_start)/test_data.shape[0])

    f = open('re.txt', 'w')
    for i in range(test_data.shape[0]):
        f.writelines(str(prd[i][0]) + "\n")
    f.close()


    sum_MAE = 0.0
    sum_MSE = 0.0
    pred_list = []
    test_list = []
    for i in range(test_data.shape[0]):
        sum_MAE += abs(prd[i][0] - test_data[:, [0]][i][0])
        sum_MSE += pow(prd[i][0] - test_data[:, [0]][i][0], 2)
        pred_list.append(prd[i][0])
        test_list.append(test_data[:, [0]][i][0])
    print("MAE: ", sum_MAE / test_data.shape[0])
    print("MSE: ", sum_MSE / test_data.shape[0])

    rho, pval = spearmanr(pred_list,test_list)
    print('rho:', rho)



    saver.save(sess, "model/my-model")