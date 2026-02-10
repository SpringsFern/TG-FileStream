# TG-FileStream

> This project is released under the **GNU AGPL v3** license.  
> You are free to use, modify, and distribute it — as long as you share your changes under the same license.

**TG-FileStream** is a lightweight web server and Telegram client that acts as a proxy between Telegram servers and HTTP clients, allowing direct downloads of Telegram media files via HTTP.

> 📌 Check out [TODO.md](./TODO.md) for the latest development progress and planned features.

---

## 📝 Notes

- If you want one without database checkout [DeekshithSH/tgfilestream](https://github.com/DeekshithSH/tgfilestream) or [simple branch](https://github.com/SpringsFern/TG-FileStream/tree/simple)

---

## 🚀 Features

- Download Telegram media via HTTP links
- Fast, concurrent chunked downloading

---

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/SpringsFern/TG-FileStream.git
cd TG-FileStream
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Store the required environment variables in a `.env` file:

```env
API_ID=1234567
API_HASH=1a2b3c4d5e6f7g8h9i0jklmnopqrstuv
BOT_TOKEN=1234567890:AAExampleBotTokenGeneratedHere
BIN_CHANNEL=-1002605638795
HOST=0.0.0.0
PORT=8080
PUBLIC_URL=http://127.0.0.1:8080
DB_BACKEND=mongodb
MONGODB_URI=mongodb://admin:pAswaRd@192.168.27.1
```

### 4. Run the server

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
| `DB_BACKEND`         | ✅                     | Which Database server to use. either `mongodb` or `mysql`                    |
| `HOST`               | `0.0.0.0`              | Host address to bind the server (default: `0.0.0.0`)                         |
| `PORT`               | `8080`                 | Port to run the server on (default: `8080`)                                  |
| `PUBLIC_URL`         | `https://0.0.0.0:8080` | Public-facing URL used to generate download links                            |
| `DEBUG`              | `False`                | Show Extra Logs                                                              |
| `CONNECTION_LIMIT`   | `5`                    | Number of connections to create per DC for a single client                   |
| `DOWNLOAD_PART_SIZE` | `1048576 (1MB)`        | Number of bytes to request in a single chunk                                 |
| `NO_UPDATE`          | `False`                | Whether to reply to messages sent to the bot (True to disable replies)       |
| `SEQUENTIAL_UPDATES` | `False`                | Handle telegram updates sequentially                                         |
| `FILE_INDEX_LIMIT`   | `10`                   | Number of files to display at once with `/files` command                     |
| `MAX_WARNS`          | `3`                    | Maximum number of warns before user get banned                               |
| `ADMIN_IDS`          | `None`                 | User id of users who can use admin commands. Each id is seperated by `,`     |
| `ALLOWED_IDS`        | `None`                 | Only users with these IDs can use the bot. Separate multiple IDs with `,`    |


### Multi Token Environment Variables
| Variable       | Required/Default | Description                                                                  |
| -------------- | ---------------- | ---------------------------------------------------------------------------- |
| `MULTI_TOKENx` | ✅               | Use Multiple Telegram Clients when downloading files to avoid flood wait, Replace x with Number |
|                |                  | Example: |
| `MULTI_TOKEN1` |                  | MULTI_TOKEN1=1234567890:AAExampleBotTokenGeneratedHere|
| `MULTI_TOKEN2` |                  | MULTI_TOKEN2=0987654321:AAExampleBotTokenGeneratedHere|
| `MULTI_TOKEN3` |                  | MULTI_TOKEN3=5432167890:AAExampleBotTokenGeneratedHere|

### MySQL Environment Variables
Set the following variables if you choose MySQL as the database in `DB_BACKEND`

| Variable         | Required/Default | Description                                |
| ---------------- | ---------------- | ------------------------------------------ |
| `MYSQL_HOST`     | ✅               | MySQL DataBase Host Name                   |
| `MYSQL_PORT`     | ✅               | MySQL Database Port Number                 |
| `MYSQL_USER`     | ✅               | MySQL Database Username                    |
| `MYSQL_PASSWORD` | ✅               | MySQL Database Password                    |
| `MYSQL_DB`       | ✅               | MySQL Database Name                        |
| `MYSQL_MINSIZE`  | `1`              | Minimum sizes of the MySQL Connection pool |
| `MYSQL_MAXSIZE`  | `5`              | Maximum sizes of the MySQL Connection pool |

### MongoDB Environment Variables
Set the following variables if you choose MongoDB as the database in `DB_BACKEND`

| Variable         | Required/Default | Description           |
| ---------------- | ---------------- | --------------------- |
| `MONGODB_URI`    | ✅               | MongoDB Database URI  |
| `MONGODB_DBNAME` | `TGFS`           | MongoDB Database name |

---

## 📂 Usage

Once the server is running, you can:

- Access Telegram media files via HTTP:

- Or simply send a file to your bot, and it will respond with a download link.

This will stream the file directly from Telegram servers to the client.

---

## 🛠️ Contributing & Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/SpringsFern/TG-FileStream/issues) on GitHub.

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
`[Feature] Add support for viewing generated links`

---

Contributions are welcome!  
Feel free to fork the project and open a pull request.

> 🔍 **Note:** Make sure to test your code thoroughly before submitting a PR to help maintain stability and performance.

---

## 💡 Credits

- **Deekshith SH** – Me
- **Tulir** – Original author of [`tgfilestream`](https://github.com/tulir/tgfilestream), whose code inspired this project and is referenced in `paralleltransfer.py`

---
