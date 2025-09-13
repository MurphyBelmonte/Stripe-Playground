# Financial Command Center AI

The Financial Command Center AI is a professional, self-hosted financial operations platform designed for security, reliability, and ease of use. It provides a unified interface for managing financial tasks, including payment processing and accounting, through integrations with Stripe and Xero.

The platform features a one-click launcher for Windows, automatic HTTPS setup, and a secure setup wizard to manage API credentials, ensuring that your financial data is always protected.

---

## Core Features

-   **One-Click Launcher**: A simple, no-fuss Windows launcher that sets up a virtual environment, installs dependencies, and starts the server.
-   **Secure by Default**: Automatic SSL certificate generation and HTTPS for all connections.
-   **Setup Wizard**: A professional, user-friendly wizard to securely configure your Stripe and Xero credentials. No more plain-text API keys in `.env` files.
-   **Stripe Integration**: Process payments and manage subscriptions with Stripe.
-   **Xero Integration**: Sync invoices, contacts, and other financial data with Xero.
-   **Admin Dashboard**: A comprehensive dashboard to monitor system status, manage API keys, and view recent activity.
-   **Demo Mode**: Run the application without real credentials to explore its features.

---

## How It Works

### 1. One-Click Launch

Simply run the `Financial-Command-Center-Launcher.exe` located in the `installer_package` directory. The launcher handles all the setup for you:

-   Creates a dedicated Python virtual environment.
-   Installs all necessary dependencies.
-   Generates SSL certificates for secure HTTPS.
-   Starts the web server.
-   Opens the application in your default web browser.

### 2. Secure Setup Wizard

On the first run, you will be guided through the Setup Wizard to configure your integrations.

-   **Stripe**: Enter your Stripe API key to enable payment processing.
-   **Xero**: Enter your Xero Client ID and Client Secret to enable accounting sync.
-   **Skip for Demo**: You can skip any integration to use the application in demo mode.

All credentials are encrypted and stored securely on your local machine.

### 3. Financial Command Center Dashboard

Once configured, the main dashboard provides a central hub for your financial operations.

-   **View Contacts and Invoices**: If you have connected to Xero, you can directly view your contacts and invoices.
-   **Admin Dashboard**: Access the admin dashboard to manage API keys and monitor system health.
-   **Reconfigure**: You can re-run the setup wizard at any time to update your credentials.

---

## Getting Started (from Source)

If you prefer to run the application from the source code:

1.  **Prerequisites**: Ensure you have Python 3.10+ and `pip` installed.
2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/Financial-Command-Center-AI.git
    cd Financial-Command-Center-AI
    ```
3.  **Run the launcher with the setup flag**:
    ```bash
    python financial_launcher.py --setup
    ```

The launcher will perform the same setup steps as the one-click executable.

---

## Configuration

The application can be configured with environment variables:

-   `FCC_PORT`: Set the preferred port for the web server (default: `8000`).
-   `FORCE_HTTPS`: Set to `true` to enforce HTTPS (default: `true`).
-   `ALLOW_HTTP`: Set to `true` to allow HTTP (default: `false`).

---

## Key Endpoints

-   **Home / Setup**: `https://localhost:<port>/`
-   **Admin Dashboard**: `https://localhost:<port>/admin/dashboard`
-   **Health Check**: `https://localhost:<port>/health`
-   **SSL Help**: `https://localhost:<port>/admin/ssl-help`

---

## Building the Launcher (for Contributors)

To build the `Financial-Command-Center-Launcher.exe` yourself:

1.  **Install PyInstaller**:
    ```bash
    pip install pyinstaller
    ```
2.  **Run the build script**:
    ```powershell
    python build_launcher.py
    ```

The output will be in the `dist` and `installer_package` directories.