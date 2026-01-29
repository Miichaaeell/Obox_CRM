# Dockerfile
FROM python:3.13-slim-trixie


# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y libpq-dev git && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copia dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .


