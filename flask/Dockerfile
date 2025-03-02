# pull official base image
FROM python:3.10-alpine3.17


# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1


# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

ENV TESSDATA_PREFIX=/usr/share/tessdata



# update the system and add git
RUN apk update && apk add --no-cache \
    git \
    gcc \
    libc-dev \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    tesseract-ocr \
    poppler-utils \
    && mkdir -p /usr/share/tessdata \
    && wget -q -O /usr/share/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata \
    && wget -q -O /usr/share/tessdata/tha.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/tha.traineddata

# set work directory
WORKDIR /flask_app

# install dependencies
COPY ./requirements.txt /flask_app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt


# copy project
COPY . /flask_app


# specify the entry point
ENTRYPOINT [ "./gunicorn_starter.sh" ]


# keep the Docker process running even when crashes
CMD ["tail", "-f", "/dev/null"]