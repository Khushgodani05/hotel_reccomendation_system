###Here we do not use lemmatization with pos_tag in recommendation systems for faster responses in real world applications 
import pandas as pd
import numpy as np
import re
import streamlit as st
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import pickle


def clean_text(text, stop):
    text = re.sub("[^a-zA-Z0-9]", " ", str(text)).lower().split()
    return " ".join(w for w in text if w not in stop)


@st.cache_resource(show_spinner="Loading  recommendor System...")
def load_model():
    data = pd.read_excel("./dataset/final_data.xlsx")

    data["country"] = data["country"].str.strip().str.lower()
    data["tags_combined"] = data["tags_combined"].fillna("")

    stop = set(stopwords.words("english"))
    with open("count_vectorizer.pkl", "rb") as f:
        cv = pickle.load(f)

    data["clean_tags"] = data["tags_combined"].apply(
        lambda x: clean_text(x, stop)
    )

    hotel_vectors = cv.transform(data["clean_tags"])

    return data, cv, hotel_vectors, stop


def recommend_hotel(country, description, top_n=5):
    data, cv, hotel_vectors, stop = load_model()

    country = country.strip().lower()
    mask = (data["country"] == country).to_numpy()

    if not mask.any():
        return pd.DataFrame(columns=["hotel_name", "hotel_address", "final_rating"])

    query_clean = clean_text(description, stop)
    query_vec = cv.transform([query_clean])

    similarity = cosine_similarity(query_vec, hotel_vectors[mask]).flatten()

    result = data.loc[mask].copy()
    result["cosine_score"] = similarity

    result = result.sort_values(
        by=["cosine_score", "final_rating", "review_no"],
        ascending=[False, False, False]
    ).drop_duplicates("hotel_name").reset_index(drop=True)

    return result[["hotel_name", "hotel_address", "final_rating"]].head(top_n)





print(recommend_hotel("uK","I want a hotel with good food and swimming pool"))




