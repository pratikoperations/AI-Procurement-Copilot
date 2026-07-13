# Deployment Guide

## Streamlit Community Cloud

1. Connect the GitHub repository to Streamlit Community Cloud.
2. Select the intended branch and `app.py` as the entry point.
3. Confirm `requirements.txt` is detected.
4. Add required secrets only through the deployment secrets interface.
5. Deploy and complete the smoke-test checklist below.

## Smoke Test

- App loads without exception.
- Demo and upload workflows open.
- Packaging and Raw Material views render.
- Supplier comparison, scenarios, allocation, and exports run.
- Eligibility warnings and human-review controls remain visible.
- No credentials or private data appear in logs or outputs.

## Release Control

Deploy stable releases from protected, reviewed branches or tags. Do not deploy experimental LLM-provider integrations over the stable v1.0.0 deployment without separate validation.

## Rollback

Redeploy the last known-good commit or release tag. Record the failed commit, symptoms, affected workflow, and rollback result in the changelog or issue tracker.

## Provider Independence

The current Streamlit application is not dependent on ChatGPT for runtime execution. Any future OpenAI, Anthropic, Google, or local-model integration must use environment-based credentials, documented fallbacks, and provider-specific tests.
