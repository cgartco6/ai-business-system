-- Payment attempts table
CREATE TABLE IF NOT EXISTS payment_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    amount DECIMAL(10,2),
    currency TEXT DEFAULT 'ZAR',
    payment_method TEXT,
    gateway TEXT,
    gateway_reference TEXT,
    status TEXT DEFAULT 'pending',
    gateway_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id)
);

-- Payout transactions table
CREATE TABLE IF NOT EXISTS payout_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    amount DECIMAL(10,2),
    percentage DECIMAL(5,2),
    destination_account TEXT,
    status TEXT DEFAULT 'pending',
    reference TEXT,
    payout_date DATE,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bank account details (encrypted)
CREATE TABLE IF NOT EXISTS bank_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT,
    account_number_encrypted TEXT,
    branch_code TEXT,
    bank_name TEXT,
    account_type TEXT,
    purpose TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
