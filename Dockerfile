FROM node:11-alpine as frontend-builder

COPY package.json      /build/package.json
COPY package-lock.json /build/package-lock.json
RUN cd /build \
	&& npm install --registry=https://registry.npm.taobao.org --disturl=https://npm.taobao.org/dist \
	&& npm cache clean --force
ENV PATH /build/node_modules/.bin:$PATH

ADD . /build/
RUN cd /build \
	&& npm run build \
	&& npm run build-admin

# ---------- 8< ----------

FROM python:3.7-alpine

ENV PROJECT_ROOT=/project
WORKDIR $PROJECT_ROOT

RUN sed -i 's@http://dl-cdn.alpinelinux.org/alpine@https://mirrors.tuna.tsinghua.edu.cn/alpine@g' /etc/apk/repositories \
	&& apk add --no-cache nginx \
	&& apk add --no-cache libssl1.1 libedit \
	&& rm -rf /root/.cache \
	&& mkdir -p /run/nginx \
	&& ln -snf /dev/stdout /var/log/nginx/access.log \
	&& ln -snf /dev/stdout /var/log/nginx/error.log

RUN apk add --no-cache tzdata \
	&& cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
	&& echo "Asia/Shanghai" > /etc/timezone

# install python requirements first, utilizing build cache
ADD requirements.txt $PROJECT_ROOT/
ADD natureself/requirements.txt $PROJECT_ROOT/natureself/
RUN apk add --no-cache py3-lxml py3-psycopg2 mariadb-dev mariadb-connector-c libmagic \
	&& apk add --no-cache --virtual .build-dep libffi-dev python3-dev build-base postgresql-dev mariadb-dev libxml2-dev libxslt-dev \
	&& pip3 install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -r requirements.txt \
	&& apk del .build-dep

COPY .  $PROJECT_ROOT/

COPY --from=frontend-builder /build/build/admin $PROJECT_ROOT/html/admin
COPY --from=frontend-builder /build/build/webapp $PROJECT_ROOT/build/webapp
COPY --from=frontend-builder /build/build/webpack-stats-webapp.json $PROJECT_ROOT/build/webpack-stats-webapp.json
RUN set -x \
	&& cp nsproject/settings_local.example.py nsproject/settings_local.py \
	&& sed -i 's@#SECRET_KEY@SECRET_KEY@g' nsproject/settings_local.py \
	&& DJANGO_DEBUG=false python3 manage.py collectstatic --noinput \
	&& rm -f nsproject/settings_local.py \
	&& mkdir -pv $PROJECT_ROOT/data \
	&& ln -snf $PROJECT_ROOT/build/static $PROJECT_ROOT/html/static \
	&& ln -snf $PROJECT_ROOT/data $PROJECT_ROOT/html/media

ADD entrypoint.sh /entrypoint.sh
ADD nginx.conf /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/entrypoint.sh"]
