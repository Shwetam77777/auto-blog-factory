import streamlit as st
import os

# --- SETUP ---
st.set_page_config(page_title="Viral Content Factory", page_icon="⚡")
st.title("⚡ Viral Content Factory")

# --- SECRETS LOAD ---
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except:
    pass

# --- IMPORTS ---
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq

# --- BRAIN ---
# Agar key nahi mili to error dikhayega
if "GROQ_API_KEY" not in os.environ:
    st.error("⚠️ GROQ_API_KEY not found in Secrets.")
    st.stop()

llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192")

# --- AGENTS (No Tools, Just Brain) ---
researcher = Agent(
    role='Viral Strategist',
    goal='Brainstorm viral angles for {topic}',
    backstory="You are a marketing genius. You know what goes viral.",
    llm=llm,
    verbose=True
)

writer = Agent(
    role='Content Creator',
    goal='Write Blog, LinkedIn & Twitter content.',
    backstory="You write engaging social media posts.",
    llm=llm,
    verbose=True
)

# --- WORKFLOW ---
def run_factory(topic):
    t1 = Task(
        description=f"Brainstorm 3 viral hooks and angles for: {topic}",
        agent=researcher,
        expected_output="Bullet points of ideas"
    )
    
    t2 = Task(
        description=f"""
        Using the ideas, create a content pack for: {topic}
        1. LinkedIn Post (With Hook & CTA)
        2. Twitter Thread (5 Tweets)
        3. Instagram Caption (With Hashtags)
        """,
        agent=writer,
        expected_output="Markdown Content Pack"
    )
    
    crew = Crew(agents=[researcher, writer], tasks=[t1, t2], verbose=2)
    return crew.kickoff()

# --- UI ---
topic = st.text_input("Enter Topic (e.g. AI for Business):")

if st.button("Generate Content"):
    with st.spinner('Generating...'):
        try:
            result = run_factory(topic)
            st.success("Success!")
            st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")
