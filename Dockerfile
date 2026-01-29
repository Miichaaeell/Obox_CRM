# Dockerfile
FROM python:3.13-slim


# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential libpq-dev git netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y git

RUN pip install --upgrade pip

# Copia dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

#ENTRYPOINT ["/entrypoint.sh"]

