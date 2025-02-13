# Multi-Search Tool

## Overview

The **Multi-Search Tool** is an integrated Streamlit-based application that allows users to interact with two different functionalities:

1. **Chatbot with PDF Document**: This functionality allows users to upload PDF files, and the content of the PDF is indexed and stored. Users can then ask questions based on the document, and the chatbot will provide answers directly from the content of the document using the Google Generative AI model.

2. **Web Search**: This functionality enables users to perform a web search using the Tavily API. It returns relevant results from the web, allowing users to access information beyond the document.

## Features

- **Chatbot with PDF Document**: 
  - Upload a PDF file and extract text content.
  - Interact with the PDF document by asking questions.
  - Get answers based on document content powered by Google Generative AI.
  
- **Web Search**: 
  - Enter a search query to retrieve search results from the web.
  - Fetch the top 3 results from the web using the Tavily API.
  - Display the results in a clean, organized format with links to the original sources.

## Installation

### Prerequisites

Before you begin, make sure you have the following installed:
- Python 3.7 or later
- Streamlit
- Langchain
- Tavily API credentials
- Google Cloud API credentials

## UI and Features

The user interface is designed using Streamlit and is organized into the following sections:

### Sidebar
- **Upload PDF**: Users can upload a PDF file for the chatbot to process.
- **Status Updates**: A success message will be shown once the PDF is uploaded successfully.

### Main Section
- **Chat History**: Displays the interaction history with the chatbot.
- **User Input Box**: The input box at the bottom of the page allows users to ask questions based on the PDF content.
- **Web Search Input Box**: Below the chat box, there is another input box for users to perform a web search.

### Chatbot UI
- **User Interaction**: When a user enters a query, it appears in the chat window with the assistant's response below it. The conversation history is preserved, creating a seamless chat experience.

### Web Search UI
- **Search Results**: After the user submits a query, the search results are shown above the input box, including URLs and a brief snippet from each result.

## Troubleshooting

- **Error: API key not found**: Ensure that you have set the correct `GOOGLE_API_KEY` and `TAVILY_API_KEY` in your `.env` file.
- **Error: File not found or uploaded**: Make sure the PDF file is successfully uploaded and the content is being loaded properly.
- **StreamlitDuplicateElementId**: If you encounter an error with duplicate input fields, ensure each input box has a unique key argument (e.g., `st.chat_input("Enter your question:", key="chat_query")`).

## Contributing

We welcome contributions! If you'd like to contribute to this project, follow these steps:

1. Fork the repository
2. Clone your fork locally
3. Create a new branch (`git checkout -b feature-branch`)
4. Make your changes and commit them
5. Push your changes (`git push origin feature-branch`)
6. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- **Google Generative AI** for the AI-powered document question-answering.
- **Tavily API** for providing the web search capabilities.
- **Streamlit** for the easy-to-use app framework.
- **Langchain** for document processing and vector store management.




### Enhancements:
1. **Expanded Overview**: The description has been expanded to better explain the two primary features of the app—PDF interaction and web search.
2. **Installation & Setup**: Provides better instructions for setting up the `.env` file with necessary API keys and steps to run the app.
3. **UI and Features**: Added details about the chat interface and the web search UI.
4. **Troubleshooting**: Includes more specific common issues that might arise, including handling API key errors and Streamlit element conflicts.
5. **Contributing**: Added guidelines for contributing to the project, including a section on forking and submitting pull requests.

Let me know if you need any more modifications!

