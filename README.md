# fragalysis-stack-behaviour-tests
A repository of (experimental) Python-based end-2-end behaviour tests using [playwrite]
for UI-based testing of the Fragalysis Stack, and [behave] for [cucumber]-like testing
of the Fragalysis Stack API.

Before running the tests, create and install a suitable Python environment: -

```bash
poetry shell
poetry install
```

Many tests rely on sensitive information that's made available through various
`STACKTEST_*` environment variables. The tests _should_ tell you what you need to
provide if something's missing.

## Running the behaviour tests
To run the stack behaviour tests navigate to the `bdd` directory and run: -

```bash
behave
```

>   For further information read `bdd/README.md`

## Running the UI tests
As a one-time setup, install the playwright dependencies: -

```bash
playwright install
```

Then run the tests from the project root or `playwrite` directory using pytest: -

```bash
pytest
```

---

[behave]: https://behave.readthedocs.io/en/latest/
[cucumber]: https://cucumber.io/
[playwrite]: https://playwright.dev/python/docs/intro
