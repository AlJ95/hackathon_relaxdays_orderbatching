# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR .

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY orderbatching .

CMD ["echo", "Use ./main.py with the input {instance_path} and the desired {solution_path}"]
CMD ["echo", "Example: python3 main.py ./data/instance0.json ./data/solution0.json"]