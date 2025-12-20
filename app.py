import streamlit as st
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Viral Content Factory", page_icon="⚡")
st.title("⚡ Viral Content Factory")

# --- SECRETS LOAD ---
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except:
    st.info("⚠️ Secrets not found. Please add keys in Settings.")
    st.stop()

# --- SAFETY BLOCK FOR TOOLS (NO MORE RED BOX) ---
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq

# Try to load Search, if fail, use Dummy (Prevents Crash)
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
    st.toast("✅ Search Tool Loaded", icon="🟢")
except Exception as e:
    st.warning(f"⚠️ Search tool failed to load ({e}). Using AI Knowledge only.")
    # Dummy tool to keep agents working
    from langchain.tools import tool
    @tool("Search")
    def search_tool(query: str):
        """Fallback tool when search fails."""
        return "Search data unavailable. Use internal knowledge."

# --- BRAIN ---
llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192")

# --- AGENTS ---
researcher = Agent(
    role='Viral Researcher',
    goal='Find angles for {topic}',
    backstory="You are a trend hunter.",
    tools=[search_tool], # Uses safety tool if main crashes
    llm=llm,
    verbose=True
)

writer = Agent(
    role='Viral Writer',
    goal='Create Blog, LinkedIn & Twitter content.',
    backstory="You write viral hooks.",
    llm=llm,
    verbose=True
)

# --- WORKFLOW ---
def run_factory(topic):
    t1 = Task(description=f"Find 3 viral hooks for: {topic}", agent=researcher, expected_output="List of hooks")
    t2 = Task(description=f"Write LinkedIn Post, Twitter Thread & Blog for: {topic}", agent=writer, expected_output="Content Pack")
    crew = Crew(agents=[researcher, writer], tasks=[t1, t2], verbose=2)
    return crew.kickoff()

# --- UI ---
topic = st.text_input("Enter Topic (e.g. AI Marketing):")
if st.button("Generate Content"):
    with st.spinner('Thinking...'):
        try:
            result = run_factory(topic)
            st.success("Done!")
            st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")
