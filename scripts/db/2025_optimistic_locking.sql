-- 2025_optimistic_locking.sql
-- ROWVERSION para bloqueo optimista en tabla obras
ALTER TABLE obras ADD rowversion ROWVERSION NOT NULL;
-- ROWVERSION permite implementar control de concurrencia optimista en la app (ver modules/obras/model.py)
