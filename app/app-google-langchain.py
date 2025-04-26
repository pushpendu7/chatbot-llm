import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title = "ChatBot (Google Gemini)", page_icon = ":robot:", layout = "wide", initial_sidebar_state = "expanded")
st.header("Chatbot :grey[(Google Gemini)]", divider = "red")

def reset_session():
    st.session_state.clear()
    # st.rerun()

message_container = st.container(height = 400, border=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = os.urandom(16).hex()

if "messages" not in st.session_state:
    # st.session_state.messages = [{"role": "assistant", "content": "Hi there! How may I help you today?"}]
    st.session_state.messages = [{"role": "assistant", "parts": ["Hi there! How may I help you today?"]}]

models = {
    "Gemini 1.5 Flash" : "gemini-1.5-flash",
    "Gemini 1.5 Pro" : "gemini-1.5-pro",
}

with st.sidebar:
    selected_model = st.selectbox("Select a model", options = models.keys(), index=0, key="model")

    streaming = st.toggle(label="Streaming output", key="streaming", value=True, help = "Enable streaming output for the assistant's response.")
    history_flag = st.toggle(label="Chat History", key="history", value = True, help = "Enable chat history or memory for the assistant's response.")

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
            # st.write(st.session_state.messages)
            st.markdown(message["parts"][0])

col1, col2 = st.columns([0.85, 0.15])

if user_prompt := col1.chat_input(f"Ask {selected_model}..."):
    # user_input = {"role": "user", "content": user_prompt}
    user_input = {"role": "user", "parts": [user_prompt]}
    st.session_state.messages.append(user_input)
    
    with message_container:
        with st.chat_message("user"):
            st.markdown(user_prompt)
        
        # chat_session = genai.ChatSession(model = model, history = st.session_state.messages)
        chat_session = model.start_chat(history = st.session_state.messages)

        with st.chat_message("assistant"):
            with st.spinner("Typing..."):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    if history_flag:
                        for response in chat_session.send_message(user_prompt, stream = streaming):
                            full_response += response.text
                            message_placeholder.markdown(full_response + "▌")
                    else:
                        for response in model.generate_content(user_prompt, stream = streaming):
                            full_response += response.text
                            message_placeholder.markdown(full_response + "▌")
                except Exception as e:
                    full_response = f":red[Error: {e}]"

            message_placeholder.markdown(full_response)
            # st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.messages.append({"role": "assistant", "parts": [full_response]})

col2.button("Start New Session", on_click = lambda: reset_session(), type="secondary", help = "Start a new session with a new session ID.")
