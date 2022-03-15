# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> :warning: Major version zero (0.y.z) is for initial development. Anything MAY change at any time. The public API SHOULD NOT be considered stable.

## [0.4]

### Added

- Provide type hints for all methods
  - All json responses are type hinted using nontotal TypedDicts
- Use [black](https://github.com/psf/black),
  [isort](https://github.com/PyCQA/isort),
  [flakeheaven](https://github.com/flakeheaven/flakeheaven),
  [flake8-annotations](https://github.com/sco1/flake8-annotations),
  [flake8-docstrings](https://github.com/PyCQA/flake8-docstrings) and
  [mypy](https://github.com/python/mypy) to enforce code style and quality
- Add tests using [nox](https://github.com/theacodes/nox), [pytest](https://github.com/pytest-dev/pytest) and [trycast](https://github.com/davidfstr/trycast)
  - `nox -s test` downloads a server binary and starts a preconfigured test server on port 30080
  - tests for plugin-related API endpoints are still missing

### Changed

- Renamed `gotify.gotify` to `gotify.Gotify` for conformity with naming conventions and to reduce ambiguity
- Use a nested structure
- Deprecated names are available via `__getattr__()`

### Removed

- Dropped Support for Python 3.8

## [0.3] - 2022-01-17

### Changed

- Remove read-only arguments

### Fixed

- Add missing return statement to `create_message()`

## [0.2.2] - 2022-01-14

## 0.2.1 - 2022-01-14

### Changed

- Format code with `black` with a line-length of 79
- Use new style metadata for flit

### Fixed

- Fix broken `set_password()` method
- Fix broken `delete_messages()` method

## [0.2] - 2021-08-04

### Changed

- Use a class-based interface (by @benjmarshall)

## [0.1.1] - 2021-05-29

### Changed

- Use config() with kwargs instead of args

## [0.1] - 2021-05-28

### Added

- Initial version

[unreleased]: https://github.com/d-k-bo/python-gotify/compare/v1.0.0...HEAD
[0.4]: https://github.com/d-k-bo/python-gotify/compare/1c7ddb5393957169248cf917be8efe4397b309e3...v0.4
[0.3]: https://github.com/d-k-bo/python-gotify/compare/dd5c4cbe8ca226e1c93482aff3dc74c88f345390...1c7ddb5393957169248cf917be8efe4397b309e3
[0.2.2]: https://github.com/d-k-bo/python-gotify/compare/36d8a5a10ab6cb6ef4f577a13a5db2a4ac3f5825...dd5c4cbe8ca226e1c93482aff3dc74c88f345390
[0.2]: https://github.com/d-k-bo/python-gotify/compare/6d8ea49cebd87e3ee65d8da49953fd0415e0b697...36d8a5a10ab6cb6ef4f577a13a5db2a4ac3f5825
[0.1.1]: https://github.com/d-k-bo/python-gotify/compare/v0.1.0...6d8ea49cebd87e3ee65d8da49953fd0415e0b697
[0.1]: https://github.com/d-k-bo/python-gotify/commit/0b573b3e7be1e828f8b9e12c6fd09298f7bc365c
