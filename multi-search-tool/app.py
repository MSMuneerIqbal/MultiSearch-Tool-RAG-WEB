import os
import tempfile
import time
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient

# API Keys
api_key = st.secrets["GOOGLE_API_KEY"]
tavily_key = st.secrets["TAVILY_API_KEY"]

st.title("Chatbot with PDF and Web Search")

# Sidebar to switch functionality
st.sidebar.title("Choose Functionality")
option = st.sidebar.radio("Select an option", ["Chat with PDF", "Search the Web"])

# Stream formatted response
def stream_response(response_text):
    streamed_text = ""
    for char in response_text:
        streamed_text += char
        yield streamed_text
        time.sleep(0.01)

# PDF Chat functionality
if option == "Chat with PDF":
    st.sidebar.title("Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    memory = ConversationBufferWindowMemory(k=5)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if uploaded_file is not None:
        st.sidebar.success("Uploaded successfully!")
        with st.spinner("Loading PDF..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
                loader = PyPDFLoader(temp_file_path)
                documents = loader.load()
                os.remove(temp_file_path)
            except Exception as e:
                st.error(f"Error loading PDF: {e}")
                loader = None

        if loader:
            with st.spinner("Creating Embedding..."):
                embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
                index_creator = VectorstoreIndexCreator(
                    embedding=embedding,
                    text_splitter=text_splitter
                )
                store = index_creator.from_documents(documents)

            st.title("Chat with your PDF")

            user_input = st.chat_input("Enter your question:", key="pdf_chat_input")

            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)
                with st.spinner("Generating response..."):
                    try:
                        response = store.query(user_input, llm=llm, memory=memory)
                        st.session_state.chat_history.append({"question": user_input, "response": response})
                        with st.chat_message("assistant"):
                            response_placeholder = st.empty()
                            for streamed_text in stream_response(response):
                                response_placeholder.markdown(streamed_text)
                    except Exception as e:
                        st.error(f"Error during query: {e}")

            # Optional: display chat history (disabled to prevent duplicates)
            # for chat in st.session_state.chat_history:
            #     with st.chat_message("user"):
            #         st.markdown(chat['question'])
            #     with st.chat_message("assistant"):
            #         st.markdown(chat['response'])

        else:
            st.info("Please upload a PDF file to begin.")

# Web Search functionality
elif option == "Search the Web":
    if not tavily_key:
        st.error("Tavily API key is missing.")

    tavily_client = TavilyClient(api_key=tavily_key)
    tavily_search = TavilySearchResults(max_results=3)

    st.title("Search the Web")

    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    query = st.chat_input("Enter your search query:", key="web_search_input")

    if query:
        with st.chat_message("user"):
            st.markdown(query)

        greetings = ["hi", "hello", "hey", "how are you", "what's up"]
        if query.strip().lower() in greetings:
            response_text = "Hello! 👋 How can I help you today with your search?"
            st.session_state.search_history.append({"question": query, "response": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

        else:
            with st.spinner("Searching the web..."):
                try:
                    results = tavily_search.invoke(query)

                    if results:
                        # Return only the first result's snippet and title
                        first_result = results[0]
                        title = first_result.get("title", "Result")
                        snippet = first_result.get("content", "")
                        url = first_result.get("url", "#")

                        response_text = f"**{title}**\n\n{snippet}\n\n[Read more]({url})"
                        st.session_state.search_history.append({"question": query, "response": response_text})

                        with st.chat_message("assistant"):
                            response_placeholder = st.empty()
                            for streamed_text in stream_response(response_text):
                                response_placeholder.markdown(streamed_text)

                    else:
                        response_text = "No results found."
                        st.session_state.search_history.append({"question": query, "response": response_text})
                        with st.chat_message("assistant"):
                            st.markdown(response_text)

                except Exception as e:
                    error_msg = f"Error: {e}"
                    st.session_state.search_history.append({"question": query, "response": error_msg})
                    with st.chat_message("assistant"):
                        st.markdown(error_msg)

    # Do NOT reprint full chat history to avoid duplicate UI
