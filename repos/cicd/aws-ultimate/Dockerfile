FROM python:3.6.8-slim
COPY bootstrap.sh /tmp/bootstrap.sh
RUN echo "Start!" \
    && export PYTHON_PATHLIB_MATE_VERSION="0.0.15" \
    && export PYTHON_CONFIGIRL_VERSION="0.0.9" \
    && export PACKER_VERSION="1.4.4" \
    && export TERRAFORM_VERSION="0.12.20" \
    && export SERVERLESS_VERSION="1.61.3" \
    && bash /tmp/bootstrap.sh
