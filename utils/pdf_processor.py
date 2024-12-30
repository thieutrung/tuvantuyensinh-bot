import os
import magic
from PyPDF2 import PdfReader
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.storage import DocumentManager

#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS

from langchain_cohere import CohereEmbeddings
from config import MAX_FILE_SIZE_MB, DOCUMENTS_DIR
import streamlit as st

from config import COHERE_API_KEY
 
def validate_pdf(file):
    """Kiểm tra tính hợp lệ của file PDF"""
    # Kiểm tra kích thước
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Kích thước file vượt quá {MAX_FILE_SIZE_MB}MB")
    
    # Kiểm tra mime type
    file_content = file.read()
    file.seek(0)  # Reset file pointer
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content)
    
    if file_type != 'application/pdf':
        raise ValueError("File không phải là PDF hợp lệ")



def process_pdf(file, doc_id):
    """Xử lý file PDF và tạo vectorstore"""
    try:
        # Validate PDF
        validate_pdf(file)
        
        # Lưu file
        pdf_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(file.getvalue())
        
        # Đọc nội dung
        pdf_data = BytesIO(file.read())
        doc_reader = PdfReader(pdf_data)
        raw_text = "".join([
            page.extract_text() 
            for page in doc_reader.pages 
            if page.extract_text()
        ])
        
        if not raw_text.strip():
            raise ValueError("Không thể trích xuất nội dung từ PDF")
        
        # Chia nhỏ văn bản
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(raw_text)
        
        # Tạo embeddings và lưu vectorstore
        embeddings = CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY,
            model="multilingual-22-12"
        )
        vectorstore = FAISS.from_texts(chunks, embeddings)
        
        # Lưu vectorstore
        doc_manager = DocumentManager()
        doc = doc_manager.get_document(doc_id)
        vectorstore.save_local(doc['vectorstore_path'])
        
        return True
        
    except Exception as e:
        raise Exception(f"Lỗi khi xử lý PDF: {str(e)}")
