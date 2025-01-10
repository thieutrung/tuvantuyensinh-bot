import streamlit as st
from datetime import datetime, timedelta
from config import SESSION_EXPIRY_MINUTES

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

def check_password():
    """Xác thực mật khẩu admin"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
        st.session_state.last_activity = None
    
    if st.session_state.admin_authenticated:
        # Kiểm tra session timeout
        if st.session_state.last_activity:
            time_passed = datetime.now() - st.session_state.last_activity
            if time_passed > timedelta(minutes=SESSION_EXPIRY_MINUTES):
                st.session_state.admin_authenticated = False
                return False
        st.session_state.last_activity = datetime.now()
        return True

    # Add custom CSS to position the login form
    st.markdown("""
        <style>
        [data-testid="stForm"] {
            max-width: 400px;
            margin: 0 auto;
            padding-top: 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create columns to position the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### Đăng nhập")
            password = st.text_input("Nhập mật khẩu admin:", type="password")
            
            # Add some vertical spacing before the button
            st.write("")
            
            login_button = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if login_button:
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.last_activity = datetime.now()
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Mật khẩu không đúng!")
    
    return False

def logout():
    """Đăng xuất admin"""
    st.session_state.admin_authenticated = False
    st.session_state.last_activity = None
    st.rerun()
