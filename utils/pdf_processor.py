import os
import magic
from PyPDF2 import PdfReader
from io import BytesIO
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.storage import DocumentManager
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from config import COHERE_API_KEY, COHERE_EMBED_MODEL, MAX_FILE_SIZE_MB, DOCUMENTS_DIR
 
def init_sample_data():
    """Khởi tạo dữ liệu mẫu nếu chưa có document nào"""
    doc_manager = DocumentManager()
    if not doc_manager.get_all_documents():
        try:
            # Load file PDF mẫu từ thư mục data
            sample_pdf = os.path.join('data', 'documents', '1.pdf')
            if os.path.exists(sample_pdf):
                with open(sample_pdf, 'rb') as f:
                    file_content = f.read()
                
                # Tạo document mới
                doc_id = doc_manager.add_document(
                    file_name='1.pdf',
                    title='Tài liệu mẫu',
                    description='Tài liệu tuyển sinh mẫu',
                    file_size=len(file_content)
                )
                
                # Process PDF
                from io import BytesIO
                file_obj = BytesIO(file_content)
                file_obj.name = '1.pdf'
                process_pdf(file_obj, doc_id)
                
                st.success("Đã khởi tạo dữ liệu mẫu")
        except Exception as e:
            st.error(f"Lỗi khi khởi tạo dữ liệu mẫu: {str(e)}")

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
            model=COHERE_EMBED_MODEL
        )
        vectorstore = FAISS.from_texts(chunks, embeddings)
        
        # Lưu vectorstore
        doc_manager = DocumentManager()
        doc = doc_manager.get_document(doc_id)
        vectorstore.save_local(doc['vectorstore_path'])
        
        return True
        
    except Exception as e:
        raise Exception(f"Lỗi khi xử lý PDF: {str(e)}")
