import streamlit as st
import cohere
from datetime import datetime
from utils.auth import check_password, logout
from utils.storage import DocumentManager, load_vectorstore
from utils.pdf_processor import process_pdf
from config import COHERE_API_KEY, COHERE_MODEL, SCHOOL_CONTACT_INFO

# Initialize Cohere client
co = cohere.Client(api_key=COHERE_API_KEY)

class ChatPDFApp:
    def __init__(self):
        self.doc_manager = DocumentManager()
        self.setup_page()
    
    def setup_page(self):
        """Configure page settings"""
        st.set_page_config(
            page_title="ChatPDF Bot",
            page_icon="🤖",
            layout="wide"
        )
        
        # Thêm menu Settings vào sidebar
        with st.sidebar:
            if st.button("⚙️ Thiết lập"):
                st.session_state.show_settings = True
            if st.button("💬 Chat"):
                st.session_state.show_settings = False
                
            if hasattr(st.session_state, 'is_authenticated') and st.session_state.is_authenticated:
                if st.button("Đăng xuất"):
                    logout()

    def handle_file_upload(self, uploaded_file, title, description):
        """Process file upload with error handling"""
        try:
            with st.spinner("Đang xử lý file PDF..."):
                doc_id = self.doc_manager.add_document(
                    uploaded_file.name,
                    title,
                    description,
                    uploaded_file.size
                )
                
                if process_pdf(uploaded_file, doc_id):
                    st.success("Upload và xử lý PDF thành công!")
                    return True
                    
        except Exception as e:
            st.error(f"Lỗi khi xử lý file: {str(e)}")
            return False

    def get_chat_response(self, prompt, context):
        """Generate chat response using Cohere"""
        system_prompt = f"""Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu. 
        Hãy trả lời câu hỏi dựa vào ngữ cảnh được cung cấp.
        Nếu không tìm thấy thông tin trong ngữ cảnh, hãy hướng dẫn người dùng liên hệ:
        {SCHOOL_CONTACT_INFO}
        
        Ngữ cảnh: {context}"""
        
        return co.chat(
            message=prompt,
            temperature=0.5,
            model=COHERE_MODEL,
            preamble=system_prompt,
        )

    def settings_page(self):
        """Render settings page with admin functions"""
        st.title("Thiết lập - Quản lý tài liệu PDF")
        
        if not check_password():
            return
            
        tab1, tab2 = st.tabs(["Upload Tài Liệu", "Quản Lý Tài Liệu"])
        
        with tab1:
            with st.form("upload_form"):
                uploaded_file = st.file_uploader("Chọn file PDF", type="pdf")
                title = st.text_input("Tiêu đề tài liệu:")
                description = st.text_area("Mô tả tài liệu:")
                
                if st.form_submit_button("Upload"):
                    if not (uploaded_file and title):
                        st.warning("Vui lòng điền đầy đủ thông tin!")
                        return
                        
                    self.handle_file_upload(uploaded_file, title, description)
            
        with tab2:
            st.subheader("Danh sách tài liệu")
            docs = self.doc_manager.get_all_documents()
            
            for doc_id, doc in docs.items():
                with st.expander(f"📄 {doc['title']}"):
                    st.write(f"**Mô tả:** {doc['description']}")
                    st.write(f"**File gốc:** {doc['file_name']}")
                    st.write(f"**Kích thước:** {doc['file_size'] / 1024:.1f} KB")
                    st.write(f"**Ngày upload:** {datetime.fromisoformat(doc['upload_date']).strftime('%d/%m/%Y %H:%M')}")
                    
                    if st.button(f"🗑️ Xóa tài liệu", key=f"del_{doc_id}"):
                        if self.doc_manager.delete_document(doc_id):
                            st.success("Đã xóa tài liệu!")
                            st.rerun()
                        else:
                            st.error("Không thể xóa tài liệu!")

    def chat_page(self):
        """Render simplified chat interface"""
        st.title("Tư vấn tuyển sinh - COFER Bot 🤖")
        
        docs = self.doc_manager.get_all_documents()
        if not docs:
            st.info("Chưa có tài liệu nào được upload. Vui lòng liên hệ admin.")
            return
            
        # Get the first document (most recently uploaded)
        latest_doc_id = list(docs.keys())[0]
            
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Handle new messages
        if prompt := st.chat_input("Nhập câu hỏi của bạn"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            vectorstore = load_vectorstore(latest_doc_id)
            if not vectorstore:
                st.error("Không thể tải dữ liệu tài liệu!")
                return
                
            # Find relevant passages
            docs = vectorstore.similarity_search(prompt, k=3)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Generate and display response
            response = self.get_chat_response(prompt, context)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"):
                st.markdown(response.text)

    def main(self):
        """Main application logic"""
        # Initialize show_settings in session state if not present
        if 'show_settings' not in st.session_state:
            st.session_state.show_settings = False
            
        # Show either settings or chat page based on session state
        if st.session_state.show_settings:
            self.settings_page()
        else:
            self.chat_page()

def main():
    app = ChatPDFApp()
    app.main()

if __name__ == "__main__":
    main()