# ------Base Image------
FROM python:3.12-slim

# -------Environment -------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# -------System Dependencies ------------
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# -------Copy Requirements------------
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# ----------Copy Project------------
COPY . /app

# ----------Expose Port-------------
EXPOSE 8000

# ----------Start Server ---------
CMD ["bash", "start_server.sh"]
