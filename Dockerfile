FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

ENV PYTHONPATH .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9001

COPY . ./

CMD ["python3", "src/main.py"]
