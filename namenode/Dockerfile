FROM python:3.7

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000
WORKDIR /app/namenode
CMD ["python", "namenode.py"]