FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt pyproject.toml README.md ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
RUN pip install --no-cache-dir --no-deps . && useradd --create-home agent \
    && mkdir -p /app/artifacts /app/data/raw/news \
    && chown -R agent:agent /app/artifacts /app/data
USER agent
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "agentic_research.api:app", "--host", "0.0.0.0", "--port", "8001"]
