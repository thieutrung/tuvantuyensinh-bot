# Admissions Consulting Chatbot

Admissions Consulting Chatbot is a web application built on the LangChain programming library platform and Streamlit UI interface, using RAG (Retrieval Augmented Generation) architecture to answer admissions questions based on PDF document files. The system integrates Cohere's LLM API service for vector data generation, natural language processing and answer generation.

Main components:
• Frontend: Streamlit web interface
• Backend: Python with PDF processing and vector storage modules
• Vector Database: FAISS for embedding storage and search
• LLM Service: Cohere API for embedding creation and answer generation

## Installation
Follow these steps:
1. Clone the repository
   ```
   git clone https://github.com/thieutrung/tuvantuyensinh-bot.git
   ```
2. Create a virtual environment and activate it (optional, but highly recommended).
   ```
   python -m venv .venv
   Windows: .venv\Scripts\activate
   Linux: source .venv/bin/activate
   ```
3. Install required packages:
   ```
   python -m pip install -r requirements.txt
   ```
4. Create a .env file in the root of the project and populate it with the following keys. You'll need to obtain your admin password and api keys:
   ```
   ADMIN_PASSWORD=
   COHERE_API_KEY=
   MAX_FILE_SIZE_MB=10
   SESSION_EXPIRY_MINUTES=30
   KMP_DUPLICATE_LIB_OK=TRUE
   ```
5. Run the program:
   ```
   streamlit run app.py
   ```
## Configuration
The structure of this entire project consists of the following files:

tuvantuyensinh-bot/
│
├── .env                    # File chứa các biến môi trường
├── requirements.txt        # File chứa các dependencies
├── app.py                  # File chính của ứng dụng
├── config.py               # Cấu hình ứng dụng
│
├── utils/
│   ├── __init__.py
│   ├── auth.py            # Xử lý authentication
│   ├── pdf_processor.py   # Xử lý PDF
│   └── storage.py         # Xử lý lưu trữ
│
└── data/
    ├── vectorstore/       # Thư mục chứa FAISS vectorstore
    ├── documents/         # Thư mục chứa PDF files
    └── metadata.json      # File chứa metadata của documents


## Resources
Thanks to the amazing libraries and services listed below:
* [Langchain](https://www.langchain.com/)
* [Cohere] (https://cohere.com)

## License
MIT

