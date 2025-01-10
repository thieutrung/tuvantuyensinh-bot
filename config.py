import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Sử dụng đường dẫn tuyệt đối
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOCUMENTS_DIR = os.path.join(DATA_DIR, 'documents') 
VECTORSTORE_DIR = os.path.join(DATA_DIR, 'vectorstore')
METADATA_FILE = os.path.join(DATA_DIR, 'metadata.json')

# Tạo thư mục nếu chưa tồn tại
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Load configuration từ environment variables
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 20))
SESSION_EXPIRY_MINUTES = int(os.getenv('SESSION_EXPIRY_MINUTES', 60))
KMP_DUPLICATE_LIB_OK = bool(os.getenv('KMP_DUPLICATE_LIB_OK', True))
