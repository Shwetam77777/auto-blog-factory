import streamlit as st
import os
import language_tool_python
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Auto-Blog Factory", page_icon="✍️")
st.title("🤖 Autonomous Blog Factory")
st.markdown("Generates **Human-Quality**, **Error-Free** articles from a single topic.")

# API Key Input (Secure)
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

if not groq_api_key:
    st.warning("Please enter your Groq API Key to proceed. (Get one for free at console.groq.com)")
    st.stop()

# Initialize LLM (Llama 3.3 70B is fast and human-like)
llm = ChatGroq(
    temperature=0.7, 
    model_name="llama3-70b-8192", 
    api_key=groq_api_key
)

# Initialize Tools
search_tool = DuckDuckGoSearchRun()
tool_grammar = language_tool_python.LanguageTool('en-US')

# --- 2. AGENT DEFINITIONS ---

# Agent 1: The Researcher
researcher = Agent(
    role='Investigative Journalist',
    goal='Find real-world data, recent news, and concrete examples about: {topic}',
    backstory="You hate generic fluff. You dig deep to find dates, specific numbers, and expert quotes.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=llm
)

# Agent 2: The Writer (The Humanizer)
writer = Agent(
    role='Senior Feature Writer',
    goal='Write a blog post that sounds 100% human and 0% AI.',
    backstory="""
    You are a world-class copywriter. 
    CRITICAL RULES:
    1. NEVER use words like "In conclusion", "realm", "delve", "game-changer", "unleash".
    2. Write in a conversational tone (use "I", "we", "you").
    3. Vary sentence length. Mix short punchy sentences with longer descriptive ones.
    4. Use analogies and rhetorical questions.
    """,
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Agent 3: The Strict Editor (Zero Error Policy)
editor = Agent(
    role='Chief Editor',
    goal='Proofread the text to ensure it has NO spelling or grammar mistakes.',
    backstory="""
    You are a perfectionist. You review the draft for any logical inconsistencies. 
    You do NOT rewrite the style, you only fix structural errors and clarity.
    """,
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- 3. TASKS ---

def run_content_factory(topic):
    # Task 1: Research
    task1 = Task(
        description=f"Research {topic}. Find 3 unique stats/facts and 1 recent event related to it.",
        agent=researcher,
        expected_output="A list of verified facts with sources."
    )

    # Task 2: Write
    task2 = Task(
        description=f"Write a 1000-word blog post on {topic} using the research. Use Markdown. Focus on storytelling.",
        agent=writer,
        expected_output="A full blog post draft."
    )

    # Task 3: Edit
    task3 = Task(
        description="Review the draft. Fix flow and logic. Output the final Markdown.",
        agent=editor,
        expected_output="Final Polished Article."
    )

    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[task1, task2, task3],
        verbose=2,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    return result

# --- 4. THE UI TRIGGER ---

topic = st.text_input("Enter Blog Topic:")

if st.button("Generate Article"):
    with st.spinner('Agents are working... (Researching -> Writing -> Editing)'):
        try:
            # 1. Generate Content
            raw_article = run_content_factory(topic)
            
            # 2. The Final Polish (Programmatic Spell Check)
            st.text("Running final programmatic spell-check...")
            final_clean_article = tool_grammar.correct(str(raw_article))
            
            # 3. Display
            st.success("Article Generated Successfully!")
            st.markdown(final_clean_article)
            
            # 4. Download Option
            st.download_button(
                label="Download Article as Markdown",
                data=final_clean_article,
                file_name=f"{topic.replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
