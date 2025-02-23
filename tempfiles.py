import tempfile
import os

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