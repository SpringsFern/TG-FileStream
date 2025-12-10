# TG-FileStream

> This project is released under the **GNU AGPL v3** license.  
> You are free to use, modify, and distribute it — as long as you share your changes under the same license.

**TG-FileStream** is a lightweight web server and Telegram client that acts as a proxy between Telegram servers and HTTP clients, allowing direct downloads of Telegram media files via HTTP.

---

## 🔁 Project Background

This project is a **successor** to  
👉 [DeekshithSH/TG-FileStreamBot](https://github.com/DeekshithSH/TG-FileStreamBot),  
which itself was a fork of  
👉 [EverythingSuckz/TG-FileStreamBot](https://github.com/EverythingSuckz/TG-FileStreamBot).

The original Python version became inactive after EverythingSuckz rewrote the project in Golang. Instead of continuing from the older Python codebase, this project is a fresh rewrite using [Telethon](https://github.com/LonamiWebs/Telethon) with a minimal approach.

> 📌 Check out [TODO.md](./TODO.md) for the latest development progress and planned features.

---

## 🚀 Features

- Download Telegram media via HTTP links  
- Fast, concurrent chunked downloading  
- Minimal setup, no database required

---

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/DeekshithSH/TG-FileStream.git
cd TG-FileStream
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create/Import Database

Import SQL file located in `tgfs/database/mysql.sql`

### 4. Create a `.env` file

Store the required environment variables in a `.env` file:

```env
API_ID=1234567
API_HASH=1a2b3c4d5e6f7g8h9i0jklmnopqrstuv
BOT_TOKEN=1234567890:AAExampleBotTokenGeneratedHere
BIN_CHANNEL=-1002605638795
HOST=0.0.0.0
PORT=8080
PUBLIC_URL=http://127.0.0.1:8080
DB_HOST=localhost
DB_USER=root
DB_PASS=root
DB_NAME=FTL
```

### 5. Run the server

```bash
python3 -m tgfs
```

---

## ⚙️ Environment Variables

| Variable             | Required/Default       | Description                                                                  |
| -------------------- | ---------------------- | ---------------------------------------------------------------------------- |
| `API_ID`             | ✅                     | App ID from [my.telegram.org](https://my.telegram.org)                       |
| `API_HASH`           | ✅                     | API hash from [my.telegram.org](https://my.telegram.org)                     |
| `BOT_TOKEN`          | ✅                     | Bot token from [@BotFather](https://t.me/BotFather)                          |
| `BIN_CHANNEL`        | ✅                     | Channel ID where files sent to the bot are stored                            |
| `HOST`               | `0.0.0.0`              | Host address to bind the server (default: `0.0.0.0`)                         |
| `PORT`               | `8080`                 | Port to run the server on (default: `8080`)                                  |
| `PUBLIC_URL`         | `https://0.0.0.0:8080` | Public-facing URL used to generate download links                            |
| `CONNECTION_LIMIT`   | `20`                   | Number of connections to create per DC for a single client                   |
| `CACHE_SIZE`         | `128`                  | Number of file info objects to cache                                         |
| `DOWNLOAD_PART_SIZE` | `1048576 (1MB)`        | Number of bytes to request in a single chunk                                 |
| `NO_UPDATE`          | `False`                | Whether to reply to messages sent to the bot (True to disable replies)       |
| `DB_HOST`            | ✅                     | Database Host Name                                                           |
| `DB_USER`            | ✅                     | Database User Name                                                           |
| `DB_PASS`            | ✅                     | Database Password                                                            |
| `DB_NAME`            | ✅                     | Database Name                                                                |



- `MULTI_TOKENx`: Use Multiple Telegram Clients when downloading files to avoid flood wait, Replace x with Number

example:
```
MULTI_TOKEN1=1234567890:AAExampleBotTokenGeneratedHere
MULTI_TOKEN2=0987654321:AAExampleBotTokenGeneratedHere
MULTI_TOKEN3=5432167890:AAExampleBotTokenGeneratedHere
```

---

## 📂 Usage

Once the server is running, you can:

- Access Telegram media files via HTTP:

```
http://{PUBLIC_URL}/{message_id}/{filename}
```

- Or simply send a file to your bot, and it will respond with a download link.

This will stream the file directly from Telegram servers to the client.

---

## 🛠️ Contributing & Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/DeekshithSH/TG-FileStream/issues) on GitHub.

### 🐞 Reporting Issues
When reporting a bug, **please include**:
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Relevant logs, screenshots, or error messages (if any)
- Environment details (OS, Python version, etc.)

**Example issue title:**  
`[Bug] Download fails for large files`

### 💡 Requesting Features
When suggesting a new feature, **please include**:
- A clear and concise description of the feature
- The motivation or use case for it
- Expected behavior (input/output examples if applicable)
- Any alternatives you've considered

**Example feature title:**  
`[Feature] Add support for download progress feedback`

---

Contributions are welcome!  
Feel free to fork the project and open a pull request.

> 🔍 **Note:** Make sure to test your code thoroughly before submitting a PR to help maintain stability and performance.

---

## 💡 Credits

- **Deekshith SH** – Me
- **Tulir** – Original author of [`tgfilestream`](https://github.com/tulir/tgfilestream), whose code inspired this project and is referenced in `paralleltransfer.py`

---
