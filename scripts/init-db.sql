-- Create the miniflux database (Miniflux needs its own DB)
CREATE DATABASE miniflux;

-- Enable pgvector on the gofetch database
\c gofetch;
CREATE EXTENSION IF NOT EXISTS vector;
