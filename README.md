# fragalysis-stack-behaviour-tests

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)

![GitHub Tag](https://img.shields.io/github/v/tag/xchem/fragalysis-stack-behaviour-tests)

[![latest stack test](https://github.com/xchem/fragalysis-stack-behaviour-tests/actions/workflows/latest-stack-test.yaml/badge.svg)](https://github.com/xchem/fragalysis-stack-behaviour-tests/actions/workflows/latest-stack-test.yaml)

A repository of behaviour tests for the backend (b/e) and frontend (f/e).
The b/e uses the Python-based [behave] package for [cucumber]-like testing
of the API, and the f/e uses TypeScript-based [Playwright] tests.

The tests are dynamically configured using numerous environment variables,
extracted for the tests by `config.py` (for the b/e) and `config.ts` (for the f/e).
All variables are prefixed with the value `BEHAVIOUR_` and are set in CI
using GitHUb **Secrets** defined in the **behaviour-stack-alan** GitHub environment.

## Contributing

The project uses: -

- [pre-commit] to enforce linting of files prior to committing them to the
  upstream repository
- [Commitizen] to enforce a [Conventional Commit] commit message format
- [Black] as a code formatter
- [Poetry] as a package manager (for the b/e)

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

## Running the b/e behaviour tests
You will need Python (ideally 3.11 or better) and [poetry].

Create a suitable Python environment: -

    poetry shell
    poetry install

Many tests rely on sensitive information that's made available through various
`BEHAVIOUR_` environment variables. The tests _should_ tell you what you need to
provide if something's missing.

As a one-time setup, install the playwright dependencies (required in order to login): -

    playwright install

To run the b/e behaviour tests run `behave` from the `behaviour` directory: -

    push behaviour
    behave

>   For further information read `behaviour/README.md`

## Running the f/e playwright tests
the Playwright tests currently rely on a a stack with the a Target
already loaded. This is the case if you run the tests immediate after the
behaviour tests, which will have already loaded this target.

The playwright tests depend on some of the environment variables used
by the behaviour tests, so you should have already set these up.

Enure you have npm/node installed and then prepare playwright: -

    npx playwright install --with-deps chrome

Run the tests from the project root directory: -

    npx playwright test

To update the set of screenshots used in comparison tests run: -

    npx playwright test --update-snapshots

>   For further information read `playwright/README.md`

---

[behave]: https://behave.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable
[commitizen]: https://commitizen-tools.github.io/commitizen/
[conventional commit]: https://www.conventionalcommits.org/en/v1.0.0/
[cucumber]: https://cucumber.io/
[playwright]: https://playwright.dev/python/docs/intro
[pre-commit]: https://pre-commit.com
[poetry]: https://python-poetry.org/
