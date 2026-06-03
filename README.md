# Instagram DM & Comment Automation

This repository contains the source code for a Server-to-Server automation developed for the Instagram business account @casa__curadoria. The application's goal is to convert public engagement (comments) into private interactions and conversions by automatically sending product links (e.g., Shopee affiliates) via Direct Message (DM), while simultaneously publishing randomized public replies when a follower comments a specific keyword.

Real-time data ingestion pipeline construction consuming the Meta Graph API. Server-to-Server architecture deployed in the cloud (Render).

## ⚙️ Architecture and Technologies

The project was built without a graphical interface (*Front-end*), running 100% on the *Back-end*, using the following tools:

* **Hosting:** [Render.com](https://render.com/) (PaaS)
* **Database/Configuration:** Google Sheets API
* **Integration:** Meta Graph API (Instagram Webhooks)
* **Language/Environment:** Python

## 🔄 Workflow (How it works)

The entire process is automated and occurs in a matter of seconds:

1.  **The Trigger (Consent):** The page publishes a "finds" post and asks in the caption for the follower to comment a keyword (e.g., *"WANT"*).
2.  **The Webhook:** The user comments on the post. The Meta Graph API detects the interaction and triggers an event (Webhook) containing the comment's *payload* to our server hosted on Render.
3.  **Processing and Validation:** The server receives the Webhook and verifies:
    * If the event occurred on the correct account (`instagram_business_basic`).
    * If the comment text contains the exact trigger keyword (`instagram_business_manage_comments`).
4.  **Database Query:** The code connects to a Google Sheets spreadsheet. The spreadsheet works as a control panel containing: `Post Link` | `Keyword` | `Message to send` | `Product Link (Shopee)`.
5. **The Action (DM Dispatch & Public Reply):** Once the data matches, the server makes two parallel POST requests to the Meta Graph API:
  - **Private DM:** Uses the comment_id to send the link directly to the user's inbox (complying with Meta's Private Reply policies).
  - **Public Reply:** Randomly selects a phrase from the spreadsheet (e.g., "Just sent it to your DM, @{username}! ✨") and replies to the user's comment. This mimics human behavior, prevents SPAM flagging, and doubles the post's algorithmic engagement.

## 🔐 Meta App Permissions

For the bot to work, the application in the Meta Developer Dashboard requires the **Advanced Access** level for the following permissions:

* `instagram_business_basic`: To read profile metadata and validate the comment's origin.
* `instagram_business_manage_comments`: To passively listen to Webhooks and identify the keyword.
* `instagram_business_manage_messages`: To execute the automated DM dispatch.

> **Note on Meta's review:** Since this is a *Server-to-Server* application, the authentication flow does not use login screens (*Facebook Login*). Authorization is done via **System User Access Tokens** generated in the Business Manager and configured in the server's environment variables.

## 🚀 Environment Setup

To run this project locally or on a new server, the following environment variables (`.env`) must be configured:

* `VERIFY_TOKEN`: Security token for Webhook validation on Meta.
* `PAGE_ACCESS_TOKEN` or `SYSTEM_USER_TOKEN`: Access token with permission to manage the linked Instagram account.
* `GOOGLE_SHEETS_CREDENTIALS`: JSON containing the Google Cloud API credentials.
* `SPREADSHEET_ID`: The ID of the Google Sheets spreadsheet used as a database.

## 🎥 Project Demonstration

Click the image below to watch the video demonstrating the Server-to-Server architecture working in real-time, from the webhook to the message delivery on Instagram:

[![Automation Demonstration](https://img.youtube.com/vi/OATuXX8J230/0.jpg)](https://www.youtube.com/watch?v=OATuXX8J230)

## 📌 Final Remarks

This project automates the delivery of value to followers, reducing friction in the purchasing journey and ensuring the user receives the requested information instantly and securely. By implementing randomized public replies and offloading configuration to Google Sheets, the architecture empowers content teams to manage campaigns without touching the codebase, all while respecting the platform's privacy and consent policies.
