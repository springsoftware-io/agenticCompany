# PostgreSQL Documentation

**Official Docs:** https://www.postgresql.org/docs/

## Overview
PostgreSQL is a powerful, open-source relational database. We use it with Cloud SQL for the Seed Planter API.

## Key Features
- ACID compliance
- Complex queries and joins
- JSON/JSONB support
- Full-text search
- Transactions and concurrency
- Extensible with custom functions

## Connection

### Connection String
```python
DATABASE_URL = "postgresql://user:password@host:port/database"

# Cloud SQL Unix socket
DATABASE_URL = "postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE"
```

### psycopg2 (Python)
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="myuser",
    password="mypassword"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
```

## Basic SQL Operations

### Create Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Insert Data
```sql
INSERT INTO users (username, email) 
VALUES ('john_doe', 'john@example.com');

-- Multiple rows
INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com');
```

### Query Data
```sql
-- Select all
SELECT * FROM users;

-- With conditions
SELECT * FROM users WHERE username = 'john_doe';

-- With ordering
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- With joins
SELECT u.username, o.order_id 
FROM users u
JOIN orders o ON u.id = o.user_id;
```

### Update Data
```sql
UPDATE users 
SET email = 'newemail@example.com' 
WHERE username = 'john_doe';
```

### Delete Data
```sql
DELETE FROM users WHERE id = 5;
```

## Data Types

### Common Types
```sql
-- Numbers
INTEGER, BIGINT, SERIAL, BIGSERIAL
NUMERIC(10,2), DECIMAL
REAL, DOUBLE PRECISION

-- Text
VARCHAR(n), TEXT, CHAR(n)

-- Date/Time
DATE, TIME, TIMESTAMP, TIMESTAMPTZ

-- Boolean
BOOLEAN

-- JSON
JSON, JSONB

-- Arrays
INTEGER[], TEXT[]

-- UUID
UUID
```

## Indexes

### Create Index
```sql
-- Simple index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Composite index
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial index
CREATE INDEX idx_active_users ON users(email) WHERE active = true;
```

### Drop Index
```sql
DROP INDEX idx_users_email;
```

## Constraints

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total NUMERIC(10,2) CHECK (total >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, created_at)
);
```

## Transactions

```sql
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Rollback on error
BEGIN;
    -- operations
ROLLBACK;
```

## JSON Operations

### JSONB Column
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    attributes JSONB
);

INSERT INTO products (name, attributes) VALUES
    ('Laptop', '{"brand": "Dell", "ram": 16, "storage": 512}');
```

### Query JSON
```sql
-- Get JSON field
SELECT attributes->>'brand' FROM products;

-- Filter by JSON field
SELECT * FROM products WHERE attributes->>'brand' = 'Dell';

-- Check JSON key exists
SELECT * FROM products WHERE attributes ? 'ram';

-- Query nested JSON
SELECT * FROM products WHERE attributes->'specs'->>'cpu' = 'Intel';
```

## Full-Text Search

```sql
-- Add tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Update search vector
UPDATE articles 
SET search_vector = to_tsvector('english', title || ' ' || content);

-- Create index
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

-- Search
SELECT * FROM articles 
WHERE search_vector @@ to_tsquery('english', 'postgresql & database');
```

## Common Functions

### String Functions
```sql
SELECT CONCAT(first_name, ' ', last_name) FROM users;
SELECT UPPER(username) FROM users;
SELECT LENGTH(email) FROM users;
SELECT SUBSTRING(email FROM 1 FOR 5) FROM users;
```

### Date Functions
```sql
SELECT NOW();
SELECT CURRENT_DATE;
SELECT CURRENT_TIMESTAMP;
SELECT AGE(birth_date) FROM users;
SELECT EXTRACT(YEAR FROM created_at) FROM orders;
```

### Aggregate Functions
```sql
SELECT COUNT(*) FROM users;
SELECT AVG(price) FROM products;
SELECT SUM(total) FROM orders;
SELECT MAX(created_at) FROM users;
SELECT MIN(price) FROM products;
```

## Window Functions

```sql
-- Row number
SELECT username, 
       ROW_NUMBER() OVER (ORDER BY created_at) as row_num
FROM users;

-- Rank
SELECT product_name, price,
       RANK() OVER (ORDER BY price DESC) as price_rank
FROM products;

-- Running total
SELECT date, amount,
       SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;
```

## Views

```sql
-- Create view
CREATE VIEW active_users AS
SELECT * FROM users WHERE active = true;

-- Use view
SELECT * FROM active_users;

-- Drop view
DROP VIEW active_users;
```

## Performance Optimization

### EXPLAIN
```sql
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1;
```

### Vacuum
```sql
-- Regular vacuum
VACUUM;

-- Full vacuum
VACUUM FULL;

-- Analyze statistics
ANALYZE;
```

## Backup & Restore

### Backup
```bash
# Dump database
pg_dump dbname > backup.sql

# Dump with compression
pg_dump dbname | gzip > backup.sql.gz

# Dump specific table
pg_dump -t users dbname > users_backup.sql
```

### Restore
```bash
# Restore database
psql dbname < backup.sql

# Restore compressed
gunzip -c backup.sql.gz | psql dbname
```

## User Management

```sql
-- Create user
CREATE USER myuser WITH PASSWORD 'mypassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
GRANT SELECT, INSERT ON users TO myuser;

-- Revoke privileges
REVOKE INSERT ON users FROM myuser;

-- Change password
ALTER USER myuser WITH PASSWORD 'newpassword';
```

## Best Practices

1. **Use indexes** on frequently queried columns
2. **Use EXPLAIN** to analyze query performance
3. **Normalize data** to reduce redundancy
4. **Use transactions** for data consistency
5. **Use connection pooling** in applications
6. **Regular VACUUM** to maintain performance
7. **Use prepared statements** to prevent SQL injection
8. **Monitor slow queries** and optimize them
9. **Use JSONB** instead of JSON for better performance
10. **Set appropriate constraints** for data integrity

## Common Issues

### Connection Limit
```sql
-- Check max connections
SHOW max_connections;

-- Check current connections
SELECT count(*) FROM pg_stat_activity;
```

### Lock Issues
```sql
-- Check locks
SELECT * FROM pg_locks;

-- Kill query
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 12345;
```

## Environment Variables

```bash
PGHOST=localhost
PGPORT=5432
PGDATABASE=mydb
PGUSER=myuser
PGPASSWORD=mypassword
```

## Resources
- Official Docs: https://www.postgresql.org/docs/
- Tutorial: https://www.postgresqltutorial.com/
- Performance: https://wiki.postgresql.org/wiki/Performance_Optimization

## Version Used in SeedGPT
```
PostgreSQL 15+ (Cloud SQL)
psycopg2-binary==2.9.9
```
