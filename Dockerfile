FROM python:3.8

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=src
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0
ENV NCBI_API_KEY="d07c55ffe0e94ecee92244f0922fb6216808"
ENV X_ELS_APIKey="18cea8004848f339d14dd509a16e753e"
ENV X_ELS_Insttoken="aa8087d5506a067fa3e1c2761628f450"
ENV SQLALCHEMY_DATABASE_URI=sqlite://instance/bambu.db

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]