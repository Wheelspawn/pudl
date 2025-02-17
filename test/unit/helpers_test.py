"""Unit tests for the :mod:`pudl.helpers` module."""

import pandas as pd
from pandas.testing import assert_frame_equal

from pudl.helpers import (convert_df_to_excel_file, convert_to_date,
                          fix_eia_na, fix_leading_zero_gen_ids)


def test_convert_to_date():
    """Test automated cleanup of EIA date columns."""
    in_df = pd.DataFrame.from_records(
        columns=["report_year", "report_month", "report_day"],
        data=[
            (2019, 3, 14),
            ("2019", "03", "14"),
        ],
    )
    expected_df = pd.DataFrame({
        "report_date": pd.to_datetime([
            "2019-03-14",
            "2019-03-14",
        ]),
    })
    out_df = convert_to_date(in_df)
    assert_frame_equal(out_df, expected_df)


def test_fix_eia_na():
    """Test cleanup of bad EIA spreadsheet NA values."""
    in_df = pd.DataFrame({
        "vals": [
            0,     # Don't touch integers, even if they're null-ish
            0.0,   # Don't touch floats, even if they're null-ish
            "0.",  # Should only replace naked decimals
            ".0",  # Should only replace naked decimals
            "..",  # Only replace single naked decimals
            "",
            " ",
            "\t",
            ".",
            "  ",  # Multiple whitespace characters
            "\t\t",  # 2-tabs: another Multi-whitespace
        ]
    })
    expected_df = pd.DataFrame({
        "vals": [
            0,
            0.0,
            "0.",
            ".0",
            "..",
            pd.NA,
            pd.NA,
            pd.NA,
            pd.NA,
            pd.NA,
            pd.NA,
        ]
    })
    out_df = fix_eia_na(in_df)
    assert_frame_equal(out_df, expected_df)


def test_fix_leading_zero_gen_ids():
    """Test removal of leading zeroes from EIA generator IDs."""
    in_df = pd.DataFrame({
        "generator_id": [
            "0001",   # Leading zeroes, all numeric string.
            "26",     # An appropriate numeric string w/o leading zeroes.
            100,      # Integer, should get stringified.
            100.0,    # What happens if it's a float?
            "01-A",   # Leading zeroes, alphanumeric. Should not change.
            "HRSG-01",   # Alphanumeric, should be no change.
        ]
    })
    expected_df = pd.DataFrame({
        "generator_id": [
            "1",
            "26",
            "100",
            "100.0",
            "01-A",
            "HRSG-01",
        ]
    })
    out_df = fix_leading_zero_gen_ids(in_df)
    assert_frame_equal(out_df, expected_df)


def test_convert_df_to_excel_file():
    """Test converting a dataframe into a pandas ExcelFile."""
    in_df = pd.DataFrame([[1, 2], [1, 2]])
    expected_df = pd.DataFrame([[1, 2], [1, 2]])

    out_excel_file = convert_df_to_excel_file(in_df, index=False)
    out_df = pd.read_excel(out_excel_file)

    assert_frame_equal(out_df, expected_df)
