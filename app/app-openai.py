import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

st.set_page_config(page_title = "ChatBot (OpenAI)", page_icon = ":robot:", layout = "wide", initial_sidebar_state = "expanded")
st.header("Chatbot :grey[(OpenAI)]", divider = "red")

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
    "GPT 3.5 Turbo" : "gpt-3.5-turbo",
}


with st.sidebar:
    selected_model = st.selectbox("Select a model", options = models.keys(), index=0, key="model")

    st.markdown("## Session ID")
    st.markdown(f":grey[{st.session_state.session_id}]")
    st.markdown("## Instructions")
    st.markdown(":grey[This is a simple chatbot application using OpenAI GPT Model. You can ask questions and get responses from the model.]")
    st.markdown("## About")
    st.markdown(":grey[This app is built using Streamlit and OpenAI API.]")


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
                    for response in openai.completions.create(model = models[selected_model], prompt = st.session_state.messages, stream = True):
                        full_response += response.choices[0].delta.get("content", "")
                        message_placeholder.markdown(full_response + "▌")
                except Exception as e:
                    full_response = f":red[Error: {e}]"
                    
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
col2.button("Start New Session", on_click = lambda: reset_session(), type="secondary", help = "Start a new session with a new session ID.")
