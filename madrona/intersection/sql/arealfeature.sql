CREATE OR REPLACE FUNCTION update_datemodified_column()
        RETURNS TRIGGER AS 'BEGIN NEW.date_modified = NOW(); RETURN NEW; END;' LANGUAGE 'plpgsql';
 
CREATE TRIGGER update_datemodified_modtime BEFORE UPDATE
  ON intersection_arealfeature FOR EACH ROW EXECUTE PROCEDURE
  update_datemodified_column();