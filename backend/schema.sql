-- MySQL 8.0 reference schema for the production-oriented design.
-- Demo app uses in-memory mock data by default; do not store raw identity documents here.
CREATE DATABASE IF NOT EXISTS insureflow;
USE insureflow;
CREATE TABLE insurer_registry (
  insurer_id VARCHAR(40) PRIMARY KEY,
  insurer_name VARCHAR(160) NOT NULL,
  licence_reference VARCHAR(80) NOT NULL UNIQUE,
  licence_status ENUM('ACTIVE','INACTIVE','PENDING') NOT NULL,
  checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE customer_tokens (
  customer_token VARCHAR(100) PRIMARY KEY,
  kyc_status ENUM('VERIFIED','PENDING','FAILED') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE insurance_products (
  product_id VARCHAR(50) PRIMARY KEY,
  insurer_id VARCHAR(40) NOT NULL,
  product_name VARCHAR(180) NOT NULL,
  premium DECIMAL(10,2) NOT NULL,
  coverage_limit DECIMAL(12,2) NOT NULL,
  policy_document_uri VARCHAR(500),
  FOREIGN KEY (insurer_id) REFERENCES insurer_registry(insurer_id)
);
CREATE TABLE checkout_transactions (
  transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  idempotency_key VARCHAR(160) NOT NULL UNIQUE,
  customer_token VARCHAR(100) NOT NULL,
  product_id VARCHAR(50) NOT NULL,
  payment_status ENUM('PENDING','CONFIRMED','FAILED','REFUNDED') NOT NULL,
  policy_status ENUM('NOT_ISSUED','ISSUED','CANCELLED') NOT NULL DEFAULT 'NOT_ISSUED',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_token) REFERENCES customer_tokens(customer_token),
  FOREIGN KEY (product_id) REFERENCES insurance_products(product_id)
);
CREATE TABLE policy_vault (
  certificate_id VARCHAR(80) PRIMARY KEY,
  transaction_id BIGINT NOT NULL UNIQUE,
  encrypted_document_uri VARCHAR(500) NOT NULL,
  issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id) REFERENCES checkout_transactions(transaction_id)
);
CREATE TABLE audit_log (
  audit_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_type VARCHAR(100) NOT NULL,
  transaction_id BIGINT NULL,
  event_status VARCHAR(30) NOT NULL,
  event_details JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
