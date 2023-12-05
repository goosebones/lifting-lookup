# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.9"
ARG DISTRO_VERSION="3.12"


# Stage 1
FROM python:${RUNTIME_VERSION}-alpine${DISTRO_VERSION} AS python-alpine

RUN apk add --no-cache \
    libstdc++

# Stage 2
FROM python-alpine AS build-image

RUN apk add --no-cache \
    build-base \
    libtool \
    autoconf \
    automake \
    libexecinfo-dev \
    make \
    cmake \
    libcurl

ARG FUNCTION_DIR
ARG RUNTIME_VERSION

RUN mkdir -p ${FUNCTION_DIR}

RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}


# Stage 3
FROM python-alpine as build-image2

ARG FUNCTION_DIR

WORKDIR ${FUNCTION_DIR}

COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

RUN apk update \
    && apk add gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg-turbo-dev

COPY requirements.txt .

RUN python${RUNTIME_VERSION} -m pip install selenium webdriver_manager awswrangler --target ${FUNCTION_DIR}

# Stage 4
FROM python-alpine

ARG FUNCTION_DIR

WORKDIR ${FUNCTION_DIR}

COPY --from=build-image2 ${FUNCTION_DIR} ${FUNCTION_DIR}

RUN apk add jpeg-dev zlib-dev libjpeg-turbo-dev \
    && apk add chromium chromium-chromedriver

ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie

RUN chmod 755 /usr/bin/aws-lambda-rie

COPY app/* ${FUNCTION_DIR}
COPY entry.sh /

ENTRYPOINT [ "/entry.sh" ]

CMD [ "refresh.handler" ]
