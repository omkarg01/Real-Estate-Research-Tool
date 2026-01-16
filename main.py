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
        with status_placeholder.container():
            for status in process_urls(urls):
                st.text(status)
        status_placeholder.success("URLs processed successfully!")

query = st.text_input("Question")
if query:
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
