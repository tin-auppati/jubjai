CREATE TABLE "users" (
  "id" integer PRIMARY KEY,
  "email" varchar UNIQUE,
  "password_hash" varchar,
  "full_name" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
);

CREATE TABLE "categories" (
  "category_id" integer PRIMARY KEY,
  "user_id" integer,
  "name" varchar,
  "description" varchar,
  "monthly_limit" numeric(10,2),
  "is_deleted" boolean DEFAULT false,
  "created_at" timestamp,
  "updated_at" timestamp
);

CREATE TABLE "expenses" (
  "expense_id" integer PRIMARY KEY,
  "user_id" integer,
  "category_id" integer,
  "expense_date" date,
  "amount" numeric(10,2),
  "description" varchar,
  "entry_method" varchar,
  "slip_image_url" varchar,
  "is_deleted" boolean DEFAULT false,
  "created_at" timestamp,
  "updated_at" timestamp
);

COMMENT ON COLUMN "users"."email" IS 'User email for login';

COMMENT ON COLUMN "users"."password_hash" IS 'Hashed password';

COMMENT ON COLUMN "categories"."is_deleted" IS 'Soft delete flag';

COMMENT ON COLUMN "expenses"."entry_method" IS 'Entry method: manual or slip';

COMMENT ON COLUMN "expenses"."is_deleted" IS 'Soft delete flag';

ALTER TABLE "categories" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "expenses" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "expenses" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("category_id");
