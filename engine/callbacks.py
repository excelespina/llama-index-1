import streamlit as st
import base64, json

def decode_jwt_payload(jwt_token):
    # JWT tokens have 3 parts separated by '.'. We want the second part (payload).
    payload = jwt_token.split('.')[1]
    
    # Base64Url decode
    padding = '=' * (4 - (len(payload) % 4))
    decoded_payload = base64.urlsafe_b64decode(payload + padding)
    
    return json.loads(decoded_payload)

def main_question_callback_1():
    st.session_state['input_value'] = st.session_state['main_questions_option_1']

def main_question_callback_2():
    st.session_state['input_value'] = st.session_state['main_questions_option_2']

def suggested_callback_1():
    st.session_state['input_value'] = st.session_state['suggested_option_1']

def suggested_callback_2():
    st.session_state['input_value'] = st.session_state['suggested_option_2']

def suggested_callback_3():
    st.session_state['input_value'] = st.session_state['suggested_option_3']

def consider_more_callback_1():
    st.session_state['input_value'] = st.session_state['consider_suggested_option_1']

def consider_more_callback_2():
    st.session_state['input_value'] = st.session_state['consider_suggested_option_2']

def consider_more_callback_3():
    st.session_state['input_value'] = st.session_state['consider_suggested_option_3']
    
