FROM sanicframework/sanic:LTS

RUN mkdir -p /code
WORKDIR /code
ENV SHELL=/bin/sh

COPY . /code

RUN apk add --no-cache git libffi-dev
RUN pip install --no-cache-dir -r requirements/base.txt
RUN pip install --no-cache-dir -r requirements/extensions.txt

CMD ["python", "/code/run_api.py"]
