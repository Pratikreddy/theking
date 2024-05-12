import streamlit as st
from openai import OpenAI
from groq import Groq
from tqdm import tqdm

# Set custom page configuration
st.set_page_config(page_title="KING P", page_icon="👑", layout="wide", initial_sidebar_state="expanded")

# Available models
gpt_models = ["gpt-4-turbo", "gpt-4-0125-preview", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-instruct"]
groq_models = ["llama3-8b-8192", "gemma-7b-it", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Page title
st.title("The Kingdom")
st.write("**A collaborative problem-solving system with a wise King and knowledgeable Peasants.**")

#sidebar
st.sidebar.title("        DAD")
st.sidebar.write("    **PRATIK REDDY**")
st.sidebar.write("github.com/Pratikreddy")





# API Key Inputs (side by side)
col1, col2 = st.columns(2)
with col1:
    openai_api_key = st.text_input("OpenAI Key", type="password", help="Provide your OpenAI API Key")
with col2:
    groq_api_key = st.text_input("Groq Key", type="password", help="Provide your Groq API Key")

# Model Selection
st.subheader("Model Selection")
king_model = st.selectbox("Pick your **KING**", gpt_models + groq_models, help="Select the primary (King) model")
peasant_models = st.multiselect("Pick your **Peasants**", gpt_models + groq_models, help="Select models that will advise the King")

# Problem Statement
st.subheader("Problem Statement")
problem_statement = st.text_area("Describe your problem or question", help="Provide a detailed problem statement for the King and Peasants to solve")

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

# Function to consult the King
def the_king(king_model, peasant_models, user_message):
    answers = {}
    tasks = [f"Consulting Peasant {i+1}" for i in range(len(peasant_models))]

    for i, model in enumerate(peasant_models):
        st.write("The KING has summoned the pesants")
        st.write(f"Peasant {i+1} is {model}...")
        if model in gpt_models:
            answers[f"Peasant {i+1} ({model})"] = openai_call(user_message, model, "You are a coder and problem solver expert", openai_api_key)
        else:
            answers[f"Peasant {i+1} ({model})"] = groq_call(user_message, model, groq_api_key)

    peasant_answers = "\n\n".join(f"{name}: {advice}" for name, advice in answers.items())
    king_prompt = f"Peasants Advice:\n{peasant_answers}\n\nProblem: {user_message}"

    st.write("All Peasants have submitted their due dilligence to the King.")
    st.write("The King is analyzing the problem...")

    if king_model in gpt_models:
        king_answer = openai_call(king_prompt, king_model, "You are a wise and knowledgeable coder and problem solver king who provides thoughtful answers to questions.", openai_api_key)
    else:
        king_answer = groq_call(king_prompt, king_model, groq_api_key)

    return answers, king_answer

# Process the solution
#st.subheader("Solve the Problem")
if st.button("Consult the King"):
    if not problem_statement:
        st.warning("Please enter a problem statement.")
    elif not (openai_api_key and groq_api_key):
        st.error("Please enter valid OpenAI and Groq API keys.")
    elif not king_model:
        st.error("Please select a King Model.")
    elif not peasant_models:
        st.error("Please select at least one Peasant Model.")
    else:
        #st.info("The King has summoned the Peasants")
        peasant_outputs, final_solution = the_king(king_model, peasant_models, problem_statement)

        # Display each Peasant's output
        st.subheader("Peasant Outputs")
        for name, advice in peasant_outputs.items():
            st.write(f"**{name}**")
            st.text_area("", advice, height=150, key=name, help=f"Advice from {name}")

        # Display King's Verdict
        st.subheader("King's Verdict")
        st.write(final_solution)
