# Contributing to ShieldGate

First off, thank you for considering contributing to ShieldGate! 🎉 It's people like you that will help us build a safer internet for everyone.

Reading and following these guidelines will help us make the contribution process easy and effective for everyone involved. It also communicates that you respect the time of the developers managing and developing this open-source project.

## 🚀 How Can I Contribute?

### 🐛 Reporting Bugs
Bugs are tracked as [GitHub issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues). Please create an issue and provide the following information:

*   **Use a clear and descriptive title.**
*   **Describe the exact steps to reproduce the problem.** Don't assume we know how to trigger the bug.
*   **Provide specific examples.** Include sample text that triggers a false positive/negative, screenshots, or links to similar examples.
*   **Describe the behavior you observed** and point out what exactly is the problem with that behavior.
*   **Describe the expected behavior.**
*   **List your environment:** OS, Python version, and application version.

### 💡 Suggesting Enhancements
Enhancement suggestions are also tracked as GitHub issues. Please provide the following:

*   **Use a clear and descriptive title.**
*   **Provide a detailed description of the proposed enhancement.**
*   **Explain why this enhancement would be useful** to most ShieldGate users.
*   **List any other platforms or contexts** where this enhancement would be relevant.

### 🌍 Adding Support for New Platforms
A key goal of ShieldGate is to be universally useful. If you want to help add detection for a new platform (e.g., WhatsApp, Signal, Twitter DMs), here's how:

1.  **Open an Issue First:** Discuss the new platform. We need to ensure it aligns with our goals.
2.  **Data is King:** The model is only as good as its data. Contribution of a **labeled dataset** (spam vs. ham messages) for that platform is the most critical step.
3.  **Follow our data format:** See the `training/datasets/README.md` file for the required format (e.g., CSV with `text` and `label` columns).

### 🧪 Improving the Model
Contributions to the core machine learning model are highly welcome. This includes:
*   **Feature Engineering:** New ideas for text preprocessing or feature extraction.
*   **Model Experimentation:** Trying out different algorithms (in the `training/` notebooks) and demonstrating improved performance.
*   **Hyperparameter Tuning:** Systematically improving the current Logistic Regression model.

### 🧑‍💻 Code Contributions
We welcome pull requests (PRs). Please follow this process:

## 📋 Development Process

1.  **Fork the repo** and create your branch from `main`. Use a descriptive branch name (e.g., `fix-gui-crash`, `add-whatsapp-dataset`, `feature-new-preprocessor`).
2.  **Set up the development environment.**
    ```bash
    git clone https://github.com/your-username/shieldgate-repo.git
    cd shieldgate-repo
    # We recommend using a virtual environment
    python -m venv venv
    # On Linux/Mac:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Make your changes.** If you're adding code, please write or update tests if applicable.
4.  **Test your changes thoroughly.** Run the desktop app and ensure it works. Test the core model with various inputs.
5.  **Ensure your code follows the project's style.**
    *   We use **Black** for code formatting. Please run `black .` on your code before committing.
    *   We use **PEP 8** as a style guide.
    *   Use descriptive variable and function names.
6.  **Update the documentation** if you change something that affects how the project works (e.g., new dependencies, new CLI arguments).
7.  **Commit your changes.** We use [Conventional Commits](https://www.conventionalcommits.org/) for a standardized commit history.
    *   `feat: add support for Twitter DM parsing`
    *   `fix: resolve GUI crash on long text input`
    *   `docs: update installation instructions for Windows`
    *   `data: add new labeled dataset for Telegram scams`
8.  **Push to your fork** and [submit a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to our `main` branch.
9.  **Wait for review.** The team leader and other contributors will review your PR. Please be responsive to any requested changes.

## 🧪 Testing

Before submitting a PR, please test your changes:
*   Run the desktop GUI and verify it launches without errors.
*   Test the core `predictor.py` module with sample text to ensure it returns expected results.
*   If you've modified the model or preprocessing, run the training notebooks to ensure accuracy is maintained or improved.

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to `[team.lead@email.com]`.

## ❓ Questions?

Feel free to open an issue with your question or contact the development team lead directly at `[team.lead@email.com]`.

Thank you for your contribution! 🙏