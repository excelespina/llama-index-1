import streamlit as st

@st.cache_data
def update_db_urls(urls):
    # 
    import requests, os
    from bs4 import BeautifulSoup 

    for i in urls:
        doc_name = f'data/{i.split("/")[-1]}.txt'
        if os.path.isfile(doc_name):
            continue
        
        soup = BeautifulSoup(requests.get(i).text, features="html.parser") 
        text = soup.get_text() 
        with open(doc_name, 'w') as f:
            f.write(text)

    st.success("Refreshed Knowledge Base!")

@st.cache_resource
def gpt_engine(model_name="gpt-3.5-turbo"):
    from llama_index import VectorStoreIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext, GPTVectorStoreIndex
    from langchain.chat_models import ChatOpenAI

    # This example uses text-davinci-003 by default; feel free to change if desired
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name=model_name, streaming=True))
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
    return index