CREATE TABLE IF NOT EXISTS `favorite` (
  `favorite_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `user_id` INTEGER NOT NULL,
  `song_id` INTEGER NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `song` (
  `song_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `song_name` TEXT NOT NULL,
  `song_url`  TEXT NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `guild` (
  `guild_id` INTEGER NOT NULL PRIMARY KEY,
  `guild_name` TEXT NOT NULL,
  `owner_id` INTEGER NOT NULL,
  `owner_name` TEXT NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `guild_members` (
  `guild_id` INTEGER NOT NULL,
  `user_id`  INTEGER NOT NULL,
  PRIMARY KEY (`guild_id`, `user_id`)
);

CREATE TABLE IF NOT EXISTS `guild_settings` (
  `guild_id` INTEGER NOT NULL,
  `setting_type` TEXT NOT NULL,
  `setting_value` TEXT NOT NULL,
  PRIMARY KEY (`guild_id`, `user_id`)
);