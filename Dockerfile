FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-paper.txt .
RUN pip install --no-cache-dir -r requirements-paper.txt
COPY telegram_paper_bot.py prospective_paper.py us_paper.py us_accounting.py prospective_lab.py paper_backup.py news_collector.py research_inputs.py news_paper_lab.py identify_telegram_owner.py railway_start.py ./
COPY news_ledger_audit.py ./
COPY action_review_bootstrap.py AAPL_review_2026-10-14.json ./
CMD ["python", "railway_start.py"]
