# Fentry Auto Crate 

This repository contains a pre-configured script and GitHub Actions workflow to automatically claim your free "Regular Crate" on fentry.org. To use it, you will first need to create your own copy (**fork**) of this repository.

---

## How It Works

The GitHub Actions workflow in this repository is scheduled to run automatically every hour. It sets up a Python environment and executes the `main.py` script. The script uses a session cookie, which you will provide, to securely log in to your Fentry account and claim the crate if it's available.

---
## Setup and Configuration

Follow these three steps to get the automation running.

### Step 1: Fork This Repository

First, you need to create a personal copy of this repository under your own GitHub account.

Click the **Fork** button at the top-right of this page. This will give you your own version of the code where you can enable GitHub Actions and add your own secure credentials.



### Step 2: Get Your Fentry Session Cookie

Next, you need to get the session cookie that the script will use to authenticate.

1.  Navigate to your Fentry dashboard at **`https://www.fentry.org/dashboard`** in your browser. If you aren't logged in, log in with your Discord account as you normally would.
2.  Once you are on your dashboard, press `F12` to open **Developer Tools**.
3.  Navigate to the **Application** tab.
4.  On the left-hand menu, expand the **Cookies** section and click on the URL for `https://www.fentry.org`.
5.  In the table of cookies, find the one with the name **`connect.sid`**.
6.  Click on it and copy the entire long string from the **"Value"** field. This is your personal session token.

### Step 3: Add the Cookie to GitHub Secrets

Finally, you must store this cookie securely in your forked repository's secrets.

1.  In **your forked repository**, go to **Settings** > **Secrets and variables** > **Actions**.
2.  Click the **New repository secret** button.
3.  For the **Name**, enter exactly:
    `FENTRY_SESSION_COOKIE`
4.  For the **Value**, paste the long cookie value you copied in the previous step.
5.  Click **Add secret**.

---
## Usage

Once the configuration is complete, the automation is active.

* **Automatic Runs**: The script is scheduled to run every 6 hours. It will automatically claim the crate if the cooldown has ended.
* **Manual Runs**: You can test the setup by manually triggering the script. Go to the **Actions** tab in your repository, select "Fentry Crate Claimer" from the sidebar, and click the "Run workflow" button.

### Troubleshooting

If a workflow run fails with a `Login failed!` error, it most likely means your session cookie has expired. To fix this, simply repeat **Step 2** and **Step 3** to get a fresh cookie and update the `FENTRY_SESSION_COOKIE` secret in your repository.
