CREATE TABLE "users" (
  "id" int PRIMARY KEY,
  "email" varchar UNIQUE,
  "name" varchar,
  "password" varchar,
  "avatar_url" varchar(300),
  "date_created" datetime,
  "date_updated" datetime,
  "is_deleted" boolean,
  "is_admin" boolean
);

CREATE TABLE "categories" (
  "category_id" int PRIMARY KEY,
  "user_id" int,
  "name" varchar,
  "description" varchar,
  "icon_url" varchar,
  "limit" numeric(10,2),
  "transaction_type" enum(income,expense),
  "limit_start_date" date,
  "limit_end_date" date,
  "is_deleted" boolean,
  "date_created" datetime,
  "date_updated" datetime
);

CREATE TABLE "transactions" (
  "transaction_id" int PRIMARY KEY,
  "user_id" int,
  "category_id" int,
  "transaction_date" date,
  "amount" numeric(10,2),
  "description" varchar,
  "transaction_type" enum(income,expense),
  "entry_method" enum(manual,slip),
  "slip_image_url" varchar,
  "is_deleted" boolean,
  "date_created" datetime,
  "date_updated" datetime
);

ALTER TABLE "categories" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("category_id");
