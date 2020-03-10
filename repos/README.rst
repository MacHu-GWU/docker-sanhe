Docker Repos Root Folder
==============================================================================

This folder is the root folder for all repository and all tags.

Every sub folder represents a docker repository (image repo root dir). Every sub-sub folder represent a tag (image tag root dir).

For example: ``./repos/cicd`` represents a docker hub repo named ``cicd``, ./repos/cicd/aws-lambda`` represents a tag ``aws-lambda``.

WARNING:

    DON't CHANGE this folder name and move this folder! (./repos)


File Structure
------------------------------------------------------------------------------

Each image tag root dir has to have two files.

1. Dockerfile
2. test.sh. A shell scripts running smoke test
