# Project Brief: Automated Video Upload Bot to Rumble via Telegram

Build a Telegram bot that receives videos from users, generates random titles/descriptions if none are provided, and automates full uploads to Rumble (including checkboxes and submission) using browser simulation for reliability. Host it on a cloud platform like Heroku or AWS for faster internet, leveraging open-source Python tools to keep costs low.

### Key Steps Summarized
- **Telegram Integration**: Bot downloads video via Telegram API; uses provided or random-generated metadata.
- **Rumble Upload**: Automate via Selenium (no direct public API for uploads), simulating login, file selection, form filling, checkbox ticking, and submission.
- **Hosting**: Deploy on free/cheap cloud (e.g., Heroku) for 24/7 speed; add error handling and notifications.
- **Tech Stack**: Python with `telebot`, `selenium`, `faker` (for random text); ensure compliance with platform terms to avoid bans.

### Developer Prompt
You are tasked with building an open-source Python-based Telegram bot for automated video uploads to Rumble. The bot should:

1. **Receive Input**: Listen for messages in a Telegram chat/channel via the Telegram Bot API (use `telebot` library). When a video file is sent, download it automatically (handle files up to 2GB). Extract any provided title, description, tags from the message text; if missing, generate random ones using `faker` (e.g., title like "Random Upload #XYZ", description as a short placeholder paragraph).

2. **Automate Rumble Upload**: Since Rumble lacks a public API for direct video uploads, use Selenium with ChromeDriver to simulate the manual process on rumble.com:
   - Log in to a predefined Rumble account (store credentials securely, e.g., via environment variables).
   - Navigate to the upload page.
   - Upload the downloaded video file.
   - Fill in title, description, tags, and other fields.
   - Automatically check all required checkboxes (e.g., terms, ownership).
   - Submit and wait for upload/processing confirmation (poll for status if needed).
   - Handle errors like upload failures with retries and log them.

3. **Workflow**: After receiving the video, process it immediately, upload to Rumble, and send a Telegram notification to the user with success/failure details (e.g., link to uploaded video).

4. **Hosting and Optimization**: Deploy the bot on a cloud platform for high-speed internet (e.g.,Render, koyed), even keep an options for local or vps hosting. Use webhooks for efficient Telegram polling. Add delays in Selenium to mimic human behavior and avoid detection/bans. Keep it cost-optimized: no unnecessary dependencies, monitor usage.

5. **Additional Features**: Include basic error handling (e.g., invalid files, network issues), logging, and compliance checks (ensure generated metadata follows Rumble's rules). Make it configurable via env vars (e.g., Telegram token, Rumble credentials). Test thoroughly with small videos first.

Provide the full source code on GitHub, with setup instructions. Budget: Aim for zero-cost deployment initially. If issues with Selenium arise, explore Pipedream for API wrappers as a fallback.

