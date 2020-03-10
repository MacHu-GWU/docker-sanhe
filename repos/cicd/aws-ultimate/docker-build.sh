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

docker build . -t ${repo_name}:${tag_name}
#docker image ls
#docker image rm ""
