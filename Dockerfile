FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive

# Instala apenas o Xvfb para o display virtual (headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Dá permissão de execução ao entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 10000

CMD ["./entrypoint.sh"]