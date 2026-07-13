# Troubleshooting

## Application does not start

```bash
python --version
pip install -r requirements.txt
streamlit run app.py
```

Confirm the virtual environment is active and the command is executed from the repository root.

## Import or package error

Recreate the virtual environment and reinstall the pinned dependencies. Do not solve the issue by changing package versions without running the complete test suite.

## Test failure

Run the failing test directly with verbose output:

```bash
python -m pytest path/to/test_file.py -vv
```

Classify whether the failure concerns input validation, normalization, calculation logic, governance, exports, or presentation before editing code.

## Upload failure

Check file type, headers, mandatory fields, supported currency, unit, and category. Do not bypass validation or fabricate missing values.

## Incorrect currency or unit result

Verify Original Currency, Original Unit Price, Normalized Currency, Normalized Unit Price, FX Rate Used, Unit of Measure, and Comparison Basis. Unsupported conversion must be blocked rather than guessed.

## Recommendation appears too strong

Check evidence quality, data confidence, eligibility, validation warnings, and human-review requirements. Weak evidence must produce capped or provisional conclusions.

## Streamlit deployment fails

Confirm the repository branch, entry point (`app.py`), dependency file, Python compatibility, and deployment logs. Keep secrets in the deployment secrets manager.

## AI assistant proposes broad rewrites

Stop the change. Require the assistant to read `AI_HANDOFF_GUIDE.md`, identify affected files, preserve protected rules, add tests, and produce a minimal diff.
