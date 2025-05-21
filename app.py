import streamlit as st
import pandas as pd
import openai
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="سوال روزانه", page_icon="🧠")
st.title("🧠 سوال روزانه برای رشد شخصی")

def get_today_question():
    df = pd.read_csv("questions.csv")
    today = datetime.now().day % len(df)
    return df.iloc[today]["question"]

def save_to_db(question, answer):
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS responses (timestamp TEXT, question TEXT, answer TEXT)")
    c.execute("INSERT INTO responses VALUES (?, ?, ?)", (datetime.now().isoformat(), question, answer))
    conn.commit()
    conn.close()

def analyze_with_gpt(answer):
    prompt = f"Analyze this response in 3 lines: emotional tone, clarity, and potential insight.\n\nResponse: {answer}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response["choices"][0]["message"]["content"]

question = get_today_question()
st.subheader("📌 سوال امروز:")
st.info(question)

answer = st.text_area("✍️ پاسخ خود را وارد کنید:")
if st.button("ارسال و تحلیل"):
    if answer.strip():
        save_to_db(question, answer)
        with st.spinner("در حال تحلیل..."):
            analysis = analyze_with_gpt(answer)
        st.success("✅ تحلیل آماده است")
        st.write(analysis)
    else:
        st.warning("لطفاً پاسخ را وارد کن.")
