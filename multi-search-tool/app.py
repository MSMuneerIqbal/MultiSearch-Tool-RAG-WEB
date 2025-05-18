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

# Load API keys
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")
api_key = st.secrets["GOOGLE_API_KEY"]

st.title("Chatbot with PDF and Web Search")

# Sidebar for user to choose between PDF Chat and Web Search
st.sidebar.title("Choose Functionality")
option = st.sidebar.radio("Select an option", ["Chat with PDF", "Search the Web"])

# Function to handle streaming response
def stream_response(response_text):
    """Generator function to stream response with proper formatting."""
    formatted_text = format_response(response_text)
    streamed_text = ""
    for char in formatted_text:
        streamed_text += char
        yield streamed_text
        time.sleep(0.01)

def format_response(response_text):
    """Format response to have each item on a new line, ensuring proper spacing."""
    items = response_text.split(" ")
    return "\n".join(items)

# PDF Chat functionality
if option == "Chat with PDF":
    # Sidebar for file upload
    st.sidebar.title("Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    # LLM Setup
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

            # Display chat history
            for chat in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.markdown(f"**You:** {chat['question']}")
                with st.chat_message("assistant"):
                    st.markdown(f"**Bot:** {chat['response']}")

            user_input = st.chat_input("Enter your question:", key="pdf_chat_input")

            if user_input:
                with st.chat_message("user"):
                    st.markdown(f"**You:** {user_input}")
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
        else:
            st.info("Please upload a PDF file to begin.")

# Web Search functionality
elif option == "Search the Web":
    tavily_key = st.secrets["TAVILY_API_KEY"]

    if not tavily_key:
        st.error("API key is missing. Please set the API key in the .env file.")

    tavily_client = TavilyClient(api_key=tavily_key)
    tavily_search = TavilySearchResults(max_results=3)

    st.title("Search the Web")

    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    query = st.chat_input("Enter your search query:", key="web_search_input")

    if query:
        with st.chat_message("user"):
            st.markdown(f"**You:** {query}")

        with st.spinner("Searching the web..."):
            try:
                search_docs = tavily_search.invoke(query)

                if search_docs:
                    st.session_state.search_history.append({"question": query, "response": search_docs})

                    with st.chat_message("assistant"):
                        for doc in search_docs:
                            url = doc.get('url', '#')
                            content = doc.get('content', 'No Content Available')
                            response_text = f"**Result:**\n\n**Link:** [Read More]({url})\n\n**Snippet:** {content}\n---"
                            response_placeholder = st.empty()
                            for streamed_text in stream_response(response_text):
                                response_placeholder.markdown(streamed_text)
                            time.sleep(0.5)
                else:
                    st.session_state.search_history.append({"question": query, "response": "No results found."})
                    with st.chat_message("assistant"):
                        st.markdown("**Bot:** No results found.")
            except Exception as e:
                st.session_state.search_history.append({"question": query, "response": f"Error: {e}"})
                with st.chat_message("assistant"):
                    st.markdown(f"**Bot:** Error occurred: {e}")

    for search in st.session_state.search_history:
        with st.chat_message("user"):
            st.markdown(f"**You:** {search['question']}")

        with st.chat_message("assistant"):
            if isinstance(search["response"], list):
                for doc in search["response"]:
                    url = doc.get('url', '#')
                    content = doc.get('content', 'No Content Available')
                    st.markdown(f"**Result:**\n\n**Link:** [Read More]({url})\n\n**Snippet:** {content}\n---")
            else:
                st.markdown(f"**Bot:** {search['response']}")
