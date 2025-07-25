#! /use/bin/env python3
import asyncio
import logging
import polars as pl

from pyrecount.models import Dtype, Annotation
from pyrecount.accessor import Metadata, Project


logger = logging.getLogger(__name__)


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
