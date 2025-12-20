import streamlit as st
import os
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="Premium Content Factory", page_icon="✨", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ Premium Viral Content Factory")

# --- AUTH ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Error: GROQ_API_KEY missing.")
    st.stop()

client = Groq(api_key=api_key)

# --- THE LOGIC ---
def generate_premium_content(topic, tone):
    prompt = f"""
    Act as a World-Class Editor. Topic: "{topic}". Tone: {tone}.
    Create a content pack in Markdown:
    
    1. Blog Post (Headline, Intro, 3 Points, Conclusion)
    2. LinkedIn Post (Hook, Bullet points, CTA)
    3. Twitter Thread (5 Tweets)
    4. Instagram Caption (With hashtags)
    """
    
    completion = client.chat.completions.create(
        # THIS WAS THE ISSUE - UPDATED TO NEW MODEL
        model="llama-3.3-70b-versatile", 
        messages=[
            {"role": "system", "content": "You are a creative expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return completion.choices[0].message.content

# --- UI ---
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Enter Topic:")
with col2:
    tone = st.selectbox("Tone:", ["Professional", "Funny", "Urgent"])

if st.button("🚀 Generate Content"):
    if not topic:
        st.warning("Enter a topic first.")
    else:
        with st.spinner('Generating...'):
            try:
                result = generate_premium_content(topic, tone)
                st.success("Success!")
                st.markdown(result)
            except Exception as e:
                st.error(f"Error: {e}")
