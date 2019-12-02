FROM python:3.7

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

WORKDIR /app/datanode
CMD ["python", "node_manager.py", "http://namenode:5000", "/"]
