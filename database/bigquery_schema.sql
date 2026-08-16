-- Sales and Inventory Audit Ledger Table
CREATE TABLE IF NOT EXISTS `vaultshield.sales_ledger` (
    transaction_id STRING NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    vault_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    manufacturer STRING,
    model STRING,
    imei STRING,
    retail_price NUMERIC,
    down_payment NUMERIC,
    otp_verified BOOLEAN,
    gemini_ocr_raw JSON
);
