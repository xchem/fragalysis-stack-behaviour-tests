# behaviour
A directory of behaviour tests for the fragalysis stack API using [Gherkin],
a domain-specific language for describing behaviour that is business-readable.
_Features_ are defined in the `features` directory and feature _steps_ are defined
in the `features/steps` directory.

We use Python's [behave] package as an executor of the tests.

>   If you're not familiar with Python's behaviour testing read its [tutorial].

To run the tests (from a suitable environment), run `behave` from the `bdd` directory: -

    behave

There is a `.behaverc` that is used to alter its default behaviour.

>   You can view stdout issued by the underlying behaviour tests
    by adding the `--no-capture` command-line option. if you don't do this
    you'll only see the output if the test fails.

>   You can avoid stopping on the first error by adding `--no-stop`

>   To see a test summary you could add `--summary`

>   To see a catalogue of all the available steps add `--steps-catalog`

## Step definition design
Feature steps are located in the standard `features/steps` directory. Direct
implementations of steps can be foun din corresponding **given**, **then**,
and **when** files (e.g. `steps_when.py`). Common logic is located in other
(`_utils.py`) files.

You will find: -

-   AWX logic used to deploy stack components in `awx_utis.py`.
-   Fragalysis Front-end logic in `browser_utils.py`. This module
    wraps-up API calls and provides stack login mechanics.
-   General Fragalysis API support in `api_utils.py`.
-   AWS S3-like storage support in `s3_utils.py`.

---

[behave]: https://behave.readthedocs.io/en/latest/
[gherkin]: https://cucumber.io/docs/gherkin/reference/
[tutorial]: https://behave.readthedocs.io/en/stable/tutorial.html
