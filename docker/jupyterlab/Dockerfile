FROM jupyter/datascience-notebook:latest

# Passing of ubuntu version to install necessary dep.
ARG arg
USER root

RUN apt-get update \
    && apt-get install -y libmariadb3 \
    && echo "root:root" | chpasswd

# Not sure right now how to check an == condition (does not work inside if)
RUN if [ -z "$arg"] ; then echo Argument not provided ; else wget http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/multiarch-support_2.27-3ubuntu1.2_amd64.deb \
&& sudo dpkg -i multiarch-support_2.27-3ubuntu1.2_amd64.deb \
&& wget http://launchpadlibrarian.net/212189159/libmysqlclient18_5.6.25-0ubuntu1_amd64.deb \
&& sudo dpkg -i libmysqlclient18_5.6.25-0ubuntu1_amd64.deb ; fi 
# TODO - see if kafka works else add librdkafka_0.11.3.orig.tar.gz

ADD libGInsUtility.so /usr/lib/x86_64-linux-gnu/libGInsUtility.so
ADD libgirpcutil.so /usr/lib/x86_64-linux-gnu/libgirpcutil.so
RUN if [ -z "$arg"] ; then ln -s /usr/lib/x86_64-linux-gnu/libmariadbclient.so.18 /usr/lib/x86_64-linux-gnu/libmysqlclient.so.18 ; fi

COPY requirements.txt ./

# install python libraries and jupyterlab extensions
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt 
# install plotly renderer for Jupyterlab
RUN jupyter labextension install jupyterlab-plotly@4.14.3


ADD librdkafka++.so.1 /usr/lib/x86_64-linux-gnu/librdkafka++.so.1
ADD librdkafka.so.1 /usr/lib/x86_64-linux-gnu/librdkafka.so.1

