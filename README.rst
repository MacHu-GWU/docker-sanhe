Sanhe Hu's DockerHub CircleCI CI/CD pipeline
==============================================================================


About This Project
------------------------------------------------------------------------------

This project is a Best Practice solution that manage **mass number of repositories and tags on DockerHub in single Git repo**. It allows you easily dev, build, test your docker image on your local machine. **Or auto trigger a build, test, publish workflow in CircleCI**.

It allows you to spin up a production ready CI/CD pipeline in 10 minutes.


Setup Project
------------------------------------------------------------------------------

It use DyanamoDB to store the state for each Image. It detects changes of Dockerfile.

**Image Build Rule**:

1. Dockerfile has to be changed.
2. If the last build is ``IMAGE_REBUILD_INTERVAL`` seconds ago, it always rebuild the image. This value can be configured in ``config.json`` file.

**Image Push Rule**:

1. Image Push only happens on push event on ``master`` branch.
2. Image Push only happens in CI/CD runtime.


For Local Laptop Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Setup a Machine User AWS IAM User account. Configure your aws cli credential in ``$HOME/.aws/credential`` and ``$HOME/.aws/config`` file.
2. Update the in-line Policy for your IAM User, just copy and paste the content from ``iam_user_policy.json`` file. Don't forget to update the aws region and aws account id in it.
3. Update the ``config.json`` file.
4. Done.


Setup CircleCI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. CircleCI APP Dashboard -> Organization Settings -> Create Context -> give the context a name, let's say ``docker-hub-cicd``.
2. Enter the following Environment Variable:
    - ``AWS_ACCESS_KEY_ID``: from your Machine IAM User.
    - ``AWS_SECRET_ACCESS_KEY``: from your Machine IAM User.
    - ``AWS_DEFAULT_REGION``: should match your ``config.json`` file.
    - ``DOCKER_HUB_PASS``: your docker hub password. otherwise CI/CD cannot push lastest image to DockerHub.
3. Update ``.circleci/config.yml``, update the context name to ``docker-hub-cicd``.
4. Add your GitHub repo to CircleCI. CircleCI APP Dashboard -> Add Projects -> Set Up Project.
5. Done.


Development Workflow
------------------------------------------------------------------------------

1. To Create a New Repo and New Tag, duplicate the sample folder ``./repos/cicd``, let's say ``./repos/my_new_reoo/my_new_tag``. Update the ``repo_name`` file and the ``tag_name`` file.
2. Update ``Dockerfile``, start from scratch::

    FROM {YOUR_BASE_IMAGE}
    COPY bootstrap.sh /tmp/bootstrap.sh
    RUN echo "Start!" \
        # Specify software versions
        && bash /tmp/bootstrap.sh

3. Start writing your setup in ``RUN`` command or ``bootstrap.sh`` shell script.
4. Run ``docker-build.sh`` utility script manually create a dev image.
5. Run ``docker-run.sh`` utility script to run a dev container, then use the ``docker exec -it ...`` command to enter the container.
6. Figure out the command you want to put in ``RUN`` command or ``bootstrap.sh`` script. **Repeat step #3, #4, #5, #6 to perfect your Dockerfile**.
7. You can use ``smoke-test.sh`` script to validate your image.
8. Once you are satisfied with your change. Run ``build_all.py`` script
 to batch build and test.
9. Issue Pull Request for code review.
10. Once change merged to ``master`` branch, It will build and push latest image to your Registry.