-- AI Business System Database Schema
-- This schema supports the lead generation and client management system

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_email TEXT,
    contact_name TEXT,
    industry TEXT,
    size TEXT,
    location TEXT,
    lead_score REAL DEFAULT 0,
    qualified_score REAL DEFAULT 0,
    status TEXT DEFAULT 'new',
    priority TEXT DEFAULT 'medium',
    source TEXT,
    last_contacted DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Outreach log table
CREATE TABLE IF NOT EXISTS outreach_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    campaign_id TEXT,
    campaign_type TEXT,
    status TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
);

-- Clients table
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    monthly_rate DECIMAL(10,2),
    start_date DATE,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Follow-up schedule table
CREATE TABLE IF NOT EXISTS follow_up_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    follow_up_type TEXT,
    scheduled_date DATETIME,
    subject TEXT,
    template TEXT,
    status TEXT DEFAULT 'scheduled',
    sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT,
    metric_value REAL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_outreach_campaign_id ON outreach_log(campaign_id);
CREATE INDEX IF NOT EXISTS idx_outreach_created_at ON outreach_log(created_at);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON system_metrics(recorded_at);
