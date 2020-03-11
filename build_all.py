#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run docker build -> test -> push workflow for all repositories and images.
"""

import hashlib
import json
import logging
import os
import re
import subprocess
from datetime import datetime

import docker
from pynamodb.attributes import UnicodeAttribute
from pynamodb.exceptions import DoesNotExist
from pynamodb.models import Model


def create_logger():
    logger = logging.getLogger("ci-runner")
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    return logger


# --- Json utility ---
def read_text(path):
    with open(path, "rb") as f:
        content = f.read().decode("utf-8")
    return content


def strip_comment_line_with_symbol(line, start):
    """
    Strip comments from line string.
    """
    parts = line.split(start)
    counts = [len(re.findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part))
              for part in parts]
    total = 0
    for nr, count in enumerate(counts):
        total += count
        if total % 2 == 0:
            return start.join(parts[:nr + 1]).rstrip()
    else:  # pragma: no cover
        return line.rstrip()


def strip_comments(string, comment_symbols=frozenset(('#', '//'))):
    """
    Strip comments from json string.
    :param string: A string containing json with comments started by comment_symbols.
    :param comment_symbols: Iterable of symbols that start a line comment (default # or //).
    :return: The string with the comments removed.
    """
    lines = string.splitlines()
    for k in range(len(lines)):
        for symbol in comment_symbols:
            lines[k] = strip_comment_line_with_symbol(lines[k], start=symbol)
    return '\n'.join(lines)


def read_json(file_path):
    """
    Read dict data from json file

    :type file_path: str
    :rtype: dict
    """
    return json.loads(strip_comments(read_text(file_path)))


def get_json_value(file_path, json_path):
    """
    Read specific field from JSON file.

    :type file_path: str
    :param file_path: the absolute path for a json file

    :type json_path: str
    :param json_path: json path notation.
    """
    # find absolute path
    cwd = os.getcwd()

    if not os.path.isabs(file_path):
        file_path = os.path.abspath(os.path.join(cwd, file_path))

    # fix json_path
    if json_path.startswith("$."):
        json_path = json_path.replace("$.", "", 1)

    with open(file_path, "rb") as f:
        data = json.loads(strip_comments(f.read().decode("utf-8")))

    value = data
    for part in json_path.split("."):
        if part in value:
            value = value[part]
        else:
            raise ValueError("'$.{}' not found in {}".format(json_path, file_path))
    return value


def get_dockerfile_md5(dockerfile_path):
    """
    Get md5 check sum of a dockerfile, comments, empty line, tailing space
    are ignored.

    :param dockerfile_path: the absolute path of the Dockerfile

    :rtype: str
    """
    valid_lines = list()
    with open(dockerfile_path, "rb") as f:
        lines = f.read().decode("utf-8").split("\n")
        for line in lines:
            line = line.rstrip()
            # ignore comment line
            if line.startswith("#"):
                continue
            # ignore empty line
            if not bool(line):
                continue
            # trim tailing comment
            if "#" in line:
                line = line[:-(line[::-1].index("#") + 1)].rstrip()
                if line:
                    valid_lines.append(line)
            else:
                valid_lines.append(line)
    md5 = hashlib.md5()
    md5.update("\n".join(valid_lines).encode("utf-8"))
    return md5.hexdigest()


DIR_HERE = os.path.abspath(os.path.dirname(__file__))
DIR_PROJECT_ROOT = DIR_HERE

DIR_CICD = DIR_HERE
DIR_REPOS = os.path.join(DIR_PROJECT_ROOT, "repos")

# config file path
PATH_GLOBAL_CONFIG = os.path.join(DIR_PROJECT_ROOT, "config.json")
GLOBAL_CONFIG = read_json(PATH_GLOBAL_CONFIG)
REGISTRY_SERVICE = GLOBAL_CONFIG["REGISTRY_SERVICE"]

PATH_DOCKER_HUB_SECRET = os.path.join(DIR_PROJECT_ROOT, "docker-hub-secret.json")

DOCKER_HUB_USERNAME = GLOBAL_CONFIG["DOCKER_HUB_USERNAME"]
IMAGE_REBUILD_INTERVAL = get_json_value(PATH_GLOBAL_CONFIG, "IMAGE_REBUILD_INTERVAL")

GLOBAL_CONFIG = read_json(PATH_GLOBAL_CONFIG)


# --- Load Configs ---
# detect runtime
class Runtime:
    local = "local"
    circleci = "circleci"


if os.environ.get("CIRCLECI"):
    runtime = Runtime.circleci
else:
    runtime = Runtime.local

# resolve config
if runtime == Runtime.local:
    AWS_REGION = get_json_value(PATH_GLOBAL_CONFIG, "AWS_REGION")
    AWS_PROFILE = get_json_value(PATH_GLOBAL_CONFIG, "AWS_PROFILE")

    # set environment variable, allow pynamodb to detect credential
    os.environ["AWS_DEFAULT_PROFILE"] = AWS_PROFILE
    os.environ["AWS_DEFAULT_REGION"] = AWS_REGION

    try:
        DOCKER_HUB_PASSWORD = get_json_value(PATH_DOCKER_HUB_SECRET, "PASSWORD")
    except:
        DOCKER_HUB_PASSWORD = ""

    GIT_BRANCH = ""
elif runtime == Runtime.circleci:
    AWS_REGION = os.environ["AWS_DEFAULT_REGION"]
    AWS_PROFILE = None
    DOCKER_HUB_PASSWORD = os.environ["DOCKER_HUB_PASS"]
    GIT_BRANCH = os.environ["CIRCLE_BRANCH"]
else:
    raise NotImplementedError

logger = create_logger()
docker_client = docker.from_env()


# --- Image State DynamoDB backend
class ImageModel(Model):
    class Meta:
        table_name = "docker-image-state"
        region = AWS_REGION

    identifier = UnicodeAttribute(hash_key=True)
    md5 = UnicodeAttribute()
    last_update = UnicodeAttribute()

    @property
    def last_update_datetime(self):
        """
        datetime type of ``last_update``
        """
        return datetime.strptime(self.last_update, "%Y-%m-%d %H:%M:%S.%f")

    dockerhub_username = DOCKER_HUB_USERNAME  # type: str
    dir_repo_root = None  # type: str
    dir_tag_root = None  # type: str
    is_state_exists = None  # type: bool

    _repo_name = None  # type: str

    @property
    def repo_name(self):
        if self._repo_name is None:
            self._repo_name = read_text(os.path.join(self.dir_repo_root, "repo_name")).strip()
        return self._repo_name

    _tag_name = None  # type: str

    @property
    def tag_name(self):
        if self._tag_name is None:
            self._tag_name = read_text(os.path.join(self.dir_tag_root, "tag_name")).strip()
        return self._tag_name

    @property
    def dockerfile_path(self):
        return os.path.join(self.dir_tag_root, "Dockerfile")

    def has_dockerfile(self):
        return os.path.exists(self.dockerfile_path)

    _dockerfile_md5 = None  # type: str

    @property
    def dockerfile_md5(self):
        if self._dockerfile_md5 is None:
            self._dockerfile_md5 = get_dockerfile_md5(self.dockerfile_path)
        return self._dockerfile_md5

    @property
    def local_identifier(self):
        return f"{self.repo_name}:{self.tag_name}"

    @property
    def dockerhub_identifier(self):
        return f"{self.dockerhub_username}/{self.repo_name}:{self.tag_name}"

    @property
    def awsecr_identifier(self):
        raise NotImplementedError

    @property
    def smoke_test_script_path(self):
        return os.path.join(self.dir_tag_root, "smoke-test.sh")

    def run_docker_build(self):
        """
        :rtype: bool
        :return:
        """
        logger.info(f"Build docker image in context at {self.dir_tag_root} ...")
        try:
            run_and_log_command(["docker", "build", "-t", self.local_identifier, self.dir_tag_root])
            self.last_update = str(datetime.utcnow())
            logger.info("  Build success!")
            return True
        except subprocess.CalledProcessError as e:
            logger.info("  Build failed!")
            logger.info("  {}".format(e))
            return False
        except Exception:
            return False

    def run_smoke_test(self):
        """
        :rtype: bool
        :return:
        """
        logger.info(f"Run smoke test script {self.smoke_test_script_path}...")
        try:
            run_and_log_command(["bash", self.smoke_test_script_path])
            logger.info("  Test passed!")
            return True
        except subprocess.CalledProcessError as e:
            logger.info("  Test failed!")
            logger.info("  {}".format(e))
            return False
        except Exception:
            return False

    def run_docker_push(self, docker_client):
        logger.info(f"Push docker image {self.identifier} ...")
        if REGISTRY_SERVICE == "dockerhub":
            remote_identifier = self.dockerhub_identifier
        elif REGISTRY_SERVICE == "awsecr":
            remote_identifier = self.awsecr_identifier
        else:
            raise ValueError
        try:
            run_and_log_command(["docker", "tag", self.local_identifier, remote_identifier])
            docker_client.push(f"{self.dockerhub_username}/{self.repo_name}", self.tag_name)
            logger.info("  Success!")
            if self.is_state_exists:
                self.update(
                    actions=[
                        ImageModel.md5.set(self.md5),
                        ImageModel.last_update.set(self.last_update)
                    ]
                )
            else:
                self.save()
            return True
        except subprocess.CalledProcessError as e:
            logger.info("  Push failed!")
            logger.info("  {}".format(e))
            return False
        except Exception as e:
            logger.info("  {}".format(e))
            return False


ImageModel.create_table(billing_mode="PAY_PER_REQUEST")


def plan_image_to_build():
    """

    :rtype: typing.List[ImageModel]
    :return:
    """
    logger.info("Scan code repo to scheduler docker build ...")
    image_list = list()
    for repo_folder in os.listdir(DIR_REPOS):
        dir_repo_root = os.path.join(DIR_REPOS, repo_folder)
        if not os.path.isdir(dir_repo_root):
            continue
        for tag_folder in os.listdir(dir_repo_root):
            dir_tag_root = os.path.join(dir_repo_root, tag_folder)

            image = ImageModel()
            image.dir_repo_root = dir_repo_root
            image.dir_tag_root = dir_tag_root

            if not image.has_dockerfile():
                continue

            logger.info(f"  Detected '{image.local_identifier}' image")
            try:
                _image = ImageModel.get(image.local_identifier)  # type: ImageModel
                image.identifier = _image.identifier
                image.md5 = _image.md5
                image.last_update = _image.last_update
                _image.is_state_exists = True
                if image.md5 == image.dockerfile_md5:
                    if (datetime.utcnow() - image.last_update_datetime).total_seconds() > IMAGE_REBUILD_INTERVAL:
                        is_todo = True
                        logger.info(
                            "    Dockerfile not changed, but it is out dated "
                            "due to the IMAGE_REBUILD_INTERVAL setting, we need to build this one")
                    else:
                        is_todo = False
                        logger.info("    Dockerfile not changed, and not beyond the IMAGE_REBUILD_INTERVAL setting")
                        logger.info("    skip this image")
                else:
                    is_todo = True
                    logger.info("    Dockerfile has changed, we need to rebuild the image")

            except DoesNotExist:
                logger.info("    State not exists, we need to build this one")
                is_todo = True
                image.identifier = image.local_identifier
                image.md5 = image.dockerfile_md5
                image.is_state_exists = False
            except Exception as e:
                raise e

            if is_todo:
                image_list.append(image)

    logger.info("--- build plan summary ---")
    if len(image_list):
        logger.info("we got these images to build")
        for image in image_list:
            logger.info(f"  {image.local_identifier}")
    else:
        logger.info("we got NO image to build")

    return image_list


def run_and_log_command(commands):
    logger.info("Run >>> {}".format(" ".join(commands)))
    subprocess.check_output(commands)


def run_build_image(image_list):
    """
    Build and test Images.

    :type image_list: typing.List[ImageModel]
    :param image_list:

    :rtype: typing.Tuple[typing.List[ImageModel]]
    :return:
    """
    success_image_list = list()
    failed_image_list = list()
    for image in image_list:
        docker_build_success_flag = image.run_docker_build()
        if not docker_build_success_flag:
            failed_image_list.append(image)
            continue
        smoke_test_sccess_flag = image.run_smoke_test()
        if not smoke_test_sccess_flag:
            failed_image_list.append(image)
            continue
        success_image_list.append(image)

    logger.info("--- docker build summary ---")
    logger.info("following image succeed:")
    for image in success_image_list:
        logger.info(f"  {image.local_identifier}")
    logger.info("following image failed:")
    for image in failed_image_list:
        logger.info(f"  {image.local_identifier}")
    return success_image_list, failed_image_list


def run_docker_push(image_list, docker_client):
    """
    Push built images to registry.

    :type image_list: typing.List[ImageModel]
    :param image_list:
    """
    logger.info("--- push image to registry ---")
    if runtime == Runtime.local:
        logger.info("Detected local runtime, stop here.")
        return

    if not len(success_image_list):
        logger.info("No success image to push, stop here.")
        return

    if GIT_BRANCH != "master":
        logger.info("Not master branch, stop here")
        return

    docker_client.login(username=DOCKER_HUB_USERNAME, password=DOCKER_HUB_PASSWORD)
    for image in image_list:
        image.run_docker_push(docker_client)
    print("Finished.")


if __name__ == "__main__":
    todo_image_list = plan_image_to_build()
    success_image_list, failed_image_list = run_build_image(todo_image_list)
    run_docker_push(success_image_list, docker_client)
