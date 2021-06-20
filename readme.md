
# DB

skyticket needs a mysql db and any engine works..
these are the tables it needs
### these are needed to MADE BY THE USER, skyticket can't make them on it's own

```sql
CREATE TABLE `ign` (
  `user_id` bigint(20) DEFAULT NULL,
  `ign` varchar(16) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `Panel` (
  `name` varchar(100) DEFAULT NULL,
  `ticket_prefix` varchar(50) DEFAULT NULL,
  `ticket_category` bigint(20) DEFAULT NULL,
  `msg_id` bigint(20) DEFAULT NULL,
  `ticket_number` smallint(6) DEFAULT NULL,
  `msg_text` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Tickets` (
  `user_id` bigint(20) DEFAULT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `claim_id` varchar(18) DEFAULT NULL,
  `is_closed` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```


# ENV
## these should be put in the .env files
`DISCORD_TOKEN` - token of the discord bot
`db_host` - host url of the db
`db_name` - name of the db
`db_user` - username of the db user
`db_password` - password of the db user
`db_port` - port for the db
`hypixel_api_key` - key for the hypixel api (for verifying igns)
`path` - absolute path for the folder where main.py is stored
