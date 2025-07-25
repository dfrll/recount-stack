CREATE SCHEMA IF NOT EXISTS sammy AUTHORIZATION sammy;

DROP TABLE IF EXISTS sammy.junctions;

DROP TABLE IF EXISTS sammy.exon_sums;

DROP TABLE IF EXISTS sammy.gene_sums;

DROP TABLE IF EXISTS sammy.metadata;

CREATE TABLE
    IF NOT EXISTS sammy.metadata (
        rail_id TEXT,
        external_id TEXT,
        study TEXT,
        project_id TEXT,
        organism TEXT,
        file_source TEXT,
        metadata_source TEXT,
        date_processed TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS sammy.gene_sums (
        project_id TEXT NOT NULL,
        external_id TEXT NOT NULL,
        gene_id TEXT NOT NULL,
        count INTEGER NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS sammy.exon_sums (
        project_id TEXT NOT NULL,
        external_id TEXT NOT NULL,
        chrom TEXT NOT NULL,
        start INTEGER NOT NULL,
        "end" INTEGER NOT NULL,
        strand TEXT NOT NULL,
        count INTEGER NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS sammy.junctions (
        project_id TEXT NOT NULL,
        chromosome TEXT NOT NULL,
        start INTEGER NOT NULL,
        "end" INTEGER NOT NULL,
        length INTEGER NOT NULL,
        strand TEXT NOT NULL,
        annotated TEXT NOT NULL,
        left_motif TEXT NOT NULL,
        right_motif TEXT NOT NULL,
        left_annotated TEXT NOT NULL,
        right_annotated TEXT NOT NULL
    );