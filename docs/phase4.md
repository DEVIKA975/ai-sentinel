# AI Sentinel Phase 4: Ghost AI Quality & CI/CD

Phase 4 introduces professional software quality controls to the AI Sentinel platform.

## 🧪 Automated Testing
We have established a comprehensive unit test suite using `pytest`.

### Test Structure
- **`tests/test_detector.py`**:- **Unit Tests**: Validates `GhostAIDetector` logic (sensitive data, malicious domains).
- **`tests/test_policies.py`**: Ensures that organizational policies and environment-based configurations are loaded correctly.

### Running Tests Locally
To run the tests on your machine:
```bash
pip install pytest
pytest tests/
```

## 🚀 Continuous Integration (GitHub Actions)
The project now includes an automated CI pipeline defined in `.github/workflows/ci.yml`.

### Automated Checks
Every time code is pushed to `main` or a Pull Request is opened, the following checks are performed:
1.  **Linting**: `flake8` checks for PEP8 compliance and syntax errors.
2.  **Security Scanning**: `bandit` scans for common security vulnerabilities in the source code.
3.  **Unit Testing**: The `pytest` suite is executed to ensure no regressions were introduced.

## 🛡️ Best Practices
- **Pre-commit Checks**: Developers are encouraged to run `pytest` and `flake8` before pushing changes.
- **Coverage**: Aim for high test coverage on core detection and mitigation logic.
