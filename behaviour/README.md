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

## Cheat sheet
Take a look at `behave --help`, but here are some useful additional commands: -

-   You can view stdout issued by the underlying behaviour tests
    by adding the `--no-capture` command-line option. if you don't do this
    you'll only see the output if the test fails.
-   You can avoid stopping on the first error by adding `--no-stop`
-   To see a test summary you could add `--summary`
-   To see a catalogue of all the available steps add `--steps-catalog`
-   You can run `@wip` tests by adding `--wip` (or `-w`)
-   You can run a specific feature file by adding `--include <feature file>`
    (or `-i <feature file>`), e.g. `behave -i public-target-loader`
-   You can run a specific scenario by adding  regular expression with
    `--name <expression>` (or `-n <expression>`), e.g. `behave -n "Load public targets"`

## Step definition design
Feature steps are all located in the standard `features/steps` directory, where you
will find all the steps defined in `steps.py`). To avoid cluttering the file
and ensuring it's size is not unwieldy a lot of logic can be found in relates
files in the steps directory: -

-   Configuration (extraction of environment variable values)
    is handled in `config.py`. So you can go here to find all the
    supported environment variables (all of which begin `BEHAVIOUR_`).
-   General Fragalysis API support in `api_utils.py`.
-   AWX logic used to deploy stack components in `awx_utis.py`.
-   Fragalysis Front-end logic in `browser_utils.py`. This module
    wraps-up API calls and provides stack login mechanics.
-   AWS S3-like storage support in `s3_utils.py`.

---

[behave]: https://behave.readthedocs.io/en/latest/
[gherkin]: https://cucumber.io/docs/gherkin/reference/
[tutorial]: https://behave.readthedocs.io/en/stable/tutorial.html
