import streamlit as st
import os
from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# --- CONFIGURATION ---
st.set_page_config(page_title="Viral Content Engine", page_icon="⚡", layout="wide")
st.title("⚡ Viral Content Factory")
st.markdown("Generates **Blog + LinkedIn + Twitter + Instagram** assets instantly.")

# Fix for search tool error
os.environ["SCARF_NO_ANALYTICS"] = "true"

# --- SILENT AUTHENTICATION ---
# The app checks the internal safe (Secrets) for keys.
# No boxes on screen. Clean and Professional.

try:
    groq_key = st.secrets["GROQ_API_KEY"]
    gemini_key = st.secrets["GEMINI_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Setup Error: Keys are missing in Secrets.")
    st.stop()
except KeyError:
    st.error("⚠️ Setup Error: Please add GROQ_API_KEY and GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# --- THE BRAINS ---
# Main Writer (Llama 3 - Free & Fast)
llm_writer = ChatGroq(
    temperature=0.7, 
    model_name="llama3-70b-8192", 
    api_key=groq_key
)

# --- THE AGENTS ---

search_tool = DuckDuckGoSearchRun()

# 1. Trend Researcher
researcher = Agent(
    role='Viral Strategist',
    goal='Find high-performing angles and keywords for {topic}.',
    backstory="You are a digital marketing expert. You find what people are actually clicking on right now.",
    tools=[search_tool],
    llm=llm_writer,
    verbose=True
)

# 2. Content Creator
writer = Agent(
    role='Social Media Copywriter',
    goal='Create a complete content pack (Blog, LinkedIn, Twitter, Insta).',
    backstory="You write punchy, engaging content. You hate boring corporate speak.",
    llm=llm_writer,
    verbose=True
)

# --- THE WORKFLOW ---
def run_factory(topic):
    task1 = Task(
        description=f"Research {topic}. Identify 3 viral angles and 5 trending keywords.",
        agent=researcher,
        expected_output="Bullet points of viral angles."
    )

    task2 = Task(
        description=f"""
        Create a VIRAL CONTENT PACK for: '{topic}'.
        
        1. **MEDIUM BLOG** (800 words): Catchy title, H2 headers, storytelling style.
        2. **LINKEDIN POST**: Strong hook (first sentence), whitespace formatting, Call to Action.
        3. **TWITTER THREAD**: 5 tweets. Tweet 1 is the hook.
        4. **INSTAGRAM**: Caption with emojis and 15 hashtags.
        """,
        agent=writer,
        expected_output="Complete markdown content pack."
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=2
    )
    return crew.kickoff()

# --- THE INTERFACE ---
# Simple, clean input box. No settings clutter.

topic = st.text_input("Enter Topic (e.g. 'How to start Freelancing'):", placeholder="Type your topic here...")

if st.button("🚀 Generate Content Pack"):
    with st.spinner('🔍 Analyzing Trends & Writing Content...'):
        try:
            result = run_factory(topic)
            
            # Show success and results
            st.success("✅ Content Generated Successfully!")
            
            tab1, tab2 = st.tabs(["📄 Preview", "💾 Download"])
            
            with tab1:
                st.markdown(result)
            
            with tab2:
                st.markdown("### Ready for Delivery")
                st.download_button(
                    label="📥 Download Final Report (.md)",
                    data=str(result),
                    file_name=f"Viral_Content_{topic}.md",
                    mime="text/markdown"
                )
                
        except Exception as e:
            st.error(f"Something went wrong: {e}")
