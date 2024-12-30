chatpdf_v2/
│
├── .env                    # File chứa các biến môi trường
├── requirements.txt        # File chứa các dependencies
├── app.py                  # File chính của ứng dụng
├── config.py              # Cấu hình ứng dụng
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
