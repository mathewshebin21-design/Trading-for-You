FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-paper.txt .
RUN pip install --no-cache-dir -r requirements-paper.txt
COPY telegram_paper_bot.py prospective_paper.py us_paper.py identify_telegram_owner.py railway_start.py ./
CMD ["python", "railway_start.py"]
