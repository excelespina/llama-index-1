from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import streamlit as st

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text=initial_text
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # "/" is a marker to show difference 
        # you don't need it 
        self.text+=token+"/" 
        self.container.markdown(self.text) 

query=st.text_input("input your query",value="Tell me a joke")
ask_button=st.button("ask") 

st.markdown("### streaming box")
# here is the key, setup a empty container first
chat_box=st.empty() 
stream_handler = StreamHandler(chat_box)
chat = ChatOpenAI(max_tokens=25, streaming=True, callbacks=[stream_handler])

st.markdown("### together box")  

if query and ask_button: 
    response = chat([HumanMessage(content=query)])    
    llm_response = response.content  
    st.markdown(llm_response)
