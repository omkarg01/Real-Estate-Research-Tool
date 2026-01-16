import streamlit as st
from rag import process_urls, generate_answer

st.title("Real Estate Research Tool")

url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

status_placeholder = st.empty()

process_url_button = st.sidebar.button("Process URLs")
if process_url_button:
    urls = [url for url in (url1, url2, url3) if url != '']
    print("urls: ", urls)
    if len(urls) == 0:
        status_placeholder.error("You must provide at least one valid url")
    else:
        for status in process_urls(urls):
            status_placeholder.info(status)
        status_placeholder.success("URLs processed successfully!")


if 'query' not in st.session_state:
    st.session_state.query = ""

query = st.text_area("Question", value=st.session_state.query, height=100, placeholder="Enter your question here...")

if query != st.session_state.query:
    st.session_state.query = query

st.markdown("""
    <style>
    .stButton > button {
        width: 150px !important;
        background-color: #1f77b4 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
    }
    .stButton > button:hover {
        background-color: #1565a0 !important;
    }
    </style>
""", unsafe_allow_html=True)

ask_llm_button = st.button("Ask LLM 🤖", type="primary")

if ask_llm_button:
    if not query or not query.strip():
        status_placeholder.warning("Please enter a question first")
    else:
        try:
            with st.spinner("Generating answer... Please wait."):
                answer, sources = generate_answer(query)
            
            st.header("Answer:")
            st.write(answer)

            if sources:
                st.subheader("Sources:")
                for source in sources.split("\n"):
                    if source.strip(): 
                        st.write(source)
        except RuntimeError as e:
            status_placeholder.error("You must process urls first")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
