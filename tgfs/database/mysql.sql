CREATE TABLE IF NOT EXISTS FILE (
    id BIGINT PRIMARY KEY,
    dc_id INT NOT NULL,
    size BIGINT NOT NULL,
    mime_type TEXT,
    file_name TEXT,
    thumb_size VARCHAR(10),
    is_deleted BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS FILE_LOCATION (
  bot_id BIGINT NOT NULL,
  id BIGINT NOT NULL,
  access_hash BIGINT NULL,
  file_reference BLOB NULL,
  PRIMARY KEY (bot_id, id),
  UNIQUE KEY uniq_bot_file (bot_id, id),
  CONSTRAINT fk_file_ids_files FOREIGN KEY (id) REFERENCES files(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX file_ids_file_idx ON file_ids (id);
CREATE INDEX file_ids_bot_idx  ON file_ids (bot_id);

CREATE TABLE IF NOT EXISTS USER (
    user_id BIGINT PRIMARY KEY,
    join_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ban_date DATETIME NULL,
    warns TINYINT NOT NULL DEFAULT 0,
    preferred_lang CHAR(2) NOT NULL DEFAULT 'en'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS USER_FILE (
  user_id BIGINT NOT NULL,
  id BIGINT NOT NULL,
  source_chat_id BIGINT NULL,
  source_msg_id BIGINT NULL,
  added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, id),
  CONSTRAINT fk_user_files_users FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_user_files_files FOREIGN KEY (id) REFERENCES files(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX user_files_file_idx ON user_files (id);
CREATE INDEX user_files_user_idx ON user_files (user_id);