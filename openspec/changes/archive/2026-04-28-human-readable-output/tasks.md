## 1. Implement Custom Formatter

- [ ] 1.1 Add `HumanReadableFormatter` class to `aur_python_packer/logger.py`
- [ ] 1.2 Implement `format()` method to handle INFO vs WARNING+ formatting

## 2. Update Logging Setup

- [ ] 2.1 Update `setup_logging()` to use `HumanReadableFormatter` for the console handler
- [ ] 2.2 Ensure the file handler continues to use the standard formatter with timestamps

## 3. Verification

- [ ] 3.1 Verify INFO messages in terminal have no preamble
- [ ] 3.2 Verify WARNING messages in terminal have minimal preamble
- [ ] 3.3 Verify file logs contain full preamble for all levels
