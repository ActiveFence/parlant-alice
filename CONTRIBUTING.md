# Contributing to parlant-alice

Thank you for your interest in contributing to parlant-alice! We welcome contributions from the community.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Ways to Contribute

There are many ways to contribute to this project:

- **Report bugs** - Help us identify and fix issues
- **Suggest features** - Propose new functionality or improvements
- **Improve documentation** - Fix typos, clarify instructions, or add examples
- **Submit code** - Fix bugs, implement features, or improve performance
- **Review pull requests** - Provide feedback on proposed changes

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/parlant-alice.git
   cd parlant-alice
   ```
3. **Add the upstream repository** as a remote:
   ```bash
   git remote add upstream https://github.com/ActiveFence/parlant-alice.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

### Setting up your development environment

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the package in editable mode with dev dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

   Pre-commit hooks will automatically run linting and formatting checks before each commit.

## Making Changes

### Creating a branch

Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Use descriptive branch names:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation changes
- `refactor/` for code refactoring

### Making commits

- Write clear, concise commit messages
- Use the present tense ("Add feature" not "Added feature")
- Reference relevant issue numbers in commit messages (e.g., "Fix #123")
- Keep commits focused on a single change

## Code Style and Standards

This project follows Python best practices and uses automated tools to enforce code quality:

### Linting and Formatting

- **Ruff**: Used for linting and code formatting
- **MyPy**: Used for static type checking

All code must:
- Follow [PEP 8](https://pep8.org/) style guidelines
- Include type hints for function signatures
- Pass ruff linting checks
- Pass mypy type checks

### Running Code Quality Checks

Pre-commit hooks will automatically run these checks, but you can also run them manually:

```bash
# Run ruff linting and formatting
ruff check .
ruff format .

# Run type checking
mypy parlant
```

Or run all pre-commit hooks manually:

```bash
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
pytest
```

### Writing Tests

- Add tests for new features
- Ensure bug fixes include regression tests
- Maintain or improve code coverage
- Place tests in appropriate test files

## Submitting Changes

### Before Submitting a Pull Request

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure all tests pass**:
   ```bash
   pytest
   ```

3. **Ensure code quality checks pass**:
   ```bash
   pre-commit run --all-files
   ```

4. **Update documentation** if needed

### Creating a Pull Request

1. **Push your changes** to your fork:
   ```bash
   git push origin your-branch-name
   ```

2. **Open a pull request** on GitHub:
   - Go to the [parlant-alice repository](https://github.com/ActiveFence/parlant-alice)
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the pull request template

3. **Pull request guidelines**:
   - Provide a clear title and description
   - Reference any related issues (e.g., "Fixes #123")
   - Describe what changes you made and why
   - Include screenshots or examples if relevant
   - Ensure CI checks pass

### Pull Request Review Process

- Maintainers will review your pull request
- Be responsive to feedback and questions
- Make requested changes by pushing new commits
- Once approved, a maintainer will merge your pull request

## Reporting Issues

When reporting bugs, please include:

- **Clear title** and description
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details**: OS, Python version, package version
- **Code examples** or error messages if applicable
- **Screenshots** if relevant

Create an issue at: https://github.com/ActiveFence/parlant-alice/issues

## Feature Requests

We welcome feature suggestions! When proposing a feature:

- **Describe the feature** and its use case
- **Explain the benefits** and who would benefit
- **Provide examples** of how it would work
- **Consider alternatives** you've thought about

Create a feature request at: https://github.com/ActiveFence/parlant-alice/issues

## Suggesting Code Changes or Additions

To suggest code changes or additions:

1. **Check existing issues and pull requests** to avoid duplicates
2. **Open an issue first** for significant changes to discuss the approach
3. **Follow the pull request process** described above
4. **Be clear about the problem** you're solving or improvement you're making
5. **Keep changes focused** - submit separate PRs for unrelated changes
6. **Update documentation** to reflect your changes
7. **Add tests** to verify your changes work as expected

For minor changes (typos, small bug fixes), you can directly submit a pull request without opening an issue first.

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with your question
- Check existing issues and documentation
- Reach out to the maintainers

## License

By contributing to parlant-alice, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to parlant-alice!
