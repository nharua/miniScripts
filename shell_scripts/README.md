# Shell Utility Scripts

This collection of shell scripts provides various small utilities to speed up common tasks.
Each script is self-contained and can be used directly from the command line.

## 1. init-pyproject

A helper script to quickly bootstrap a new Python project with sensible defaults.

### Features

- Initializes a Git repository with `main` branch.
- Creates essential starter files: `.env`, `.gitignore`, `LICENSE`, `README.md`.
- Downloads Python `.gitignore` template from GitHub.
- Adds current year automatically to the `LICENSE`.
- Optional `--venv` flag to create a local `.venv` folder and add it to `.gitignore`.

### Usage

- Initialize in current directory:
``` bash
init-pyproject
```

- Initialize in a new directory:
``` bash
init-pyproject myproject
```

- Initialize with virtual environment:
``` bash
init-pyproject myproject --venv
```

### Example Result

```yaml
myproject/
├── .env
├── .git/
├── .gitignore
├── .venv/        # only if --venv is used
├── LICENSE
└── README.md
```
