tuvantuyensinh-bot/
│
├── .env                    # File chứa các biến môi trường
├── requirements.txt        # File chứa các dependencies
├── streamlit_app.py        # File chính của ứng dụng
├── config.py               # Cấu hình ứng dụng
├── styles.css              # Khai báo các style sử dụng trong giao diện 
│
├── utils/
│   ├── auth.py             # Xử lý authentication
│   ├── pdf_processor.py    # Xử lý PDF
│   └── storage.py          # Xử lý lưu trữ
│
└── data/
    ├── vectorstore/        # Thư mục chứa FAISS vectorstore
    ├── documents/          # Thư mục chứa PDF files
    └── metadata.json       # File chứa metadata của documents
