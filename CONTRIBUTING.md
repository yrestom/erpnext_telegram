# Contributing to Erpnext Telegram Integration

Thank you for your interest in contributing to this project! We welcome all contributions that improve the reliability, performance, and features of the ERPNext Telegram Integration.

## How to Contribute

### 1. Reporting Bugs
- Use the [GitHub Issue Tracker](https://github.com/yrestom/erpnext_telegram/issues).
- Provide a clear description of the bug and steps to reproduce it.

### 2. Suggesting Enhancements
- Open an issue to discuss your idea before implementing it.

### 3. Pull Requests
- **Fork** the repository and create your branch from `master`.
- **Performance First**: We prioritize non-blocking code. Use `frappe.enqueue` for external API calls.
- **Testing**: Add unit tests for any new logic in the corresponding `test_*.py` file.
- **Code Style**: Follow the [Frappe Coding Guidelines](https://frappeframework.com/docs/v14/user/en/tutorial/coding-standards).
- Ensure your PR description clearly explains the "Why" behind the change.

## Development Setup

1. Install the app in your bench environment:
   ```bash
   bench get-app erpnext_telegram_integration https://github.com/[your-username]/erpnext_telegram.git
   ```
2. Run tests to ensure everything is working:
   ```bash
   bench --site [your-site] run-tests --app erpnext_telegram_integration
   ```

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
