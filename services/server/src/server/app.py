#! /usr/bin/env python3
import logging
import datetime
import polars as pl


from psycopg2 import sql
from psycopg2.extras import RealDictCursor, execute_values


from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from pyrecount.models import Dtype, Annotation
from pyrecount.accessor import Metadata, Project

from db import db_transaction
from services.cache_service import cache_project

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


@app.route("/api/projects", methods=["GET"])
def get_all_projects():
    # query = _load_sql('get_projects.sql')
    query = "SELECT DISTINCT project_id FROM metadata;"
    with db_transaction() as cur:
        cur.execute(query)
        table = cur.fetchall()

    return jsonify({"status": "success", "table": table})


# @app.route("/api/project/<project_id>", methods=["GET"])
# def get_project(project_id):
# conn = get_db_connection()
# cur = conn.cursor(cursor_factory=RealDictCursor)

# cur.execute(
# """
# SELECT rail_id, external_id, project_id, organism, metadata_source, date_processed
# FROM metadata
# WHERE project_id = %s;
# """,
# (project_id,),
# )

# rows = cur.fetchall()
# conn = get_db_connection()

# table = []
# for row in rows:
# try:
# row["rail_id"] = int(row["rail_id"])
# except (ValueError, TypeError):
# pass

# if isinstance(row.get("date_processed"), (datetime.date, datetime.datetime)):
# row["date_processed"] = row["date_processed"].isoformat()

# table.append(row)

# return jsonify({"status": "success", "table": table})


# def query_table_exists(cur, table_name, project_id):
# query = sql.SQL(
# "SELECT EXISTS (SELECT 1 FROM sammy.{} WHERE project_id = %s LIMIT 1)"
# ).format(sql.Identifier(table_name))
# cur.execute(query, (project_id,))
# return cur.fetchone()["exists"]


# def fetch_table_count(cur, table_name, project_id):
# query = sql.SQL("SELECT COUNT(*) FROM sammy.{} WHERE project_id = %s").format(
# sql.Identifier(table_name)
# )
# cur.execute(query, (project_id,))
# return cur.fetchone()["count"]


# def fetch_table_data(cur, table_name, project_id, start, limit):
# query = sql.SQL(
# "SELECT * FROM sammy.{} WHERE project_id = %s ORDER BY project_id LIMIT %s OFFSET %s"
# ).format(sql.Identifier(table_name))
# cur.execute(query, (project_id, limit, start))
# return cur.fetchall()


# @app.route("/api/project/<project_id>/gene", methods=["GET"])
# def get_gene(project_id):
# return handle_data_request(project_id, Dtype.GENE)


# @app.route("/api/project/<project_id>/exon", methods=["GET"])
# def get_exon(project_id):
# return handle_data_request(project_id, Dtype.EXON)


# @app.route("/api/project/<project_id>/jxn", methods=["GET"])
# def get_jxn(project_id):
# return handle_data_request(project_id, Dtype.JXN)


# def prepare_insert_data(dtype, project_id, project):
# table_name = dtype.value
# match dtype:
# case dtype.GENE:
# from services.data_service import gene_prep

# values, insert_query = gene_prep(project, project_id, dtype, table_name)

# case dtype.EXON:
# annotation, counts = project.load(dtype)
# counts_long = counts.unpivot(
# index=["chrom", "start", "end", "strand"],
# variable_name="external_id",
# value_name="count",
# ).with_columns(pl.lit(project_id).alias("project_id"))

# logging.info(f"Table {table_name} unpivot finished.")

# records = counts_long.to_dicts()
# values = [
# (
# r["project_id"],
# r["external_id"],
# r["chrom"],
# r["start"],
# r["end"],
# r["strand"],
# r["count"],
# )
# for r in records
# ]

# insert_query = sql.SQL("""
# INSERT INTO sammy.{} (
# project_id, external_id, chrom, start, "end", strand, count
# )
# VALUES %s
# """).format(sql.Identifier(table_name))

# case dtype.JXN:
# jxn_mm_dataframe, jxn_dataframe = project.load(Dtype.JXN)
# records = jxn_dataframe.to_dicts()

# values = [
# (
# r["project_id"],
# r["chromosome"],
# r["start"],
# r["end"],
# r["length"],
# r["strand"],
# r["annotated"],
# r["left_motif"],
# r["right_motif"],
# r["left_annotated"],
# r["right_annotated"],
# )
# for r in records
# ]

# insert_query = sql.SQL("""
# INSERT INTO sammy.{} (
# project_id, chromosome, start, "end", length, strand, annotated, left_motif, right_motif, left_annotated, right_annotated
# )
# VALUES %s
# """).format(sql.Identifier(table_name))

# case _:
# raise ValueError(f"No insert logic defined for table: {table_name}")

# return values, insert_query


# def handle_data_request(project_id, dtype):
# table_name = dtype.value
# valid_tables = {d.value for d in Dtype}
# if table_name not in valid_tables:
# abort(400, "Invalid data type")

# with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
# exists = query_table_exists(cur, table_name, project_id)

# if not exists:
# project = cache_project(project_id, dtype)

# values, insert_query = prepare_insert_data(dtype, project_id, project)
# logging.info(f"Starting insert {project_id} into table {table_name}.")
# try:
# execute_values(cur, insert_query, values)
# conn.commit()
# logging.info(f"Finished insert {project_id} into table {table_name}.")

# except Exception as e:
# conn.rollback()
# logging.exception(
# f"Failed inserting '{project_id}' into table '{table_name}': {e}"
# )
# raise

# start = request.args.get("start", default=0, type=int)
# end = request.args.get("end", default=1000, type=int)
# limit = end - start

# total_count = fetch_table_count(cur, table_name, project_id)
# table = fetch_table_data(cur, table_name, project_id, start, limit)

# return jsonify({"status": "success", "table": table, "totalCount": total_count})


if __name__ == "__main__":
    app.run()
