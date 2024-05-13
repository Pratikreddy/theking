import streamlit as st
from openai import OpenAI
from groq import Groq

# Set custom page configuration
st.set_page_config(page_title="KING P", page_icon="👑", layout="wide", initial_sidebar_state="expanded")

# Available models
gpt_models = ["gpt-4-turbo", "gpt-4-0125-preview", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-instruct"]
groq_models = ["llama3-8b-8192", "gemma-7b-it", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Page title
st.title("The Kingdom")
st.write("**A collaborative problem-solving system with a wise King and knowledgeable Peasants.**")

# Sidebar
st.sidebar.write("    **PRATIK REDDY**")
st.sidebar.write("https://twitter.com/pratikredy")
st.sidebar.write("https://www.youtube.com/@pratik_AI")

# API Key Inputs (side by side)
col1, col2 = st.columns(2)
with col1:
    openai_api_key = st.text_input("OpenAI Key", type="password", help="Provide your OpenAI API Key")
with col2:
    groq_api_key = st.text_input("Groq Key", type="password", help="Provide your Groq API Key")

# Model Selection for two gangs
st.subheader("Gang Model Selection")
gang_water_models = st.multiselect("Pick your **Gang Water**", gpt_models + groq_models, help="Select models for Gang Water")
gang_earth_models = st.multiselect("Pick your **Gang Earth**", gpt_models + groq_models, help="Select models for Gang Earth")

# Problem Statements for two gangs
st.subheader("Problem Statements")
problem_water = st.text_area("Gang Water Problem", help="Provide the problem for Gang Water")
problem_earth = st.text_area("Gang Earth Problem", help="Provide the problem for Gang Earth")

# Function to call OpenAI API
def openai_call(messages, model, system_message, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": messages}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# Function to call Groq API
def groq_call(messages, model, api_key):
    client = Groq(api_key=api_key)
    system_message = "You are a coder and problem solver expert"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": messages}
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

# Function to consult the gangs
def consult_gang(gang_name, gang_models, problem_statement):
    answers = {}
    for i, model in enumerate(gang_models):
        st.write(f"{gang_name} Peasant {i+1} ({model}) is being consulted...")
        if model in gpt_models:
            response = openai_call(problem_statement, model, "You are a coder and problem solver expert", openai_api_key)
        else:
            response = groq_call(problem_statement, model, groq_api_key)
        answers[f"{gang_name} Peasant {i+1} ({model})"] = response
    return answers

# King's final analysis
def king_analysis(gang_water_info, gang_earth_info, problem_water, problem_earth):
    st.write("The King is analyzing the contributions from both gangs...")
    water_answers = "\n\n".join(f"{name}: {advice}" for name, advice in gang_water_info.items())
    earth_answers = "\n\n".join(f"{name}: {advice}" for name, advice in gang_earth_info.items())
    king_prompt = f"Gang Water Advice:\n{water_answers}\n\nGang Earth Advice:\n{earth_answers}\n\nProblems:\nWater: {problem_water}\nEarth: {problem_earth}"

    king_model = "gpt-4-turbo"  # Example, select appropriately
    king_answer = openai_call(king_prompt, king_model, "You are a wise king deciding which gang provided better insights.", openai_api_key)
    return king_answer

# Process the solution
if st.button("Consult the King"):
    if not (problem_water and problem_earth):
        st.warning("Please enter problem statements for both gangs.")
    elif not (gang_water_models and gang_earth_models):
        st.error("Please select at least one model for each gang.")
    elif not (openai_api_key and groq_api_key):
        st.error("Please enter valid OpenAI and Groq API keys.")
    else:
        st.info("Summoning the gangs and discussing...")
        gang_water_info = consult_gang("Gang Water", gang_water_models, problem_water)
        gang_earth_info = consult_gang("Gang Earth", gang_earth_models, problem_earth)

        # Display outputs from each gang
        st.subheader("Gang Water Outputs")
        for name, advice in gang_water_info.items():
            st.write(f"**{name}**")
            st.text_area("", advice, height=150, key=name + "_water", help=f"Advice from {name}")

        st.subheader("Gang Earth Outputs")
        for name, advice in gang_earth_info.items():
            st.write(f"**{name}**")
            st.text_area("", advice, height=150, key=name + "_earth", help=f"Advice from {name}")

        # King's Verdict
        st.subheader("King's Verdict")
        king_answer = king_analysis(gang_water_info, gang_earth_info, problem_water, problem_earth)
        st.write(king_answer)
