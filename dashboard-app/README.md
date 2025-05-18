# Energy Delivery Forecasting App

This Streamlit application forecasts energy delivery for the next three months based on a time series model. It allows users to upload their data, view historical trends, and see the generated forecast.

## Setting up the Environment

It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts.

**Using standard Python's `venv`:**

1.  **Create a virtual environment** (e.g., named `.venv`) in the `dashboard-app` directory:
    ```bash
    python -m venv .venv
    ```
2.  **Activate the virtual environment**:
    *   On macOS and Linux (including WSL):
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows (Command Prompt):
        ```bash
        .venv\\Scripts\\activate.bat
        ```
    *   On Windows (PowerShell):
        ```powershell
        .venv\\Scripts\\Activate.ps1
        ```
    Your terminal prompt should change to indicate the active environment.

## Running the Application Locally

To run this application on your local machine, follow these steps:

1.  **Activate your virtual environment** if you haven't already (see "Setting up the Environment" above).
2.  **Navigate to the application directory**:
    ```bash
    cd path/to/your/dashboard-app 
    ```
3.  **Install Dependencies**: With your virtual environment activated, and inside the `dashboard-app` directory, run the following command to install the required packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Application**: Once the dependencies are installed, you can start the Streamlit application by running:
    ```bash
    streamlit run app.py
    ```
    This will typically open the application in your default web browser.

### Troubleshooting

**`ModuleNotFoundError: No module named 'streamlit.cli'` or similar import errors:**

*   **Ensure your virtual environment is activated**: This is the most common cause. The `streamlit` command must be run from within the environment where it (and its dependencies) were installed. Check your terminal prompt.
*   **Reinstall Streamlit and dependencies**: If you are sure the correct environment is active, Streamlit or its dependencies might have had an issue during installation. Try reinstalling them within the active environment:
    1.  Deactivate and reactivate your environment to be sure.
    2.  Then, run:
        ```bash
        pip uninstall streamlit -y
        pip install -r requirements.txt
        ```
*   **Check Python and Pip versions**: Ensure `python --version` and `pip --version` point to the versions within your activated virtual environment.
*   **PATH issues (less common)**: In rare cases, your system's `PATH` environment variable might be misconfigured. Ensure that the scripts directory of your active Python environment (e.g., `myenv/bin` or `.venv/bin`) is correctly prioritized in your `PATH`.
