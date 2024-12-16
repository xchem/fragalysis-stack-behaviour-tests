# bdd
A directory of behaviour tests for the fragalysis stack API
with [cucumber]-like features defined in the `features` directory and
steps defined in the `features/steps` directory. We use the [behave] package
to run the tests.

The `features/environment.py` module connects feature fixture tags to fixtures
(defined in `*_fixtures.py` modules).

To run the behaviour tests (from a suitable environment), run `behave`
from this directory: -

```bash
behave
```

>   You can capture stdout issued by the underlying behaviour tests
    by adding the `--output` command-line option.

---

[behave]: https://behave.readthedocs.io/en/latest/
[cucumber]: https://cucumber.io/tools/cucumber-open/
