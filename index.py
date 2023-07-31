import os, streamlit as st

# Uncomment to specify your OpenAI API key here (local testing only, not in production!), or add corresponding environment variable (recommended)
# os.environ['OPENAI_API_KEY']= ""

import html, random
from engine.loaders import update_db_urls, gpt_engine

main_questions = ['Who are you?', "What can you offer my child?"]
rand_questions = []
# rand_questions = [
#     "What is the average class size at your high school?",
#     "Could you explain the curriculum to me in more detail? How flexible is it to cater to a student's individual strengths, weaknesses, and interests?",
#     "What extracurricular activities and clubs are offered at your school?",
#     "How does the school handle advanced students? Is there a gifted program or opportunities for advanced placement (AP) classes?",
#     "How well does the school prepare students for college admissions? What percentage of students get accepted into college, and what kinds of colleges do they typically attend?",
#     "How does your school handle students who need additional academic support?",
#     "How is technology incorporated into the classroom and curriculum? Does the school provide devices to the students?",
#     "How diverse is the school in terms of both the student body and the faculty?",
#     "How is student safety ensured? What security measures are in place?",
#     "What is your school's philosophy on homework and testing?",
#     "How is the school's relationship with the surrounding community? Are there opportunities for community service or involvement?",
#     "How does the school address student mental health and well-being?",
#     "How does the school handle incidents of bullying or harassment?",
#     "How are parents involved in the school? Is there a parent-teacher association?",
#     "Does the school offer any internship or work experience programs?",
#     "What are the physical facilities like? Are there modern science labs, a library, sports facilities, and arts spaces?",
#     "Does the school provide guidance counseling services? How do they assist students in making future education or career decisions?",
#     "How does the school handle discipline? What is the policy on detentions, suspensions, etc.?",
#     "How qualified and experienced are the teachers? What professional development opportunities do teachers have?",
#     "What are the graduation rates at your high school?"
# ]

# curr_domain = "http://localhost:8501"
curr_domain = "https://itava.xl-exp.net"

urls = []
import validators
with open('output.txt') as f:
    for i in list(f.read().split("\n")):
        if validators.url(i):
            urls.append(i)

with open('recommended_questions.txt') as f:
    for i in list(f.read().split("\n")):
        rand_questions.append(i)
    
# Define a simple Streamlit app
st.title("Ask ITAVA Bot")
default_query = st.experimental_get_query_params().get("query", [""])[0]

with st.container():
    st.markdown("""
        <style>
        .low-title {
            opacity: 0.7;
        }
        .button_custom_main {
            background-color: #04AA6D;
            border-radius: 12px;
            color: white;
            margin: 0 auto;
            display: inline;
        }
        .button_custom_opts {
            border-radius: 12px;
            margin: 0 auto;
            display: inline;
        }
        .action_btn {
            margin: 0 auto;
            display: inline;
            margin-right: 5px; 
        }
        .buttons {
            margin: 0 auto;
            display: flex;}
        </style>
        """, unsafe_allow_html=True)

    md_builder = """<div class="row buttons">\n"""
    with st.expander("Get Some Ideas Here"):
        st.text("Get Started")
        for text, col in zip(main_questions, st.columns(len(main_questions))):
            md_builder += f'''
                \n<a href="{curr_domain}?query={html.escape(text)}" target="_self"><button class="button_custom_main action_btn">{text}</button></a>\n
                '''
        md_builder += """\n</div>"""
        st.markdown(md_builder, unsafe_allow_html=True)
        md_builder = ""
        st.divider()

        st.text("Suggested:")
        rand_qs = rand_questions.copy()
        random.shuffle(rand_qs)
        rand_qs = rand_qs[:3]

        md_builder += """<div class="row buttons">\n"""
        for text, col in zip(rand_qs, st.columns(len(rand_qs))):
            md_builder += f'''
                \n<a href="{curr_domain}?query={html.escape(text)}" target="_self"><button class="button_custom_opts action_btn">"{text}"</button></a>\n
                '''
        md_builder += """\n</div>"""
        st.markdown(md_builder, unsafe_allow_html=True)

query = st.text_input("What would you like to know?", default_query)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# If the 'Submit' button is clicked
# if st.button("Submit", disabled=st.session_state.submit_button_state, on_click=submit_button_status(True)) or query:
if st.button("Submit") or query:
    res_box = st.empty()
    if not query.strip():
        st.error(f"Please provide the search query.")
    else:
        try:
            resp = ""
            index = gpt_engine()
            
            response = index.as_query_engine(streaming=True, similarity_top_k=1).query(query)
            # for i in range(len(response)):
            #     res_box.write(str(response[i]))
            for token in response.response_gen:
                resp += token
                res_box.markdown(resp, unsafe_allow_html=True)

            st.markdown("""
                <style>
                .element-opt{
                    -webkit-animation: 1s ease 0s normal forwards 1 fadein;
                    animation: 1s ease 0s normal forwards 1 fadein;
                }

                @keyframes fadein{
                    0% { opacity:0; }
                    66% { opacity:0; }
                    100% { opacity:1; }
                }

                @-webkit-keyframes fadein{
                    0% { opacity:0; }
                    66% { opacity:0; }
                    100% { opacity:1; }
                }
                </style>
                """, unsafe_allow_html=True)

            md_builder = """<p class="element-opt">Consider more:</p>"""
            st.divider()
            
            rand_qs = rand_questions.copy()
            random.shuffle(rand_qs)
            rand_qs = rand_qs[:3]

            md_builder += """<div class="row buttons element-opt">\n"""
            for text, col in zip(rand_qs, st.columns(len(rand_qs))):
                md_builder += f'''
                    \n<a href="{curr_domain}?query={html.escape(text)}" target="_self"><button class="button_custom_opts action_btn">"{text}"</button></a>\n
                    '''
            md_builder += """\n</div>"""
            st.markdown(md_builder, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    update_db_urls(urls)
