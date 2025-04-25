import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title = "ChatBot (Google Gemini)", page_icon = ":robot:", layout = "wide", initial_sidebar_state = "expanded")

st.header("Chatbot :grey[(Google Gemini)]", divider = "red")

streaming = st.toggle(label="Streaming output", key="streaming", value=True, help="Enable streaming output for the assistant's response.")

def reset_session():
    st.session_state.clear()
    # st.rerun()

message_container = st.container(height = 400, border=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = os.urandom(16).hex()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there! How may I help you today?"}]

models = {
    "Gemini 1.5 Flash" : "gemini-1.5-flash",
    "Gemini 1.5 Pro" : "gemini-1.5-pro",
}

with st.sidebar:
    selected_model = st.selectbox("Select a model", options = models.keys(), index=0, key="model")

    st.markdown("## Session ID")
    st.markdown(f":grey[{st.session_state.session_id}]")
    st.markdown("## Instructions")
    st.markdown(":grey[This is a simple chatbot application using Google Gemini. You can ask questions and get responses from the model.]")
    st.markdown("## About")
    st.markdown(":grey[This app is built using Streamlit and Google Gemini API.]")

model = genai.GenerativeModel(model_name = models[selected_model])

for message in st.session_state.messages:
    with message_container:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

col1, col2 = st.columns([0.85, 0.15])

if user_prompt := col1.chat_input(f"Ask {selected_model}..."):
    user_input = {"role": "user", "content": user_prompt}
    st.session_state.messages.append(user_input)
    
    with message_container:
        with st.chat_message("user"):
            st.markdown(user_prompt)
        
        
        with st.chat_message("assistant"):
            with st.spinner("Typing..."):
                message_placeholder = st.empty()
                full_response = ""

                try:
                    for response in model.generate_content(user_prompt, stream = streaming):
                        full_response += response.text
                        message_placeholder.markdown(full_response + "▌")
                except Exception as e:
                    full_response = f":red[Error: {e}]"

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

col2.button("Start New Session", on_click = lambda: reset_session(), type="secondary", help = "Start a new session with a new session ID.")
