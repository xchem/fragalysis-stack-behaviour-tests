# bdd
A directory of behaviour tests for the fragalysis stack API
using [Gherkin], a domain-specific language for describing behaviour that is
business-readable. _Features_ are defined in the `features` directory and
feature _steps_ defined in the `features/steps` directory.

We use Python's [behave] package as an executor of the tests.

To run the behaviour tests (from a suitable environment), run `behave`
from the `bdd` directory: -

```bash
behave
```

>   You can view stdout issued by the underlying behaviour tests
    by adding the `--no-capture` command-line option. if you don't do this
    you'll only see the output if the test fails.

>   You can stop on the first error by adding `--stop` to the command-line.

---

[behave]: https://behave.readthedocs.io/en/latest/
[gherkin]: https://cucumber.io/docs/gherkin/reference/
