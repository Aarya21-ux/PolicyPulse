CREATE TABLE policy_clauses (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source VARCHAR(200),
  page INT,
  body VARCHAR(2000),
  emb VECTOR(384, FLOAT32)
);
CREATE TABLE rules (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  category VARCHAR(50),
  limit_amt DECIMAL(12,2),
  clause_id INT
);
CREATE TABLE transactions (
  id INT PRIMARY KEY,
  emp VARCHAR(50),
  category VARCHAR(50),
  amount DECIMAL(12,2),
  txn_date DATE,
  has_receipt CHAR(1),
  approved CHAR(1)
);
CREATE VIEW v_violations AS
  SELECT t.id AS txn_id, t.emp, t.category, t.amount, r.limit_amt, r.clause_id
  FROM transactions t
  JOIN rules r ON LOWER(t.category) = LOWER(r.category)
  WHERE t.amount > r.limit_amt AND t.approved = 'N'
