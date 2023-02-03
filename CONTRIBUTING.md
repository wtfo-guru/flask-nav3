# How to contribute


## Dependencies

We use [poetry](https://github.com/python-poetry/poetry) to manage the dependencies.

To install them you would need to run `install` command:

```bash
poetry install
```

To activate your `virtualenv` run `poetry shell`.

## One magic command

Run `make test` to run everything we have!

## Tests

We use `pytest` and `flake8` for quality control.
We also use [wemake_python_styleguide](https://github.com/wemake-services/wemake-python-styleguide) to enforce the code quality.

To run all tests:

```bash
make unit
```

To run linting:

```bash
make lint
```

Keep in mind: default virtual environment folder excluded by flake8 style checking is `.venv`.
If you want to customize this parameter, you should do this in `setup.cfg`.
These steps are mandatory during the CI.

## Type checks

We use `mypy` to run type checks on our code.
To use it:

```bash
make mypy
```

This step is mandatory during the CI.

## Submitting your code

What the point of this method?

1. We use protected `main` branch,
   so the only way to push your code is via pull request
2. We use issue branches: to implement a new feature or to fix a bug
   create a new branch named `issue-$TASKNUMBER`
3. Then create a pull request to `main` branch
4. We use `git tag`s to make releases, so we can track what has changed
   since the latest release

So, this way we achieve an easy and scalable development process
which frees us from merging hell and long-living branches.

In this method, the latest version of the app is always in the `main` branch.

### Before submitting

Before submitting your code please do the following steps:

1. Run `make test` to make sure everything was working before
2. Add any changes you want
3. Add tests for the new changes
4. Edit documentation if you have changed something significant
5. Run `make test` again to make sure it is still working

## Other help

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.
