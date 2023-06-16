import os, streamlit as st

# Uncomment to specify your OpenAI API key here (local testing only, not in production!), or add corresponding environment variable (recommended)
# os.environ['OPENAI_API_KEY']= ""

from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext
from langchain.callbacks.base import BaseCallbackHandler
from langchain.llms.openai import OpenAI

# Define a simple Streamlit app
st.title("Ask XL EXP LLC")
query = st.text_input("What would you like to ask? (source: data/paul_graham_essay.txt)", "")

hide_st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


# If the 'Submit' button is clicked
if st.button("Submit"):
    res_box = st.empty()
    if not query.strip():
        st.error(f"Please provide the search query.")
    else:
        try:
            # This example uses text-davinci-003 by default; feel free to change if desired
            llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo", streaming=True))

            # Configure prompt parameters and initialise helper
            max_input_size = 4096
            num_output = 256
            max_chunk_overlap = 20

            prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

            # Load documents from the 'data' directory
            documents = SimpleDirectoryReader('data').load_data()
            service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
            index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
            
            response = index.query(query)
            for i in range(len(response)):
                res_box.write(str(response[i]))
            #res_box.write (str(response))
            #st.success(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
