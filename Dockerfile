FROM acceleratorbase/openvino-base

ADD . /app/
WORKDIR /app
RUN python3 setup.py install

EXPOSE 8084

CMD [ "prometheus_ncs2_exporter" ]
