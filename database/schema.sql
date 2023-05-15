CREATE TABLE IF NOT EXISTS `song` (
  `song_id` BLOB NOT NULL PRIMARY KEY,
  `song_name` TEXT NOT NULL,
  `song_url`  TEXT NOT NULL,
  `added_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `playlist` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `guild_user_id` INTEGER NOT NULL,
  `playlist_name` TEXT NOT NULL,
  FOREIGN KEY(`guild_user_id`) REFERENCES `guild_user` (`id`),
  UNIQUE (`guild_user_id`, `playlist_name`)
);

CREATE TABLE IF NOT EXISTS `playlist_songs` (
  `favorite_id` INTEGER NOT NULL,
  `playlist_id` INTEGER NOT NULL,
  FOREIGN KEY(`favorite_id`) REFERENCES `favorite` (`guild_user_id`, `song_id`),
  FOREIGN KEY(`playlist_id`) REFERENCES `playlist` (`id`)
  PRIMARY KEY (`favorite_id`, `playlist_id`)
);

CREATE TABLE IF NOT EXISTS `favorite` (
  `guild_user_id` INTEGER NOT NULL,
  `song_id` BLOB NOT NULL,
  FOREIGN KEY(`song_id`) REFERENCES `song` (`song_id`),
  FOREIGN KEY(`guild_user_id`) REFERENCES `guild_user` (`id`),
  PRIMARY KEY (`guild_user_id`, `song_id`)
);

CREATE TABLE IF NOT EXISTS `guild_user` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `guild_id` INTEGER NOT NULL,
  `user_id`  INTEGER NOT NULL,
  UNIQUE (`guild_id`, `user_id`)
);

CREATE TABLE IF NOT EXISTS `guild_settings` (
  `guild_id` INTEGER NOT NULL,
  `setting_type` TEXT NOT NULL,
  `setting_value` TEXT NOT NULL,
  PRIMARY KEY (`guild_id`, `setting_type`)
);

CREATE TABLE IF NOT EXISTS `blacklist` (
  `guild_user_id` INTEGER NOT NULL,
  FOREIGN KEY(`guild_user_id`) REFERENCES `guild_user` (`id`),
  PRIMARY KEY (`guild_user_id`)
);

CREATE TABLE IF NOT EXISTS `whitelist` (
  `guild_user_id` INTEGER NOT NULL,
  FOREIGN KEY(`guild_user_id`) REFERENCES `guild_user` (`id`),
  PRIMARY KEY (`guild_user_id`)
);