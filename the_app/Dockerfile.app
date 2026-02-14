FROM python:3.12-alpine AS builder
WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

#-----------------------
FROM python:3.12-alpine
WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["python", "app.py"]
