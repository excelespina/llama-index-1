import openai, os, base64, json
import streamlit as st
import time, os, streamlit as st
import st_oauth
from engine.callbacks import *

# Uncomment to specify your OpenAI API key here (local testing only, not in production!), or add corresponding environment variable (recommended)
# os.environ['OPENAI_API_KEY']= ""

st.set_page_config(
        page_title="Ask ITAVA Bot",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

header = st.container()
header.title("Ask ITAVA Bot")
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

### Custom CSS for the sticky header
st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: sticky;
        top: 2rem;
        z-index: 999;
    }
    .fixed-header {
        border-bottom: 1px solid black;
    }
</style>
    """,
    unsafe_allow_html=True
)

import html, random
from engine.loaders import update_db_urls, gpt_engine, nav_to


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.input_value = ""
    st.session_state.not_answering = False
    st.session_state.responding = False
    st.session_state.logged_in = False

if 'ST_OAUTH' not in st.session_state:
    try:
        redirect_uri = st.secrets['oauth']['redirect_uri']
        st_oauth.st_oauth("oauth", 'Login via Google to continue')
    except Exception as e:
        print(e)
        Secrets_OAuth = {
            "authorization_endpoint": os.environ['authorization_endpoint'],
            "token_endpoint": os.environ['token_endpoint'],
            "jwks_uri": os.environ['jwks_uri'],
            "redirect_uri": os.environ['redirect_uri'],
            "client_id": os.environ['client_id'],
            "client_secret": os.environ['client_secret'],
            "scope": os.environ['scope'],
            "audience": os.environ['audience']
        }
        redirect_uri = Secrets_OAuth['redirect_url']
        st_oauth.st_oauth(Secrets_OAuth, 'Login via Google to continue')

        print("No secrets found")

    
else:
    st.session_state.logged_in = True

payload = decode_jwt_payload(st.session_state['ST_OAUTH']['id_token'])
email = payload['email']

## Limiting access to only certain emails
if email.split("@")[-1] != 'xl-exp.net':
    st.error('User not allowed. Check the email you signed in.', icon="🚨")
    st.error('Redirecting in 3 seconds...', icon="⚠")
    time.sleep(3)
    nav_to(redirect_uri)
    exit()

main_questions = ['Who are you?', "What can you offer my child?"]
rand_questions = []

urls = []
import validators
with open('output.txt') as f:
    for i in list(f.read().split("\n")):
        if validators.url(i):
            urls.append(i)

with open('recommended_questions.txt') as f:
    for i in list(f.read().split("\n")):
        rand_questions.append(i)

openai.api_key = os.environ['OPENAI_API_KEY']

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.text_input("What would like to ask?", st.session_state.input_value)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # with st.chat_message("user"):
    #     st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        st.session_state.responding = True

        index = gpt_engine()
        for response in index.as_query_engine(streaming=True, similarity_top_k=1).query(prompt).response_gen:
            full_response += response
            message_placeholder.markdown(full_response + "▌")

        st.session_state.responding = False
        message_placeholder.markdown(full_response)

    st.divider()
    st.text("Consider other:")

    rand_qs = rand_questions.copy()
    random.shuffle(rand_qs)
    rand_qs = rand_qs[:3]

    count = 1
    for text, col in zip(rand_qs, st.columns(len(rand_qs))):
        st.session_state[f"consider_suggested_option_{count}"] = text
        st.button(text, key=f"consider_suggested__{count}", on_click=locals()[f'consider_more_callback_{count}'], disabled=st.session_state.not_answering)
        count += 1
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.divider()

with st.container():
    with st.expander("Get Some Ideas Here"):
        st.text("Get Started")
        count = 1
        for text, col in zip(main_questions, st.columns(len(main_questions))):
            st.session_state[f"main_questions_option_{count}"] = text
            st.button(text, on_click=locals()[f'main_question_callback_{count}'], disabled=st.session_state.responding)
            count += 1
        st.divider()

        st.text("Suggested:")
        rand_qs = rand_questions.copy()
        random.shuffle(rand_qs)
        rand_qs = rand_qs[:3]

        count = 1
        for text, col in zip(rand_qs, st.columns(len(rand_qs))):
            st.session_state[f"suggested_option_{count}"] = text
            st.button(text, on_click=locals()[f'suggested_callback_{count}'], disabled=st.session_state.not_answering)
            count += 1