# Usa uma imagem Python leve
FROM python:3.9-slim

# Define diretório de trabalho
WORKDIR /app

# Previne o Python de escrever arquivos .pyc e bufferizar stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte para dentro do container
COPY . .

# Define PYTHONPATH para encontrar módulos
ENV PYTHONPATH=/app

# Expõe as portas padrões (8000 para API, 8501 para Streamlit)
EXPOSE 8000
EXPOSE 8501

# O comando padrão (será sobrescrito se necessário)
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]