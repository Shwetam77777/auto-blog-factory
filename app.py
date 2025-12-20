import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# --- CONFIG & KEYS ---
st.set_page_config(page_title="Viral Content Generator", page_icon="🔥", layout="wide")
st.title("🔥 Viral Content Factory (Fiverr Mode)")
st.markdown("Generates: **Blog + LinkedIn + Twitter + Instagram** from one topic.")

# Fix for search tool
os.environ["SCARF_NO_ANALYTICS"] = "true"

# Sidebar for Keys (Client ya aapki apni keys)
with st.sidebar:
    st.header("🔑 API Keys")
    groq_key = st.text_input("Groq API Key (Required)", type="password")
    gemini_key = st.text_input("Gemini API Key (Optional for Review)", type="password")
    
    st.info("💡 Tip: Groq Llama-3 is Free & fast.")

if not groq_key:
    st.warning("Please enter Groq API Key to start.")
    st.stop()

# --- BRAINS ---
# Main Writer (Llama 3 - Best for Creative Writing)
llm_writer = ChatGroq(
    temperature=0.7, 
    model_name="llama3-70b-8192", 
    api_key=groq_key
)

# Optional Reviewer
if gemini_key:
    llm_reviewer = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=gemini_key)
else:
    llm_reviewer = llm_writer # Agar Gemini nahi hai to Groq hi review karega

# --- AGENTS ---

search_tool = DuckDuckGoSearchRun()

# 1. The Trend Hunter
researcher = Agent(
    role='Viral Strategist',
    goal='Find what is trending about {topic} and high-click keywords.',
    backstory="You analyze viral hooks. You don't just find facts, you find 'Angles' that get clicks.",
    tools=[search_tool],
    llm=llm_writer,
    verbose=True
)

# 2. The Omni-Channel Writer
writer = Agent(
    role='Social Media Ghostwriter',
    goal='Write content tailored for 4 different platforms.',
    backstory="""
    You are a master copywriter.
    - Blogs: SEO optimized, storytelling.
    - LinkedIn: Professional, short paragraphs, strong hooks.
    - Twitter: Punchy, thread format.
    - Instagram: Engaging caption with hashtags.
    """,
    llm=llm_writer,
    verbose=True
)

# --- WORKFLOW ---

def run_viral_factory(topic):
    # Task 1: Research
    t1 = Task(
        description=f"Research {topic}. Find 3 viral hooks/angles and 5 high-volume keywords.",
        agent=researcher,
        expected_output="List of hooks and keywords."
    )

    # Task 2: Create Content Pack
    t2 = Task(
        description=f"""
        Using the research, create a CONTENT BUNDLE for topic: {topic}.
        
        SECTION 1: MEDIUM BLOG POST (1000 words)
        - Catchy Title
        - SEO Headers (H2, H3)
        - Conclusion
        
        SECTION 2: LINKEDIN POST
        - Hook (First line must grab attention)
        - Value body (bullet points)
        - Call to Action
        
        SECTION 3: TWITTER THREAD (5 Tweets)
        - Tweet 1: The Hook
        - Tweet 2-4: The Value
        - Tweet 5: The Conclusion
        
        SECTION 4: INSTAGRAM CAPTION
        - Engaging short summary
        - 10-15 Hashtags
        """,
        agent=writer,
        expected_output="A full markdown document with all 4 sections."
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[t1, t2],
        verbose=2
    )
    
    return crew.kickoff()

# --- UI ---

topic = st.text_input("Enter Topic (e.g. 'AI for Passive Income'):")

if st.button("🚀 Generate Content Pack"):
    with st.spinner('Generating Viral Content...'):
        try:
            result = run_viral_factory(topic)
            
            # Display Results
            st.success("Content Generated!")
            st.markdown("### Preview:")
            st.markdown(result)
            
            # Download Button (Deliverable for Fiverr)
            st.download_button(
                label="📥 Download Final File (For Client)",
                data=str(result),
                file_name=f"{topic}_Viral_Pack.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
