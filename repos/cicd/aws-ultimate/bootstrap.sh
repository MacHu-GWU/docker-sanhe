#!/bin/bash

# install pip, virtualenv, awscli and python library
echo "[Bootstrap] install aws cli"
pip install --upgrade pip --no-cache-dir
pip install awscli --no-cache-dir
pip install boto3 --no-cache-dir

echo "[Bootstrap] install python libraries"
pip install virtualenv --no-cache-dir
pip install pathlib_mate=="${PYTHON_PATHLIB_MATE_VERSION}" --no-cache-dir
pip install configirl=="${PYTHON_CONFIGIRL_VERSION}" --no-cache-dir

# install linux tool
echo "[Bootstrap] install linux tool"
apt-get update
apt-get install -y --no-install-recommends wget
apt-get install -y --no-install-recommends curl
apt-get install -y --no-install-recommends unzip
apt-get install -y --no-install-recommends jq
apt-get install -y --no-install-recommends make
apt-get install -y --no-install-recommends git
rm -rf /var/lib/apt/lists/*

# install packer
echo "[Bootstrap] install packer"
wget "https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_amd64.zip" -P "${HOME}" -q
unzip "${HOME}/packer_${PACKER_VERSION}_linux_amd64.zip" -d "${HOME}"
mv "${HOME}/packer" "/usr/local/bin"
rm "${HOME}/packer_${PACKER_VERSION}_linux_amd64.zip"

# install terraform
echo "[Bootstrap] install terraform"
wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -P "${HOME}" -q
unzip "${HOME}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -d "${HOME}"
mv "${HOME}/terraform" "/usr/local/bin"
rm "${HOME}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip"


# install node.js for serverless
echo "[Bootstrap] install serverless"
curl -sL https://deb.nodesource.com/setup_12.x | bash -
apt-get install -y nodejs

# install serverless
npm install -g "serverless@${SERVERLESS_VERSION}"
