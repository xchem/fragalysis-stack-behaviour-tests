# fragalysis-stack-behaviour-tests

[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)

A repository of (experimental) Python-based end-2-end behaviour tests using [playwrite]
for UI-based testing of the Fragalysis Stack, and [behave] for [cucumber]-like testing
of the API.

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
[cucumber]: https://cucumber.io/
[playwrite]: https://playwright.dev/python/docs/intro
[poetry]: https://python-poetry.org/
