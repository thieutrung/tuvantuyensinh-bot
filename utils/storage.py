import json
import os
import shutil
import streamlit as st
from datetime import datetime
from config import METADATA_FILE, DOCUMENTS_DIR, VECTORSTORE_DIR
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings

COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
COHERE_EMBED_MODEL = st.secrets["COHERE_EMBED_MODEL"]

def init_storage():
    """Khởi tạo storage với xử lý lỗi"""
    try:
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        os.makedirs(VECTORSTORE_DIR, exist_ok=True)
        
        if not os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)
                
    except Exception as e:
        st.error(f"Lỗi khởi tạo storage: {str(e)}")
        raise

class DocumentManager:

    def __init__(self):
        init_storage()  # Khởi tạo storage
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        """Load metadata từ file"""
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Lưu metadata xuống file"""
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def add_document(self, file_name, title, description, file_size):
        """Thêm document mới"""
        doc_id = str(len(self.metadata) + 1)
        self.metadata[doc_id] = {
            'file_name': file_name,
            'title': title,
            'description': description,
            'file_size': file_size,
            'upload_date': datetime.now().isoformat(),
            'vectorstore_path': os.path.join(VECTORSTORE_DIR, doc_id)
        }
        self._save_metadata()
        return doc_id
    
    def get_document(self, doc_id):
        """Lấy thông tin document"""
        return self.metadata.get(doc_id)
    
    def get_all_documents(self):
        """Lấy danh sách tất cả documents"""
        return self.metadata
    
    def delete_document(self, doc_id):
        """Xóa document"""
        if doc_id in self.metadata:
            # Xóa file và vectorstore
            doc_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}.pdf")
            vectorstore_path = self.metadata[doc_id]['vectorstore_path']
            
            if os.path.exists(doc_path):
                os.remove(doc_path)
            if os.path.exists(vectorstore_path):
                shutil.rmtree(vectorstore_path)
                
            # Xóa metadata
            del self.metadata[doc_id]
            self._save_metadata()
            return True
        return False

def load_vectorstore(doc_id):
    """Load vectorstore cho document cụ thể"""
    try:
        doc_manager = DocumentManager()
        doc = doc_manager.get_document(doc_id)
        if doc and os.path.exists(doc['vectorstore_path']):
            embeddings = CohereEmbeddings(
                cohere_api_key=COHERE_API_KEY,
                model=COHERE_EMBED_MODEL
            )
            return FAISS.load_local(
                doc['vectorstore_path'],
                embeddings,
                allow_dangerous_deserialization=True
            )
        return None
    except Exception as e:
        st.error(f"Lỗi khi load vectorstore: {str(e)}")
        return None
