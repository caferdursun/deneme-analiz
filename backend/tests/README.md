# Test Files

This directory contains test scripts for various components of the application.

## Test Scripts

### PDF Processing Tests

- **`test_pdf_analysis.py`** - Tests PDF analysis functionality
  - Tests Claude API integration for PDF extraction
  - Usage: `python tests/test_pdf_analysis.py`

### Data Validation Tests

- **`test_json_validity.py`** - Validates JSON data structures
  - Tests JSON schema validation
  - Usage: `python tests/test_json_validity.py`

## Running Tests

All tests should be run from the backend directory:

```bash
cd /root/projects/deneme-analiz/backend
source venv/bin/activate
python tests/<test_name>.py
```

## Future Test Organization

Consider migrating to pytest framework for better test organization:

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## Notes

- These are standalone test scripts, not pytest tests yet
- Each test can be run independently
- Tests may require API keys and database access
- Check test file contents for specific requirements
