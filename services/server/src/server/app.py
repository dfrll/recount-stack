#! /usr/bin/env python3
import os
import asyncio
import logging
import datetime
import psycopg2
import polars as pl

from psycopg2 import sql
from psycopg2.extras import RealDictCursor, execute_values

from dotenv import load_dotenv

from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from pyrecount.models import Dtype, Annotation
from pyrecount.accessor import Metadata, Project

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

load_dotenv(dotenv_path="/run/secrets/server")


def get_db_connection():
    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )
    return conn


@app.route("/api/projects", methods=["GET"])
def get_md():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT 
                project_id, 
                COUNT(external_id) AS external_id_count
            FROM metadata
            GROUP BY project_id;""")

            rows = cur.fetchall()

    table = []
    for row in rows:
        try:
            row["external_id_count"] = int(row["external_id_count"])
        except (ValueError, TypeError, KeyError):
            pass
        table.append(row)

    return jsonify({"status": "success", "table": table})


@app.route("/api/project/<project_id>", methods=["GET"])
def get_project(project_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    rail_id,
                    external_id,
                    project_id,
                    organism,
                    metadata_source,
                    date_processed
                FROM metadata
                WHERE project_id = %s;
                """,
                (project_id,),
            )

            rows = cur.fetchall()

    table = []
    for row in rows:
        try:
            row["rail_id"] = int(row["rail_id"])
        except (ValueError, TypeError, KeyError):
            pass

        try:
            row["external_id_count"] = int(row["external_id_count"])
        except (ValueError, TypeError, KeyError):
            pass

        if isinstance(row.get("date_processed"), (datetime.date, datetime.datetime)):
            row["date_processed"] = row["date_processed"].isoformat()

        table.append(row)

    return jsonify({"status": "success", "table": table})


def query_table_exists(cur, table_name, project_id):
    query = sql.SQL(
        "SELECT EXISTS (SELECT 1 FROM sammy.{} WHERE project_id = %s LIMIT 1)"
    ).format(sql.Identifier(table_name))
    cur.execute(query, (project_id,))
    return cur.fetchone()["exists"]


def fetch_table_count(cur, table_name, project_id):
    query = sql.SQL("SELECT COUNT(*) FROM sammy.{} WHERE project_id = %s").format(
        sql.Identifier(table_name)
    )
    cur.execute(query, (project_id,))
    return cur.fetchone()["count"]


def fetch_table_data(cur, table_name, project_id, start, limit):
    query = sql.SQL(
        "SELECT * FROM sammy.{} WHERE project_id = %s ORDER BY project_id LIMIT %s OFFSET %s"
    ).format(sql.Identifier(table_name))
    cur.execute(query, (project_id, limit, start))
    return cur.fetchall()


def cache_project(project_id, dtype):
    organism = "human"
    dbase = "sra"
    annotation = Annotation.GENCODE_V29

    mdata = Metadata(organism=organism)
    mdata.cache()
    mdata_frame = mdata.load()

    proj_frame = mdata_frame.filter(pl.col("project").is_in([project_id]))

    project = Project(
        metadata=proj_frame,
        dbase=dbase,
        organism=organism,
        dtype=[dtype],
        jxn_format="all",
        annotation=annotation,
    )

    asyncio.run(project.cache())
    return project


@app.route("/api/project/<project_id>/gene", methods=["GET"])
def get_gene(project_id):
    return handle_data_request(project_id, Dtype.GENE)


@app.route("/api/project/<project_id>/exon", methods=["GET"])
def get_exon(project_id):
    return handle_data_request(project_id, Dtype.EXON)


@app.route("/api/project/<project_id>/jxn", methods=["GET"])
def get_jxn(project_id):
    return handle_data_request(project_id, Dtype.JXN)


