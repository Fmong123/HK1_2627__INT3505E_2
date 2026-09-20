CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT DEFAULT 'pending',
    item TEXT NOT NULL
);
BEGIN TRANSACTION;

DELETE FROM orders;
DELETE FROM sqlite_sequence WHERE name = 'orders';

INSERT INTO orders (item, status) VALUES 
('Laptop', 'pending'),
('Phone', 'shipped'),
('Book', 'delivered');

COMMIT;