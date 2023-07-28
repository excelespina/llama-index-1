import os, streamlit as st

# Uncomment to specify your OpenAI API key here (local testing only, not in production!), or add corresponding environment variable (recommended)
# os.environ['OPENAI_API_KEY']= ""

from llama_index import VectorStoreIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext, GPTVectorStoreIndex
from langchain.callbacks.base import BaseCallbackHandler
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI

from llama_index import download_loader
SimpleWebPageReader = download_loader("SimpleWebPageReader")

urls = ['https://www.itavabrooklyn.org/curriculum',
        'https://www.itavabrooklyn.org/directory/faculty',
        'https://www.itavabrooklyn.org/admissions',
        'https://www.itavabrooklyn.org/about_us',
]

RWP_loader = SimpleWebPageReader()
net_docs = RWP_loader.load_data(urls=urls)

import requests
from bs4 import BeautifulSoup 

for i in urls:
    doc_name = f'data/{i.split("/")[-1]}.txt'
    if os.path.isfile(doc_name):
        continue
    
    soup = BeautifulSoup(requests.get(i).text, features="html.parser") 
    text = soup.get_text() 
    with open(doc_name, 'w') as f:
        f.write(text)

# Define a simple Streamlit app
st.title("Ask ITAVA Bot")
query = st.text_input("What would you like to ask?", "")

hide_st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# If the 'Submit' button is clicked
if st.button("Submit") or query:
    res_box = st.empty()
    if not query.strip():
        st.error(f"Please provide the search query.")
    else:
        try:
            resp = ""
            # This example uses text-davinci-003 by default; feel free to change if desired
            llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", streaming=True))
            # llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-4", streaming=True))

            # Configure prompt parameters and initialise helper
            max_input_size = 4096
            num_output = 256
            max_chunk_overlap = 20

            prompt_helper = PromptHelper(max_input_size, num_output)

            # Load documents from the 'data' directory
            documents = SimpleDirectoryReader('data').load_data()
            service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
            index = VectorStoreIndex.from_documents(documents, service_context=service_context)
            
            response = index.as_query_engine(streaming=True, similarity_top_k=1).query(query)
            # for i in range(len(response)):
            #     res_box.write(str(response[i]))
            for token in response.response_gen:
                resp += token
                res_box.markdown(resp, unsafe_allow_html=True)


            # res_box.write (str(response))
            #st.success(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
