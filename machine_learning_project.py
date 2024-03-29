# -*- coding: utf-8 -*-
"""Machine_Learning_Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K_A2JCoKOCxw8ZtUOxJC7gJz_HTFkXUZ
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import metrics
from sklearn.metrics import recall_score, confusion_matrix, precision_score, f1_score, accuracy_score, classification_report



"""**Data Understanding Step.** This part is focused on **understanding the data** within the dataset. There is a line of code exploring data types."""

df = pd.read_csv('/content/telco.csv.xls')
df.head()

df.describe()

df.dtypes

"""**Data Preparation / Feature Engineering Step**"""

#separate the identifier and target variable names as lists
custid = ['customerID']
target = ['Churn']
df.head()

#separate the categorical and numeric column names as lists
categorical = df.nunique()[df.nunique()<10].keys().tolist()
categorical.remove(target[0])
numerical = [col for col in df.columns
                      if col not in custid + target + categorical]
df.head()

#one-hot encoding
df = pd.get_dummies(df, columns = categorical, drop_first = True)
df.head()

"""**Data Preprocessing Step**"""

# Replace empty strings with NaN
df[numerical] = df[numerical].replace('', np.nan)

# Convert columns to numeric
df[numerical] = df[numerical].apply(pd.to_numeric, errors='coerce')

# Drop rows with NaN values
df.dropna(subset=numerical, inplace=True)

#scaling numerical features
scaler = StandardScaler()
scaled_numerical = scaler.fit_transform(df[numerical])
scaled_numerical = pd.DataFrame(scaled_numerical, columns=numerical)

df1 = df.drop(columns = numerical, axis=1)
df1.head()

df2 = df1.merge(right=scaled_numerical,
                 how = 'left',
                 left_index =True,
                 right_index=True)
df2.head()

"""**encoding churn**"""

set(df['Churn'])

#there is a class imbalance, but not a severe one.
df.groupby(['Churn']).size() / df.shape[0]* 100

"""Machine Learning"""

train, test = train_test_split(df,test_size = .25)

#separate the indipendent features and the target variable
target = ['Churn']
custid = ['customerID']
cols = [col for col in df.columns if col not in custid + target]

#build training and testing set
train_X = train[cols]
train_Y = train[target]
test_X = test[cols]
test_Y = test[target]

"""**Logistic Regression**"""

logreg = LogisticRegression()

logreg.fit(train_X, train_Y)

"""Calculating Accuracy"""

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Assuming 'logreg' is your logistic regression model
pred_probabilities = logreg.predict_proba(test_X)[:, 1]

# Convert true labels ('Yes' and 'No') to numeric format (1 and 0)
true_labels_numeric = (test_Y == 'Yes').astype(int)

# Choose a threshold (e.g., 0.5) to convert probabilities into class labels
threshold = 0.5
predicted_labels = (pred_probabilities >= threshold).astype(int)

pred_train_Y = logreg.predict(train_X)
pred_test_Y = logreg.predict(test_X)
train_accuracy = accuracy_score(train_Y, pred_train_Y)
test_accuracy = accuracy_score(test_Y, pred_test_Y)
print('Training accuracy:', round(train_accuracy, 4))
print('Test accuracy:', round(test_accuracy, 4))

"""Calculating Precision & Recall"""

pred_train_Y = logreg.predict(train_X)
pred_test_Y = logreg.predict(test_X)

train_precision = round(precision_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_precision = round(precision_score(test_Y, pred_test_Y, pos_label='Yes'), 4)
train_recall = round(recall_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_recall = round(recall_score(test_Y, pred_test_Y, pos_label='Yes'), 4)
print('Training precision: {}, Training Recall: {}'.format(train_precision, train_recall))
print('Test precision: {}, Test Recall: {}'.format(train_precision, train_recall))

#values less than one decrease the odds, values more than one increase the odds.
#The effect on the odds is calculated by multiplying the exponent of the coefficient. the effect of one additional year of tenure decreases the odds of churn by 1 minus 0.403.
#This translates to roughly 60% decrease in the churn odds.

# Concatenate the feature names and their corresponding coefficients
coefficients = pd.concat([pd.DataFrame(train_X.columns),
                         pd.DataFrame(np.transpose(logreg.coef_))],
                        axis=1)

# Rename the columns
coefficients.columns = ['Feature', 'Coefficient']

# Calculate the exponential of the coefficients
coefficients['Exp_Coefficient'] = np.exp(coefficients['Coefficient'])

# Filter out features with coefficient equal to 0
coefficients = coefficients[coefficients['Coefficient'] != 0]

# Print and sort the coefficients
print(coefficients.sort_values(by=['Coefficient']))

"""**Decision Tree**"""

mytree = DecisionTreeClassifier()
tree.model = mytree.fit(train_X, train_Y)

"""Accuracy Metric"""

pred_train_Y = mytree.predict(train_X)
pred_test_Y = mytree.predict(test_X)
train_accuracy = accuracy_score(train_Y, pred_train_Y)
train_accuracy = accuracy_score(test_Y, pred_test_Y)
print('Training Accuracy:', round(train_accuracy, 4))
print('Test Accuracy:', round(test_accuracy, 4))

"""Precision & Recall"""

train_precision = round(precision_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_precision = round(precision_score(test_Y, pred_test_Y, pos_label='Yes'), 4)
train_recall = round(recall_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_recall = round(recall_score(test_Y, pred_test_Y, pos_label='Yes'), 4)
print('Training precision: {}, Training recall: {}'.format(train_precision, train_recall))
print('Test precision: {}, Test recall: {}'.format(train_recall, test_recall))

"""**Plotting the Decision Tree**"""

from sklearn import tree
import graphviz

max_depth_value = 3

exported = tree.export_graphviz(
    decision_tree=mytree,
    out_file=None,
    feature_names=cols,
    precision=1,
    class_names=['Not churn', 'Churn'],
    filled=True,
    max_depth=max_depth_value
)

graph = graphviz.Source(exported)
display(graph)

"""**Random Forest**"""

# Create and train the Random Forest model
model_rf = RandomForestClassifier(n_estimators=500, oob_score=True, n_jobs=-1,
                                  random_state=50, max_features="auto",
                                  max_leaf_nodes=30)
model_rf.fit(train_X, train_Y)

# Predictions on the training set
pred_train_Y = model_rf.predict(train_X)

# Predictions on the test set
pred_test_Y = model_rf.predict(test_X)

# Calculate metrics
train_accuracy = accuracy_score(train_Y, pred_train_Y)
test_accuracy = accuracy_score(test_Y, pred_test_Y)
train_precision = round(precision_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_precision = round(precision_score(test_Y, pred_test_Y, pos_label='Yes'), 4)
train_recall = round(recall_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_recall = round(recall_score(test_Y, pred_test_Y, pos_label='Yes'), 4)

# Print the results
print('Training Accuracy:', round(train_accuracy, 4))
print('Test Accuracy:', round(test_accuracy, 4))
print('Training Precision: {}, Training Recall: {}'.format(train_precision, train_recall))
print('Test Precision: {}, Test Recall: {}'.format(test_precision, test_recall))

"""Confudion Matrix"""

plt.figure(figsize=(4,3))
sns.heatmap(confusion_matrix(test_Y, prediction_test),
                annot=True,fmt = "d",linecolor="k",linewidths=3)

plt.title(" RANDOM FOREST CONFUSION MATRIX",fontsize=14)
plt.show()

"""**AdaBoost Classifier**"""

# Create and train the AdaBoost Classifier
a_model = AdaBoostClassifier()
a_model.fit(train_X, train_Y)

# Predictions on the training set
pred_train_Y = a_model.predict(train_X)

# Predictions on the test set
pred_test_Y = a_model.predict(test_X)

# Calculate metrics
train_accuracy = accuracy_score(train_Y, pred_train_Y)
test_accuracy = accuracy_score(test_Y, pred_test_Y)
train_precision = round(precision_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_precision = round(precision_score(test_Y, pred_test_Y, pos_label='Yes'), 4)
train_recall = round(recall_score(train_Y, pred_train_Y, pos_label='Yes'), 4)
test_recall = round(recall_score(test_Y, pred_test_Y, pos_label='Yes'), 4)

# Print the results
print('Training Accuracy:', round(train_accuracy, 4))
print('Test Accuracy:', round(test_accuracy, 4))
print('Training Precision: {}, Training Recall: {}'.format(train_precision, train_recall))
print('Test Precision: {}, Test Recall: {}'.format(test_precision, test_recall))

"""Confusion Matrix"""

plt.figure(figsize=(4,3))
sns.heatmap(confusion_matrix(test_Y, a_preds),
                annot=True,fmt = "d",linecolor="k",linewidths=3)

plt.title("AdaBoost Classifier Confusion Matrix",fontsize=14)
plt.show()