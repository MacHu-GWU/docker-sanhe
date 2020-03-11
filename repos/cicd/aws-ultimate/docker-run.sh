#!/bin/bash
#
# This is a utility script allows you to quickly run a
# newly built image and enter it for development or debugging

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
container_name="${repo_name}-${tag_name}-dev"

docker run --rm -dt --name ${container_name} ${repo_name}:${tag_name}

echo "run this command to enter the container:"
echo
echo "docker exec -it ${container_name} sh"

echo "run this command to delete the container:"
echo
echo "docker container stop ${container_name}"
