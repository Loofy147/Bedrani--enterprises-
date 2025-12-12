-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tenants table to manage different enterprises
CREATE TABLE tenants (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,        -- e.g. bedrani-maamur, bedrani-djelali
  domain TEXT UNIQUE,               -- e.g. bedrani-maamur.dz
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tenant-specific settings
CREATE TABLE tenant_settings (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(tenant_id, key)
);

-- Projects table
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  start_date DATE,
  end_date DATE,
  budget NUMERIC,
  status TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Properties table
CREATE TABLE properties (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  description TEXT,
  price NUMERIC,
  area_m2 NUMERIC,
  status TEXT,
  geo_point GEOMETRY(POINT, 4326),
  created_by INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Parcels table for land plots
CREATE TABLE parcels (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  cadastre_ref TEXT,
  owner TEXT,
  area_m2 NUMERIC,
  geom GEOMETRY(POLYGON, 4326),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX parcels_geom_idx ON parcels USING GIST (geom);

-- Seed initial tenants
INSERT INTO tenants (name, slug, domain) VALUES
('Badrani Maamur', 'bedrani-maamur', 'bedrani-maamur.dz'),
('Badrani Djelali', 'bedrani-djelali', 'bedrani-djelali.dz');

-- Seed initial settings for tenants
-- (Assuming tenant_id 1 is Maamur, 2 is Djelali)
INSERT INTO tenant_settings (tenant_id, key, value) VALUES
(1, 'branding', '{"logoUrl": "/tenants/bedrani-maamur/logo.png", "primaryColor": "#FF5733"}'),
(1, 'contact', '{"phone": "+213123456789", "email": "contact@bedrani-maamur.dz"}'),
(2, 'branding', '{"logoUrl": "/tenants/bedrani-djelali/logo.png", "primaryColor": "#3375FF"}'),
(2, 'contact', '{"phone": "+213987654321", "email": "contact@bedrani-djelali.dz"}');
