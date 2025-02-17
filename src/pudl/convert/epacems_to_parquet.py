"""Process raw EPA CEMS data into a Parquet dataset outside of the PUDL ETL.

This script transforms the raw EPA CEMS data from Zip compressed CSV files into
an Apache Parquet dataset partitioned by year and state.

Processing the EPA CEMS data requires information that's stored in the main PUDL
database, so to run this script, you must already have a PUDL database
available on your system.

"""
import argparse
import logging
import pathlib
import sys

import coloredlogs

import pudl
from pudl import constants as pc

logger = logging.getLogger(__name__)


def parse_command_line(argv):
    """
    Parse command line arguments. See the -h option.

    Args:
        argv (str): Command line arguments, including caller filename.

    Returns:
        dict: Dictionary of command line arguments and their parsed values.

    """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-y',
        '--years',
        nargs='+',
        type=int,
        help="""Which years of EPA CEMS data should be converted to Apache
        Parquet format. Default is all available years, ranging from 1995 to
        the present. Note that data is typically incomplete before ~2000.""",
        default=pc.WORKING_PARTITIONS['epacems']['years']
    )
    parser.add_argument(
        '-s',
        '--states',
        nargs='+',
        type=str.upper,
        help="""Which states EPA CEMS data should be converted to Apache
        Parquet format, as a list of two letter US state abbreviations. Default
        is everything: all 48 continental US states plus Washington DC.""",
        default=pc.WORKING_PARTITIONS["epacems"]["states"]
    )
    parser.add_argument(
        '-c',
        '--clobber',
        action='store_true',
        help="""Clobber existing parquet files if they exist. If clobber is not
        included but the parquet directory already exists the _build will
        fail.""",
        default=False
    )
    parser.add_argument(
        "--gcs-cache-path",
        type=str,
        help="""Load datastore resources from Google Cloud Storage.
        Should be gs://bucket[/path_prefix]"""
    )
    parser.add_argument(
        "--bypass-local-cache",
        action="store_true",
        default=False,
        help="If enabled, the local file cache for datastore will not be used."
    )

    arguments = parser.parse_args(argv[1:])
    return arguments


def main():
    """Convert zipped EPA CEMS Hourly data to Apache Parquet format."""
    # Display logged output from the PUDL package:
    pudl_logger = logging.getLogger("pudl")
    log_format = '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)s %(message)s'
    coloredlogs.install(fmt=log_format, level='INFO', logger=pudl_logger)

    args = parse_command_line(sys.argv)

    # Make sure the requested years/states are available:
    for year in args.years:
        if year not in pc.WORKING_PARTITIONS["epacems"]["years"]:
            raise ValueError(
                f"{year} is not a valid year within the EPA CEMS dataset."
            )
    for state in args.states:
        if state not in pc.WORKING_PARTITIONS["epacems"]["states"]:
            raise ValueError(
                f"{state} is not a valid state within the EPA CEMS dataset."
            )

    pudl_settings = pudl.workspace.setup.get_defaults()

    # Configure how we want to obtain raw input data:
    ds_kwargs = dict(
        gcs_cache_path=args.gcs_cache_path,
        sandbox=pudl_settings.get("sandbox", False)
    )
    if not args.bypass_local_cache:
        ds_kwargs["local_cache_path"] = pathlib.Path(pudl_settings["pudl_in"]) / "data"

    _ = pudl.helpers.prep_dir(
        pathlib.Path(pudl_settings["parquet_dir"]) / "epacems",
        clobber=args.clobber,
    )

    # Messy settings arguments used in our main ETL which we should clean up
    epacems_etl_settings = pudl.settings.EpaCemsBaseSettings(
        states=args.states,
        years=args.years,
    )

    pudl.etl.etl_epacems(
        epacems_etl_settings,
        pudl_settings,
        ds_kwargs,
    )


if __name__ == '__main__':
    sys.exit(main())
