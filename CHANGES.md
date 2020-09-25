# Change Log

## v0.2.0

- Converted `manageiq.credentials_test` workflow to Orquesta
  Contributed by Nick Maludy (Encore Technologies)

## v0.1.6

- Pinned parsedatetime to <2.6 to fix tests on Python 2.7
- Updated requirements file handling and Makefile

## v0.1.5

- Fixed issue with wait-for module where newest version only supports python 3
  Contributed by Bradley Bishop (Encore Technologies)

## v0.1.4

- Fixed error with CF 4.7 in hosts.py credential_check action
  Contributed by John Schoewe (Encore Technologies)

## v0.1.3

- Added action to refresh a given or every provider.
  Added action to check the status of a task.
  Fixed circle ci python 3 errors.
  Contributed by John Schoewe (Encore Technologies)

## v0.1.2

- Removed payload from debug logs when creating objects.
  Affects `manangeiq.tags_create` `manangeiq.provision_request_create`.
  Contributed by Nick Maludy (Encore Technologies)

## v0.1.1

- Version bump to fix tagging issues, and linting bypass due to changed flake8 rules

## v0.1.0

- Initial Revision