def prepare_insert_data(dtype, project_id, project):
    """ """
    batch_size = 100
    table_name = dtype.value

    match dtype:
        case dtype.GENE:
            annotation, counts = project.load(dtype)
            index_cols = ["gene_id"]

            insert_sql = sql.SQL("""
            INSERT INTO sammy.{} (project_id, external_id, gene_id, count)
            VALUES %s
            """).format(sql.Identifier(table_name))

            batch = list()
            for col in counts.columns:
                if col in index_cols:
                    continue

                chunk = (
                    counts.select(index_cols + [col])
                    .with_columns(
                        [
                            pl.lit(col).alias("external_id"),
                            pl.lit(project_id).alias("project_id"),
                        ]
                    )
                    .rename({col: "count"})
                )

                for row in chunk.iter_rows(named=True):
                    record = (
                        row["project_id"],
                        row["external_id"],
                        row["gene_id"],
                        row["count"],
                    )
                    batch.append(record)

                    if len(batch) == batch_size:
                        yield insert_sql, batch
                        batch = list()

            if batch:
                yield insert_sql, batch

        case dtype.EXON:
            annotation, counts = project.load(dtype)

            index_cols = ["chrom", "start", "end", "strand"]

            insert_sql = sql.SQL("""
            INSERT INTO sammy.{} (
            project_id, external_id, chrom, start, "end", strand, count
            )
            VALUES %s
            """).format(sql.Identifier(table_name))

            batch = list()
            for col in counts.columns:
                if col in index_cols:
                    continue

                chunk = (
                    counts.select(index_cols + [col])
                    .with_columns(
                        [
                            pl.lit(col).alias("external_id"),
                            pl.lit(project_id).alias("project_id"),
                        ]
                    )
                    .rename({col: "count"})
                )

                for row in chunk.iter_rows(named=True):
                    record = (
                        row["project_id"],
                        row["external_id"],
                        row["chrom"],
                        row["start"],
                        row["end"],
                        row["strand"],
                        row["count"],
                    )
                    batch.append(record)

                    if len(batch) == batch_size:
                        yield insert_sql, batch
                        batch = list()

            if batch:
                yield insert_sql, batch

        case dtype.JXN:
            jxn_mm_dataframe, jxn_dataframe = project.load(dtype)

            insert_sql = sql.SQL("""
                INSERT INTO sammy.{} (
                    project_id, chromosome, start, "end", length, strand, annotated, left_motif, right_motif, left_annotated, right_annotated
                )
                VALUES %s
            """).format(sql.Identifier(table_name))

            batch = []
            for row in jxn_dataframe.iter_rows(named=True):
                record = (
                    row["project_id"],
                    row["chromosome"],
                    row["start"],
                    row["end"],
                    row["length"],
                    row["strand"],
                    row["annotated"],
                    row["left_motif"],
                    row["right_motif"],
                    row["left_annotated"],
                    row["right_annotated"],
                )
                batch.append(record)

                if len(batch) == batch_size:
                    yield insert_sql, batch
                    batch = []

            if batch:
                yield insert_sql, batch

        case _:
            raise ValueError(f"No insert logic defined for table: {table_name}")


def handle_data_request(project_id, dtype):
    table_name = dtype.value
    valid_tables = {d.value for d in Dtype}
    if table_name not in valid_tables:
        abort(400, "Invalid data type")

    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        exists = query_table_exists(cur, table_name, project_id)

        if not exists:
            project = cache_project(project_id, dtype)

            try:
                logging.info(f"Starting insert {project_id} into table {table_name}.")
                for insert_sql, batch in prepare_insert_data(
                    dtype, project_id, project
                ):
                    execute_values(cur, insert_sql, batch)
                conn.commit()
                logging.info(f"Finished insert {project_id} into table {table_name}.")

            except Exception as e:
                conn.rollback()
                logging.exception(
                    f"Failed inserting '{project_id}' into table '{table_name}': {e}"
                )
                raise

        start = request.args.get("start", default=0, type=int)
        end = request.args.get("end", default=1000, type=int)
        limit = end - start

        total_count = fetch_table_count(cur, table_name, project_id)
        table = fetch_table_data(cur, table_name, project_id, start, limit)

    return jsonify({"status": "success", "table": table, "totalCount": total_count})


if __name__ == "__main__":
    app.run()
