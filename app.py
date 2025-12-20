import streamlit as st
import os
from groq import Groq

# --- PAGE SETUP ---
st.set_page_config(page_title="Pro Content Factory", page_icon="🎯", layout="wide")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #00D26A; /* Fiverr Green */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3em;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Pro Content Studio")
st.markdown("Draft content tailored for specific platforms.")

# --- AUTH ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("⚠️ Error: API Key missing in Secrets.")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Platform Selection
    st.subheader("Select Platforms")
    use_blog = st.checkbox("📝 Blog Post (Medium)", value=True)
    use_linkedin = st.checkbox("💼 LinkedIn Post", value=True)
    use_twitter = st.checkbox("🐦 Twitter Thread", value=True)
    use_insta = st.checkbox("📸 Instagram Caption", value=False)
    
    # 2. Tone
    st.subheader("Content Tone")
    tone = st.selectbox("Choose Tone", ["Viral & Punchy", "Professional & Clean", "Storytelling", "Funny & Witty"])

# --- MAIN INPUT ---
user_input = st.text_area(
    "What do you want to create?", 
    placeholder="Enter a Topic (e.g. 'Future of AI') OR a Custom Prompt (e.g. 'Write a controversial post about remote work')",
    height=100
)

# --- THE SMART BRAIN ---
def generate_content(input_text, platforms, tone):
    
    # Constructing the instructions dynamically based on user selection
    instructions = f"""
    You are an expert Social Media Strategist.
    
    **INPUT:** "{input_text}"
    **TONE:** {tone}
    
    Generate content ONLY for the following selected platforms. 
    Separate them clearly with Markdown headers (e.g., # LINKEDIN).
    """
    
    if platforms['blog']:
        instructions += """
        \n# BLOG POST
        - Headline: Catchy and SEO optimized.
        - Structure: Intro -> 3 Key Points -> Conclusion.
        - Style: High-value, skimmable.
        """
        
    if platforms['linkedin']:
        instructions += """
        \n# LINKEDIN POST
        - Format: Short lines (Broetry style).
        - Hook: First sentence must stop the scroll.
        - CTA: End with a question.
        """
        
    if platforms['twitter']:
        instructions += """
        \n# TWITTER THREAD
        - Tweet 1: The Hook.
        - Tweet 2-N: The Value.
        - Final Tweet: CTA.
        - Format: Numbered list.
        """
        
    if platforms['insta']:
        instructions += """
        \n# INSTAGRAM CAPTION
        - Engaging hook.
        - Short body.
        - 15 Hashtags.
        """

    instructions += "\nDo not include filler text. Just the content."

    # Call AI
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a top-tier ghostwriter."},
            {"role": "user", "content": instructions}
        ],
        temperature=0.7
    )
    return completion.choices[0].message.content

# --- GENERATE BUTTON ---
if st.button("✨ Generate Selected Content"):
    if not user_input:
        st.warning("Please enter a topic or prompt.")
    elif not (use_blog or use_linkedin or use_twitter or use_insta):
        st.warning("Please select at least one platform from the sidebar.")
    else:
        with st.spinner('Crafting your content...'):
            try:
                # Prepare platform list
                platforms = {
                    'blog': use_blog,
                    'linkedin': use_linkedin,
                    'twitter': use_twitter,
                    'insta': use_insta
                }
                
                result = generate_content(user_input, platforms, tone)
                
                st.success("Drafts Created!")
                
                # --- DISPLAY IN TABS (Cleaner UI) ---
                # Create tabs dynamically based on selection
                tabs_list = []
                if use_blog: tabs_list.append("📝 Blog")
                if use_linkedin: tabs_list.append("💼 LinkedIn")
                if use_twitter: tabs_list.append("🐦 Twitter")
                if use_insta: tabs_list.append("📸 Insta")
                tabs_list.append("💾 All")
                
                tabs = st.tabs(tabs_list)
                
                # We need to split the AI text manually or just show full text in respective tabs
                # For simplicity in this Lite version, we show the full text in the 'All' tab
                # and instructions on how to use it.
                
                # (Smart Splitting is hard without complex code, so we display the full result neatly)
                with tabs[-1]: # The "All" Tab
                    st.markdown(result)
                    st.download_button("Download All (.md)", result, file_name="content_pack.md")
                
                # In a real app, we would parse the text, but for now, the user sees everything clearly separated by headers.
                
            except Exception as e:
                st.error(f"Error: {e}")
