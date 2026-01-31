# ============ Base stage ============

FROM python:3.13-slim-trixie AS base
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
  && rm -rf /var/lib/apt/lists/*


# ============ Build stage ============
FROM base AS builder

# Dependências só de build (não ficam no runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip wheel setuptools

# Copiar requirements primeiro para melhorar cache
COPY requirements.txt ./

RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============ Runtime stage ============

FROM base AS runtime
COPY --from=builder /install /usr/local
COPY . .
