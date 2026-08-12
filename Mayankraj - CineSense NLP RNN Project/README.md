# MovieMood 

Advanced Cinematic Sentiment & Context Intelligence Dashboard.

This project uses a Simple Recurrent Neural Network (RNN) built with TensorFlow/Keras to analyze the sentiment of movie reviews. It is trained on the IMDB 50K Movie Reviews dataset and classifies reviews as Positive or Negative. In addition, the Streamlit dashboard heuristically determines the movie genre based on the review's context.

## Project Structure

- `Simple_RNN_NLP_Training.ipynb`: Jupyter Notebook documenting the data preprocessing, model building, and training process of the RNN on the IMDB dataset.
- `Simple_RNN_NLP_Testing.ipynb`: Jupyter Notebook demonstrating how to decode reviews and test the trained model locally.
- `app.py`: The beautiful, interactive Streamlit dashboard allowing users to input a movie review and get real-time sentiment analysis and genre prediction.
- `simple_imdb_rnn_model.keras` & `simple_imdb_rnn_model.h5`: The trained Simple RNN model files.
- `requirements.txt`: Python dependencies needed to run the project.

## How to Run the Dashboard

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

3. Open your browser to the URL provided in the terminal (usually `http://localhost:8501`).

## Tech Stack
- **Algorithm**: Simple Recurrent Neural Network (RNN)
- **Dataset**: IMDB 50K Movie Reviews
- **Framework**: TensorFlow & Keras
- **UI**: Streamlit with custom CSS (Glassmorphism & Gradients)
