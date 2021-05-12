FROM python:3

RUN pip install -r requirements.txt
CMD ["python", "main.py"]