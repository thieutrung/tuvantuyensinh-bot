import streamlit as st
import cohere
from datetime import datetime
from utils.storage import DocumentManager, load_vectorstore
from utils.pdf_processor import process_pdf
from utils.auth import check_password, logout

COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
COHERE_MODEL = st.secrets["COHERE_MODEL"]
SCHOOL_CONTACT_INFO = st.secrets["SCHOOL_CONTACT_INFO"]

# Initialize Cohere client
co = cohere.Client(api_key=COHERE_API_KEY)

class ChatPDFApp:
    def __init__(self):
        self.doc_manager = DocumentManager()
        self.setup_page()
        if 'vectorstore_cache' not in st.session_state:
            st.session_state.vectorstore_cache = {}

    def setup_page(self):
        """Configure page settings"""
        st.set_page_config(
            page_title="Tu van tuyen sinh Bot",
            page_icon="🤖",
            layout="wide",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None
            }
        )

        # Load custom CSS from file
        with open('styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
        # Toggle button for settings
        if 'show_settings' not in st.session_state:
            st.session_state.show_settings = False
            
        col1, col2 = st.columns([0.95, 0.05])
        with col2:
            if st.button("⚙️" if not st.session_state.show_settings else "✖️", key="settings_toggle"):
                if st.session_state.show_settings:
                    # Log out when closing settings
                    st.session_state.admin_authenticated = False
                st.session_state.show_settings = not st.session_state.show_settings
                st.rerun()

    def handle_file_upload(self, uploaded_file, title, description):
        """Process file upload with error handling"""
        try:
            with st.spinner("Đang xử lý file tài liệu..."):
                doc_id = self.doc_manager.add_document(
                    uploaded_file.name,
                    title,
                    description,
                    uploaded_file.size
                )
                
                if process_pdf(uploaded_file, doc_id):
                    st.success("Upload và xử lý tài liệu thành công!")
                    return True
                    
        except Exception as e:
            st.error(f"Lỗi khi xử lý file: {str(e)}")
            return False

    def get_chat_response(self, prompt, context):
        """Generate chat response using Cohere"""
        system_prompt = f"""Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu với vai trò là chuyên viên tư vấn tuyển sinh. 
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
        st.markdown('<div class="settings-container">', unsafe_allow_html=True)
        st.title("Thiết lập - Quản lý tài liệu")
        
        authenticated = check_password()
        
        if not authenticated:
            st.markdown('</div>', unsafe_allow_html=True)
            return
            
        tab1, tab2 = st.tabs(["Upload Tài Liệu", "Quản Lý Tài Liệu"])
        
        with tab1:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("upload_form", clear_on_submit=True):
                    st.markdown("### Upload tài liệu mới")
                    uploaded_file = st.file_uploader("Chọn file PDF", type="pdf")
                    title = st.text_input("Tiêu đề tài liệu:")
                    description = st.text_area("Mô tả tài liệu:")
                    
                    st.write("")  # Add spacing
                    
                    if st.form_submit_button("Upload", use_container_width=True):
                        if not (uploaded_file and title):
                            st.warning("Vui lòng điền đầy đủ thông tin!")
                            return
                            
                        if self.handle_file_upload(uploaded_file, title, description):
                            st.session_state.show_settings = False
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with tab2:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.subheader("Danh sách tài liệu")
            docs = self.doc_manager.get_all_documents()
            
            st.markdown('<div class="document-list-container">', unsafe_allow_html=True)
            for doc_id, doc in docs.items():
                with st.expander(f"📄 {doc['title']}"):
                    st.write(f"**Mô tả:** {doc['description']}")
                    st.write(f"**File gốc:** {doc['file_name']}")
                    st.write(f"**Kích thước:** {doc['file_size'] / 1024:.1f} KB")
                    st.write(f"**Ngày upload:** {datetime.fromisoformat(doc['upload_date']).strftime('%d/%m/%Y %H:%M')}")
                    
                    # Wrap delete button in a flex container
                    st.markdown('<div class="delete-button-wrapper">', unsafe_allow_html=True)
                    if st.button(f"🗑️ Xóa tài liệu", key=f"del_{doc_id}"):
                        if self.doc_manager.delete_document(doc_id):
                            st.success("Đã xóa tài liệu!")
                            st.session_state.show_settings = False
                            st.rerun()
                        else:
                            st.error("Không thể xóa tài liệu!")
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    def get_vectorstore(self, doc_id):
        """Load and cache vectorstore"""
        if doc_id not in st.session_state.vectorstore_cache:
            vectorstore = load_vectorstore(doc_id)
            if vectorstore:
                st.session_state.vectorstore_cache[doc_id] = vectorstore
            else:
                st.session_state.vectorstore_cache[doc_id] = None
        return st.session_state.vectorstore_cache[doc_id]

    def chat_page(self):
        """Render chat interface"""
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.title("Tư vấn tuyển sinh - COFER Bot 🤖")
        
        docs = self.doc_manager.get_all_documents()
        if not docs:
            st.info("Chưa có tài liệu nào được upload. Vui lòng liên hệ admin.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
            
        latest_doc_id = list(docs.keys())[0]
            
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Nhập câu hỏi của bạn"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    vectorstore = self.get_vectorstore(latest_doc_id)
                    if vectorstore:
                        docs = vectorstore.similarity_search(prompt, k=3)
                        context = "\n".join([doc.page_content for doc in docs])    
                        response = self.get_chat_response(prompt, context)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                        st.markdown(response.text)
        
        st.markdown('</div>', unsafe_allow_html=True)

    def main(self):
        """Main application logic"""
        if 'show_settings' not in st.session_state:
            st.session_state.show_settings = False
            
        if 'vectorstore_cache' not in st.session_state:
            st.session_state.vectorstore_cache = {}
            
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        if st.session_state.show_settings:
            self.settings_page()
        else:
            self.chat_page()
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    app = ChatPDFApp()
    app.main()

if __name__ == "__main__":
    main()
