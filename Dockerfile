FROM tiangolo/uvicorn-gunicorn:python3.10
ENV TZ=Asia/Seoul

WORKDIR /app

RUN wget https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py &&\
    python get-poetry.py --preview --yes &&\
    rm -f get-poetry.py

COPY ./pyproject.toml /app/
COPY ./poetry.lock* /app/

RUN poetry install --no-root --no-dev

COPY ./ /app

CMD ["poetry", "run", "task", "prod"]