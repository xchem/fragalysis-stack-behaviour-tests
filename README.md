# fragalysis-stack-behaviour-tests

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)

![GitHub Tag](https://img.shields.io/github/v/tag/xchem/fragalysis-stack-behaviour-tests)

A repository of (experimental) Python-based end-2-end behaviour tests using [playwrite]
for UI-based testing of the Fragalysis Stack, and [behave] for [cucumber]-like testing
of the API.

## Contributing

The project uses: -

- [pre-commit] to enforce linting of files prior to committing them to the
  upstream repository
- [Commitizen] to enforce a [Conventional Commit] commit message format
- [Black] as a code formatter
- [Poetry] as a package manager

You **MUST** comply with these choices in order to  contribute to the project.

To get started review the pre-commit utility and the conventional commit style
and then set-up your local clone by following the **Installation** and
**Quick Start** sections: -

    poetry shell
    poetry install --with dev
    pre-commit install -t commit-msg -t pre-commit

Now the project's rules will run on every commit, and you can check the
current health of your clone with: -

    pre-commit run --all-files

## Getting started

You will need Python (ideally 3.11 or better) and [poetry].

Create a suitable Python environment: -

    poetry shell
    poetry install

Many tests rely on sensitive information that's made available through various
`STACKTEST_*` environment variables. The tests _should_ tell you what you need to
provide if something's missing.

## Running the behaviour tests

To run the stack behaviour tests run `behave` from the `bdd` directory: -

    push bdd
    behave

>   For further information read `bdd/README.md`

## Running the UI tests

As a one-time setup, install the playwright dependencies: -

    playwright install

Then run the tests from the project root or `playwrite` directory using pytest: -

    pytest

---

[behave]: https://behave.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable
[commitizen]: https://commitizen-tools.github.io/commitizen/
[conventional commit]: https://www.conventionalcommits.org/en/v1.0.0/
[cucumber]: https://cucumber.io/
[playwrite]: https://playwright.dev/python/docs/intro
[pre-commit]: https://pre-commit.com
[poetry]: https://python-poetry.org/
