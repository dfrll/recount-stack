#! /usr/bin/env python3
import logging
import polars as pl
from psycopg2 import sql

logger = logging.getLogger(__name__)


def gene_prep(project, project_id, dtype, table_name):
    annotation, counts = project.load(dtype)
    counts_long = counts.unpivot(
        index=["gene_id"], variable_name="external_id", value_name="count"
    ).with_columns(pl.lit(project_id).alias("project_id"))

    records = counts_long.to_dicts()

    values = [
        (r["project_id"], r["external_id"], r["gene_id"], r["count"]) for r in records
    ]

    insert_query = sql.SQL("""
    INSERT INTO sammy.{} (project_id, external_id, gene_id, count)
    VALUES %s
    """).format(sql.Identifier(table_name))
