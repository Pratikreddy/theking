import os
import streamlit as st
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize clients
openai_client = OpenAI(api_key=openai_api_key)
groq_client = Groq(api_key=groq_api_key)

# Available models for king and peasants
gpt_models = ["gpt-4-turbo", "gpt-4-0125-preview", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-instruct"]
groq_models = ["llama3-8b-8192", "gemma-7b-it", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Streamlit UI Elements
st.title("AI Model Management")
king_model = st.selectbox("Select King Model", gpt_models + groq_models)
num_peasants = st.slider("Number of Peasants", min_value=1, max_value=4)
peasant_models = [st.selectbox(f"Select Peasant Model {i+1}", gpt_models + groq_models) for i in range(num_peasants)]
openai_key = st.text_input("Enter OpenAI API Key", type="password")
groq_key = st.text_input("Enter Groq API Key", type="password")
problem_statement = st.text_area("Problem Statement")

# Ensure API keys are set
if openai_key:
    openai_client.api_key = openai_key
if groq_key:
    groq_client.api_key = groq_key

# Define API function
def openai_call(model, messages, is_king=False):
    if is_king:
        system_message = """You are a wise and knowledgeable coder and problem solver king who provides thoughtful answers to questions.

        You have 10 advisors, who offer their insights to assist you.

        Consider their perspectives and advice, but ultimately provide your own well-reasoned response to the problem based on all context and advice. If you find their input helpful, feel free to acknowledge their contributions in your answer."""
    else:
        system_message = "You are a wise and knowledgeable coder and problem solver expert"

    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": messages}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()

# Define Groq function
def groq_call(model, messages):
    response = groq_client.chat.completions.create(
        model=model,
        messages=[
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
            answers[f"Peasant {i+1} ({model})"] = openai_call(model, user_message, is_king=False)
        else:
            answers[f"Peasant {i+1} ({model})"] = groq_call(model, user_message)
        progress_bar.update()

    peasant_answers = "\n\n".join(f"{name}: {advice}" for name, advice in answers.items())
    king_prompt = f"Peasants Advice:\n{peasant_answers}\n\nProblem: {user_message}"

    progress_bar.set_description("The King is solving the problem")
    if king_model in gpt_models:
        king_answer = openai_call(king_model, king_prompt, is_king=True)
    else:
        king_answer = groq_call(king_model, king_prompt)

    progress_bar.update()
    progress_bar.close()
    return king_answer

# Process the solution
if st.button("Solve Problem"):
    if not problem_statement:
        st.warning("Please enter a problem statement")
    else:
        final_solution = the_king(king_model, peasant_models, problem_statement)
        st.write("**Solution:**")
        st.write(final_solution)
