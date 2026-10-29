-- Userul cu care se conecteaza aplicatia Django
CREATE USER user_condimente WITH PASSWORD 'parola_condimente';

-- Baza de date a proiectului, avand ca proprietar userul de mai sus
CREATE DATABASE condimente OWNER user_condimente ENCODING 'UTF8';