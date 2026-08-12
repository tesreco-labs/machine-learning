import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

df=pd.read_csv('height_weight.csv')

plt.scatter(df['Weight'],df['Height'])
plt.xlabel("Weight")
plt.ylabel("Height")

plt.show()

X=df[['Weight']] 
y=df[['Height']]

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.20,random_state=42)

## Standardize the dataset
from sklearn.preprocessing import StandardScaler
scaler=StandardScaler()
X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test) 

#X_train=np.array(X_train).reshape(-1,1)
#X_test=np.array(X_test).reshape(-1,1)

regressor=LinearRegression()

regressor.fit(X_train,y_train)

print("Coefficient : ",regressor.coef_)
print("Intercept : ",regressor.intercept_)

#regressor.predict(scaler.transform([[75]]))

# Saving Standarization Object
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Save model
with open("weight_height_model.pkl", "wb") as f:
    pickle.dump(regressor, f)

print("Model pickeled")



