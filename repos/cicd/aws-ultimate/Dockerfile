FROM python:3.6.8-slim
COPY bootstrap.sh /tmp/bootstrap.sh
RUN echo "Start!" \
    # Specify software versions
    && export PYTHON_PATHLIB_MATE_VERSION="1.0.1" \
    && export PYTHON_CONFIGIRL_VERSION="0.0.10" \
    && export PYTHON_PYSECRET_VERSION="0.0.8" \
    && export PACKER_VERSION="1.6.6" \
    && export TERRAFORM_VERSION="0.14.4" \
    && export SERVERLESS_VERSION="2.18.0" \
    && bash /tmp/bootstrap.sh
