import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application Config
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'thieutrung@2025')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 10))
SESSION_EXPIRY_MINUTES = int(os.getenv('SESSION_EXPIRY_MINUTES', 30))

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOCUMENTS_DIR = os.path.join(DATA_DIR, 'documents')
VECTORSTORE_DIR = os.path.join(DATA_DIR, 'vectorstore')
METADATA_FILE = os.path.join(DATA_DIR, 'metadata.json')

# Ensure directories exist
for directory in [DATA_DIR, DOCUMENTS_DIR, VECTORSTORE_DIR]:
    os.makedirs(directory, exist_ok=True)

COHERE_MODEL = "command-xlarge-nightly"
SCHOOL_CONTACT_INFO = "Trường Cao đẳng Kinh tế Đối ngoại: ĐT (028)38446320, email: tuyensinh@cofer.edu.vn, Website: www.cofer.edu.vn"