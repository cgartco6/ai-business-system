-- Sample data for AI Business System

-- Insert sample leads
INSERT OR IGNORE INTO leads (id, company_name, contact_email, contact_name, industry, size, location, lead_score, status, priority, source) VALUES
('lead_000001', 'Tech Solutions SA', 'info@techsolutionssa.co.za', 'Sarah Johnson', 'Technology', '10-50', 'Johannesburg', 8.5, 'qualified_high', 'high', 'ai_generated'),
('lead_000002', 'Digital Marketing Pros', 'hello@digitalmarketingpros.co.za', 'Mike Chen', 'Marketing', '5-20', 'Cape Town', 7.2, 'qualified_medium', 'medium', 'ai_generated'),
('lead_000003', 'Business Consultants CT', 'contact@businessconsultantsct.co.za', 'David Williams', 'Consulting', '10-30', 'Cape Town', 6.8, 'qualified_medium', 'medium', 'ai_generated'),
('lead_000004', 'SA Ecommerce Store', 'info@saecommercestore.co.za', 'Lisa van der Merwe', 'Retail', '15-40', 'Durban', 5.5, 'qualified_low', 'low', 'ai_generated'),
('lead_000005', 'Innovation Labs SA', 'contact@innovationlabssa.co.za', 'James Wilson', 'Technology', '20-100', 'Pretoria', 9.1, 'qualified_high', 'high', 'ai_generated');

-- Insert sample clients
INSERT OR IGNORE INTO clients (company_name, contact_person, email, monthly_rate, start_date, status) VALUES
('Tech Innovators SA', 'Robert Brown', 'robert@techinnovatorssa.co.za', 25000.00, '2024-01-15', 'active'),
('Digital Growth Partners', 'Maria Garcia', 'maria@digitalgrowthpartners.co.za', 25000.00, '2024-02-01', 'active'),
('Smart Business Solutions', 'Thomas Anderson', 'thomas@smartbusinesssolutions.co.za', 25000.00, '2024-01-20', 'active');

-- Insert sample outreach logs
INSERT OR IGNORE INTO outreach_log (lead_id, campaign_id, campaign_type, status) VALUES
('lead_000001', 'campaign_20240115_093000', 'cold_email', 'sent'),
('lead_000002', 'campaign_20240115_093000', 'cold_email', 'sent'),
('lead_000003', 'campaign_20240115_093000', 'cold_email', 'sent'),
('lead_000005', 'campaign_20240115_093000', 'cold_email', 'sent');

-- Insert sample system metrics
INSERT OR IGNORE INTO system_metrics (metric_type, metric_value) VALUES
('leads_generated', 150),
('emails_sent', 300),
('conversion_rate', 2.5),
('revenue_current', 75000),
('revenue_target', 1000000);
