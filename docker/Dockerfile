FROM python:3.7.4-alpine

# app workdir
WORKDIR /app

# copy app dependencies
COPY requirements.txt docker/*.sh ./

# install dependecies
RUN set -ex \
    # install system dependencies
	&& apk add --update bash \
	&& apk add --virtual .fetch-deps \
	    gcc \
	    musl-dev \
	    libffi-dev \
	    make \
	\
    # install app dependencies
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r ./requirements.txt --upgrade \
    \
    # clean pip cache
    && rm -rf /root/.cache/pip/* \
    \
    # clean system dependencies
    && rm -rf /var/cache/apk/*

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
ENTRYPOINT ["./start.sh"]
CMD ["long"]
