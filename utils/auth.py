import streamlit as st
from datetime import datetime, timedelta
from config import ADMIN_PASSWORD, SESSION_EXPIRY_MINUTES

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
        
    password = st.text_input("Nhập mật khẩu admin:", type="password")
    if st.button("Đăng nhập"):
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
