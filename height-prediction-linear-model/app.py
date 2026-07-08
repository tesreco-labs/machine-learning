from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

#Load Scaler Object for input weights
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Load model
with open("weight_height_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return "Height Prediction API"

'''
Method: predict_height()
Input:  weight value or list of weights
Output: json containing input weight and predicted height value or height list 
'''
 
@app.route("/predictHeightList", methods=["POST"])
def predict_height_list():
    data = request.get_json()

    weight = data["weight"] # list of weight
    
    weight_scaled = scaler.transform(np.array(weight).reshape(-1, 1))  # Standar Scaler require 2D array 
    
    prediction = model.predict(weight_scaled)
    print(type(prediction))
    
    if(len(prediction)>1):
        return jsonify({
            "weight": weight,
            "predicted_Height": prediction.tolist()
        })
    else : 
        return jsonify({
        "weight": weight,
        "predicted_Height": round(float(prediction[0][0]), 2)
    })   

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)