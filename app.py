import streamlit as st
import os
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="Premium Content Factory", page_icon="✨", layout="wide")

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        border-radius: 10px;
    }
    .reportview-container {
        background: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ Premium Viral Content Factory")
st.markdown("Generates **High-Retention** content for Blog, LinkedIn, Twitter & Insta.")

# --- SILENT LOGIN ---
try:
    # Keys load karna (Secrets se)
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Error: GROQ_API_KEY nahi mila. Settings > Secrets check karein.")
    st.stop()

client = Groq(api_key=api_key)

# --- THE "NO COMPROMISE" BRAIN ---
def generate_premium_content(topic, tone):
    
    # Ye Prompt 'Agents' ka kaam karega (Research -> Draft -> Polish)
    prompt = f"""
    Act as a World-Class Chief Editor and Social Media Strategist.
    
    My Topic is: "{topic}"
    Target Tone: {tone}
    
    I need a content pack that is NOT generic AI text. It must be specific, data-driven, and highly engaging.
    
    Create these 4 assets strictly in Markdown:
    
    ---
    ### 1. 📝 High-Impact Blog Post (Medium/Website)
    - **Headline:** Viral & Clickable (No clickbait).
    - **Structure:** Hook -> Problem -> Solution -> Actionable Tips.
    - **Quality Control:** Use short paragraphs. No fluff words like "In conclusion".
    
    ---
    ### 2. 💼 LinkedIn Authority Post
    - **Format:** Broetry style (One sentence per line).
    - **Hook:** Start with a controversial or strong statement.
    - **Value:** 3-5 Bullet points.
    - **CTA:** Ask a specific question to drive comments.
    
    ---
    ### 3. 🐦 Twitter Thread (Viral Style)
    - **Tweet 1:** The Hook.
    - **Tweet 2-4:** The Meat (Insights).
    - **Tweet 5:** The Summary & CTA.
    
    ---
    ### 4. 📸 Instagram Caption
    - Engaging story-based caption.
    - 15 High-Volume Hashtags relevant to the topic.
    
    ---
    """
    
    completion = client.chat.completions.create(
        model="llama3-70b-8192", # The smartest free model
        messages=[
            {"role": "system", "content": "You are a perfectionist content creator. You hate generic output."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=5000,
    )
    
    return completion.choices[0].message.content

# --- UI INTERFACE ---
col1, col2 = st.columns([3, 1])

with col1:
    topic = st.text_input("Enter Topic:", placeholder="e.g. AI Agents for Business")

with col2:
    tone = st.selectbox("Select Tone:", ["Professional", "Witty/Funny", "Storytelling", "Urgent"])

if st.button("🚀 Generate Premium Content"):
    if not topic:
        st.warning("Please write a topic first.")
    else:
        with st.spinner('🧠 AI is Brainstorming & Writing (High Quality)...'):
            try:
                # Direct Call - No Libraries to Crash
                result = generate_premium_content(topic, tone)
                
                st.success("✅ Content Ready!")
                
                # Show Result
                st.markdown(result)
                
                # Download File
                st.download_button(
                    label="📥 Download Content Pack (.md)",
                    data=result,
                    file_name=f"{topic}_Premium_Pack.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
