import streamlit as st
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key is missing. Please add it to the `.env` file.")
    st.stop()

# Set up Streamlit app
st.title("Retrieval Augmented Generation (RAG) Application")
st.write("Upload documents and chat with them using a RAG model!")

# File uploader
uploaded_files = st.file_uploader("Upload your documents (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

# Load and split documents
def load_and_split_documents(uploaded_files):
    documents = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split(".")[-1]
        
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            if file_type == "pdf":
                loader = PyPDFLoader(tmp_file_path)
            elif file_type == "docx":
                loader = Docx2txtLoader(tmp_file_path)
            elif file_type == "txt":
                loader = TextLoader(tmp_file_path)
            else:
                st.error(f"Unsupported file type: {file_type}")
                continue

            documents.extend(loader.load())
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file_path)

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    return texts

if uploaded_files:
    texts = load_and_split_documents(uploaded_files)
    st.success(f"Loaded {len(texts)} document chunks.")

# Create embeddings and vector store
def create_vector_store(texts):
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_texts([doc.page_content for doc in texts], embeddings)
    return vector_store


if uploaded_files:
    vector_store = create_vector_store(texts)
    st.success("Vector store created successfully.")

# Set up RAG model
def setup_rag_model(vector_store):
    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))  # Use environment variable
    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    return qa_chain

if uploaded_files:
    qa_chain = setup_rag_model(vector_store)
    st.success("RAG model is ready!")

# Chat interface
if uploaded_files:
    st.subheader("Chat with your documents")
    user_query = st.text_input("Ask a question about the documents:")
    if user_query:
        response = qa_chain.run(user_query)
        st.write("**Response:**")
        st.write(response)