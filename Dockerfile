FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Build the vector database inside the image (downloads the embedding model once)
RUN python make_faqs.py && python src/ingest.py
EXPOSE 8000 8501
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
