import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.datasets import imdb

# -------------------- Configuration --------------------
st.set_page_config(page_title="MovieMood", layout="wide")

# Custom CSS for a state-of-the-art, premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    body { background-color: #050505; font-family: 'Poppins', sans-serif; }
    .stApp { background: radial-gradient(circle at 15% 50%, #1a1a2e 0%, #050505 100%); }
    
    /* Title Gradient */
    .title-glow {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
        line-height: 1.2;
    }
    
    /* Result Card Glassmorphism */
    .result-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 35px;
        margin-top: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .result-card:hover {
        transform: translateY(-5px);
        border-color: rgba(79, 172, 254, 0.4);
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6, p { color: #e2e8f0; font-family: 'Poppins', sans-serif; }
    
    /* Custom Inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(0, 0, 0, 0.4) !important; 
        color: #f8fafc !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 1.05rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4facfe !important;
        box-shadow: 0 0 0 1px #4facfe !important;
    }
    
    /* Button */
    .stButton>button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover { 
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.6);
        transform: translateY(-2px);
    }
    
    /* Meta Tags */
    .meta-tag {
        display: inline-block;
        background: rgba(79, 172, 254, 0.1);
        border: 1px solid rgba(79, 172, 254, 0.3);
        border-radius: 20px;
        padding: 6px 18px;
        font-size: 0.9em;
        font-weight: 600;
        margin-right: 12px;
        margin-bottom: 15px;
        color: #4facfe;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .sentiment-positive { color: #10b981; font-weight: 800; font-size: 1.6em; text-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    .sentiment-negative { color: #ef4444; font-weight: 800; font-size: 1.6em; text-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }

    /* Sidebar tweaks */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .sidebar-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #4facfe;
        transition: transform 0.2s ease;
    }
    .sidebar-card:hover {
        transform: translateX(5px);
        background: rgba(255,255,255,0.04);
    }
    .sidebar-label { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px; }
    .sidebar-value { color: #f8fafc; font-size: 1.05rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# -------------------- Model Loading --------------------
@st.cache_resource
def load_assets():
    model = load_model("simple_imdb_rnn_model.keras")
    word_index = imdb.get_word_index()
    return model, word_index

model, word_index = load_assets()
MAX_LEN = 500

def preprocess_review(review):
    review = review.lower()
    for char in [".", ",", "!", "?", "(", ")", '"']:
        review = review.replace(char, "")
    
    words = review.split()
    sequence = []
    for word in words:
        index = word_index.get(word)
        if index is not None and index < 9997:
            sequence.append(index + 3)
        else:
            sequence.append(2) 
            
    return pad_sequences([sequence], maxlen=MAX_LEN)

def guess_genre(review):
    review_lower = review.lower()
    genres = {
        "Action": ["action", "fight", "explosion", "stunt", "thrill", "chase", "superhero", "gun"],
        "Comedy": ["funny", "hilarious", "laugh", "comedy", "joke", "humor", "amusing", "hilarious"],
        "Horror": ["scary", "terrifying", "horror", "jump scare", "fear", "creepy", "spooky", "blood"],
        "Romance": ["love", "romantic", "romance", "heartwarming", "relationship", "couple"],
        "Sci-Fi": ["space", "alien", "science fiction", "future", "time travel", "robot", "sci-fi"],
        "Drama": ["drama", "emotional", "tragic", "sad", "moving", "tearjerker", "intense"],
        "Thriller": ["suspense", "thriller", "mystery", "plot twist", "tense", "gripping", "detective"]
    }
    
    genre_scores = {g: 0 for g in genres}
    for genre, keywords in genres.items():
        for keyword in keywords:
            if keyword in review_lower:
                genre_scores[genre] += 1
                
    best_genre = max(genre_scores, key=genre_scores.get)
    if genre_scores[best_genre] == 0:
        return "General / Uncategorized"
    return best_genre

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #4facfe; font-weight: 800; margin-bottom: 30px; letter-spacing: 1px;'>Tech Stack</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-label">Algorithm</div>
        <div class="sidebar-value">Simple Recurrent Neural Network (RNN)</div>
    </div>
    <div class="sidebar-card">
        <div class="sidebar-label">Dataset</div>
        <div class="sidebar-value">IMDB 50K Movie Reviews</div>
    </div>
    <div class="sidebar-card">
        <div class="sidebar-label">Framework</div>
        <div class="sidebar-value">TensorFlow & Keras</div>
    </div>
    <div class="sidebar-card">
        <div class="sidebar-label">Sequence Length</div>
        <div class="sidebar-value">500 Tokens</div>
    </div>
    """, unsafe_allow_html=True)
    
# -------------------- Main UI --------------------
col1, col2, col3 = st.columns([1.5, 6, 1.5])
with col2:
    st.markdown("<div class='title-glow'>MovieMood</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.3rem; color: #94a3b8; margin-bottom: 2.5rem; font-weight: 300;'>Advanced Cinematic Sentiment & Context Intelligence</p>", unsafe_allow_html=True)

    with st.form("review_form"):
        movie_name = st.text_input("Movie Title (Optional)", placeholder="e.g., Inception")
        review_text = st.text_area("Review", height=200, placeholder="Write your review here...")
        submitted = st.form_submit_button("Analyze Sentiment")

    if submitted:
        if review_text.strip():
            # Preprocess and Predict
            x = preprocess_review(review_text)
            score = float(model.predict(x, verbose=0)[0][0])
            
            sentiment_label = "Positive" if score >= 0.5 else "Negative"
            confidence = score if score >= 0.5 else 1 - score
            sentiment_class = "sentiment-positive" if sentiment_label == "Positive" else "sentiment-negative"
            
            genre = guess_genre(review_text)
            title_display = movie_name.strip() if movie_name.strip() else "Unknown Movie"
            
            st.markdown(f"""
            <div class="result-card">
                <h2 style="margin-top: 0; margin-bottom: 15px; font-weight: 800; letter-spacing: -0.5px;">{title_display}</h2>
                <div>
                    <span class="meta-tag">🎬 {genre}</span>
                    <span class="meta-tag">🎯 Confidence: {confidence*100:.1f}%</span>
                </div>
                <p style="margin-top: 25px; font-style: italic; color: #cbd5e1; font-size: 1.15rem; line-height: 1.7;">"{review_text}"</p>
                <div style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 25px; display: flex; align-items: center;">
                    <span style="color: #94a3b8; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Assessment:</span> 
                    <span class="{sentiment_class}" style="margin-left: 15px;">{sentiment_label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a review to analyze.")

st.markdown("<br><br><hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>Powered by Deep Learning & Natural Language Processing</p>", unsafe_allow_html=True)