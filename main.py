import streamlit as st
from openai import OpenAI
from groq import Groq
from tqdm import tqdm

# Available models
gpt_models = ["gpt-4-turbo", "gpt-4-0125-preview", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-instruct"]
groq_models = ["llama3-8b-8192", "gemma-7b-it", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Streamlit UI Elements
st.title("AI Model Management")
openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
groq_api_key = st.text_input("Enter Groq API Key", type="password")

# Selection of king model and peasants
king_model = st.selectbox("Select King Model", gpt_models + groq_models)
num_peasants = st.slider("Number of Peasants", min_value=1, max_value=4)
peasant_models = [st.selectbox(f"Select Peasant Model {i+1}", gpt_models + groq_models) for i in range(num_peasants)]

# Problem statement input
problem_statement = st.text_area("Problem Statement")

# Initialize clients with API keys
openai_client, groq_client = None, None
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)

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

# Function to consult the king
def the_king(king_model, peasant_models, user_message):
    answers = {}
    tasks = [f"Consulting Peasant {i+1}" for i in range(len(peasant_models))]
    progress_bar = tqdm(tasks, desc="Gathering insights", unit="task")

    for i, model in enumerate(peasant_models):
        progress_bar.set_description(f"Consulting Peasant {i+1}")
        if model in gpt_models:
            answers[f"Peasant {i+1} ({model})"] = openai_call(user_message, model, "You are a coder and problem solver expert", openai_api_key)
        else:
            answers[f"Peasant {i+1} ({model})"] = groq_call(user_message, model, groq_api_key)
        progress_bar.update()

    peasant_answers = "\n\n".join(f"{name}: {advice}" for name, advice in answers.items())
    king_prompt = f"Peasants Advice:\n{peasant_answers}\n\nProblem: {user_message}"

    progress_bar.set_description("The King is solving the problem")
    if king_model in gpt_models:
        king_answer = openai_call(king_prompt, king_model, "You are a wise and knowledgeable coder and problem solver king who provides thoughtful answers to questions.", openai_api_key)
    else:
        king_answer = groq_call(king_prompt, king_model, groq_api_key)

    progress_bar.update()
    progress_bar.close()
    return king_answer

# Process the solution
if st.button("Solve Problem"):
    if not problem_statement:
        st.warning("Please enter a problem statement")
    elif not (openai_api_key and groq_api_key):
        st.error("Please enter valid OpenAI and Groq API keys")
    else:
        final_solution = the_king(king_model, peasant_models, problem_statement)
        st.write("**Solution:**")
        st.write(final_solution)
