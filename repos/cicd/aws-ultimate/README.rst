



What's Include in this Image
------------------------------------------------------------------------------

.. contents::
    :depth: 1
    :local:


Packer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Packer is a cross platform, multi cloud vendor VM image builder open source software developed by Hashicorp.

- Installation Guide: it has single executable file, pre-built binary distribution on multiple platform. You can just use ``wget`` to download it, ``unzip`` to extract it, and move it to ``/usr/local/bin`` to use it.
- Download Specific version: https://releases.hashicorp.com/packer/
- Check version: ``packer --version``


Terraform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Packer is a cross platform, multi cloud vendor Infrastructure as Code orchestration open source software developed by Hashicorp.

- Installation Guide: it has single executable file, pre-built binary distribution on multiple platform. You can just use ``wget`` to download it, ``unzip`` to extract it, and move it to ``/usr/local/bin`` to use it.
- Download Specific version: https://releases.hashicorp.com/terraform/
- Check version: ``terraform --version``


NodeJs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Installation Guide Reference: https://nodejs.org/en/download/package-manager/
- For Ubuntu and Debian, it has binary distribution: https://github.com/nodesource/distributions/blob/master/README.md. There's no easy way to choose exactly the minor version you want to install, you can only choose the major version. The install command is::

    # on VM
    curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    sudo apt-get install -y nodejs

    # on docker
    curl -sL https://deb.nodesource.com/setup_12.x | bash -
    apt-get install -y nodejs
- Check version: ``nodejs --version``
- Check npm (package manager): ``npm``


Serverless
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Serverless is a microservice development and deployment framework.

- Version History: https://github.com/serverless/serverless/releases
- Installation: serverless is just a nodejs package, there's no independent binary release. The only way is ``npm install -g serverless`` or ``npm install -g serverless@1.61.3``
- Check version: ``serverless --version``
