#!/bin/bash

if [ -n "${BASH_SOURCE}" ]
then
    dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
else
    dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
fi
dir_tag="${dir_here}"
dir_repo="$(dirname ${dir_tag})"

repo_name=$(cat ${dir_repo}/repo_name)
tag_name=$(cat ${dir_tag}/tag_name)
container_name="${repo_name}-${tag_name}-smoke-test"

docker run --rm -dt --name "${container_name}" "${repo_name}:${tag_name}"
sleep 2 # sleep 2 seconds wait web server become ready

check_exit_status() {
    exit_status=$1
    if [ $exit_status != 0 ]
    then
        echo "FAILED!"
        docker container stop "${container_name}"
        exit $exit_status
    fi
}

echo "is aws cli installed?"
docker exec -t "${container_name}" aws --version

echo "is boto3 installed?"
docker exec -t "${container_name}" pip list | grep boto3
check_exit_status $?

echo "is configirl installed?"
docker exec -t "${container_name}" pip list | grep configirl
check_exit_status $?

echo "is pathlib_mate installed?"
docker exec -t "${container_name}" pip list | grep pathlib-mate
check_exit_status $?

echo "is packer installed?"
docker exec -t "${container_name}" packer --version
check_exit_status $?

echo "is terraform installed?"
docker exec -t "${container_name}" terraform --version
check_exit_status $?

echo "is serverless installed?"
docker exec -t "${container_name}" serverless --version
check_exit_status $?

docker container stop "${container_name}"
