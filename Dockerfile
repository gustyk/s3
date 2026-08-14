# Official multi-platform index digest resolved from Docker Hub on 2026-08-12.
FROM python:3.12.13-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

WORKDIR /artifact
COPY requirements.lock pyproject.toml README.md LICENSE ./
RUN python -m pip install --no-cache-dir -r requirements.lock
COPY src ./src
COPY tests ./tests
COPY config ./config
COPY docs ./docs
COPY CHANGELOG.md DATA_LICENSE.md QUALITY_TODO_Q1.md ./
RUN python -m pip install --no-cache-dir --no-deps .

CMD ["python", "-m", "src.experiment", "--mode", "selected", "--repetitions", "1", "--output-dir", "outputs/container-smoke"]
