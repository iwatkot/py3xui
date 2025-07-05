# Contributing to py3xui

<p align="center">
    <a href="#Reporting-Issues">Reporting Issues</a> •
    <a href="#How-to-Contribute">How to Contribute</a><br>
    <a href="#Code-style">Code style</a> •
    <a href="#Submitting-a-Pull-Request">Submitting a Pull Request</a> •
    <a href="#Code-of-Conduct">Code of Conduct</a>
</p>

Thank you for your interest in contributing to py3xui!

## Reporting Issues
If you encounter any issues while using py3xui, please follow these steps to report them:
1. **Check Existing Issues**: Before creating a new issue, please check the [existing issues](https://github.com/iwatkot/py3xui/issues) to see if your issue has already been reported.
2. **Create a New Issue**: If your issue is not listed, you can create a new issue by clicking on the "New issue" button in the [Issues tab](https://github.com/iwatkot/py3xui/issues).
3. **Provide Detailed Information**: When creating a new issue, please provide as much detail as possible, including:
- Description of the issue
- Expected behavior
- Actual behavior
- Steps to reproduce the issue
- Python version
- OS
- py3xui version
- 3x-UI version
- Code snippet or a minimal example to reproduce the issue (if applicable)
- JSON representation of the request to the API (if applicable)

This will help me understand the issue better and provide a quicker resolution.

## How to Contribute

ℹ️ You'll need to install [Git](https://git-scm.com/) and [Python](https://www.python.org/downloads/) (version 3.11 or higher) on your machine to contribute to the py3xui project. You also must have a GitHub account to fork the repository and submit pull requests.  
ℹ️ It's recommended to use [Visual Studio Code](https://code.visualstudio.com/) as your code editor, since the repository already contains a `.vscode` directory with the recommended settings, and launch configurations for debugging.

1. **Fork the Repository**: Start by [forking the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) you want to contribute to. This creates a copy of the repository under your GitHub account.
2. **Clone Your Fork**: Clone your forked repository to your local machine using the command:

```bash
git clone <your_forked_repository_url>
```

3. **Create a New Branch**: Before making any changes, create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```

4. **Prepare a virtual environment**: It's recommended to use a virtual environment to manage dependencies. The repository already contains ready-to-use scripts in the `dev` directory. You can use the following command to create a virtual environment and install dependencies:

```bash
sh dev/create_venv.sh # For Linux/MacOS
dev\create_venv.ps1 # For Windows
```

Dependencies will be installed from the `dev/requirements.txt` file.

5. **Make Your Changes**: Now, you can make your changes in the codebase. Ensure that your code follows the project's coding standards and conventions.

6. **Use the demo.py script**: The `demo.py` script is provided to help you test your changes. If you're using VSCode, you can simply select the `demo.py` launch configuration and run it.  

If you're using the terminal, you can run the script with the following command:

```bash
python demo.py
```

7. ⚠️ **Run MyPy**: The project relies on the static type checker [MyPy](https://mypy.readthedocs.io/en/stable/).  
   Before submitting a pull request, ensure that your code passes MyPy checks. You can run MyPy with the following command:

```bash
mypy py3xui
```

ℹ️ The automatic checks will also be performed by the CI/CD pipeline, but it's a good practice to run them locally before submitting a pull request.

8. ⚠️ **Run Pylint**: The project uses [Pylint](https://pylint.pycqa.org/en/latest/) for code quality checks.  
   Before submitting a pull request, ensure that your code passes Pylint checks. You can run Pylint with the following command:

```bash
pylint py3xui
```

ℹ️ The automatic checks will also be performed by the CI/CD pipeline, but it's a good practice to run them locally before submitting a pull request.

9. ⚠️ **Run PyTest**: The project uses [PyTest](https://docs.pytest.org/en/stable/) for automated testing. 
   Before submitting a pull request, ensure that your code passes all tests. You can run the tests with the following command:

```bash
pytest
```

ℹ️ The automatic tests will also be performed by the CI/CD pipeline, but it's a good practice to run them locally before submitting a pull request.

## Code style
The py3xui project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.  
Please ensure that your code adheres to these guidelines and is properly formatted. Remember to run Pylint and MyPy to check for any style violations before submitting your pull request.  
All methods, functions and classes must have type hints (including generic types) and docstrings in [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).  

If those requirements are not met, your pull request will not be accepted.

## Submitting a Pull Request
Once you have made your changes and tested them, you can submit a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to the repository.

## Code of Conduct
By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).