"""Paper status: Status of papers per primary subject area"""
from asyncio import gather, run
from itertools import product
from math import isnan
from typing import Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from seaborn import barplot
from sqlalchemy import func, literal
from sqlalchemy.future import select
from uvloop import install

from vldb.statistics import get_data, test_plot_df
from vldb.tables import Revision, Submission


async def submission() -> DataFrame:
    statement = (
        select(Submission.primary_subject_area, Submission.status, func.count())
        .group_by(Submission.primary_subject_area, Submission.status)
        .order_by(Submission.primary_subject_area, Submission.status)
    )
    df = DataFrame(await get_data(statement))
    df[0] = df[0].apply(lambda s: s.partition("->")[0].strip())
    df = df.groupby([0, 1]).sum().reset_index()
    total = df.groupby(0).sum()
    accept = (
        df[df[1].isin(("Accept", "Minor revision", "Major revision"))].groupby(0).sum()
    )
    df = total.join(accept, how="outer", lsuffix="_t", rsuffix="_a")
    df = df.fillna(0).astype(int).reset_index()
    df = df.melt([0], ["2_a", "2_t"], "Status", "Count")
    df[0].replace(
        {
            "": "None",
            "Specialized and Domain-Specific Data Management": "Specialized and Domain-Specific\nData Management",
        },
        inplace=True,
    )
    df["Status"].replace({"2_t": "All", "2_a": "Accept/To be revised"}, inplace=True)
    return df.rename(columns={0: "Primary Subject Area"})


def plot_submission(df: DataFrame, ax: Axes) -> None:
    hue_order = ["All", "Accept/To be revised"]
    order = df[df["Status"] == "All"].sort_values("Count", ascending=False)[
        "Primary Subject Area"
    ]
    barplot(
        y="Primary Subject Area",
        x="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p in ax.patches:
        width = 0 if isnan(p.get_height()) else int(p.get_width())
        ax.annotate(
            width,
            xy=(
                p.get_x() + p.get_width() + 5,
                p.get_y() + p.get_height() / 2,
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of submissions per primary subject area")


async def revision() -> DataFrame:
    statement = (
        select(Revision.primary_subject_area, Revision.status, func.count())
        .group_by(Revision.primary_subject_area, Revision.status)
        .order_by(Revision.primary_subject_area, Revision.status)
    )
    df = DataFrame(await get_data(statement))
    df[0] = df[0].apply(lambda s: s.partition("->")[0].strip())
    df = df.groupby([0, 1]).sum().reset_index()
    total = df.groupby(0).sum()
    accept = df[df[1] == "Accept"].groupby(0).sum()
    df = total.join(accept, how="outer", lsuffix="_t", rsuffix="_a")
    df = df.fillna(0).astype(int).reset_index()
    df = df.melt([0], ["2_a", "2_t"], "Status", "Count")
    df[0].replace(
        {
            "": "None",
            "Specialized and Domain-Specific Data Management": "Specialized and Domain-Specific\nData Management",
        },
        inplace=True,
    )
    df["Status"].replace({"2_t": "All", "2_a": "Accept"}, inplace=True)
    return df.rename(columns={0: "Primary Subject Area"})


def plot_revision(df: DataFrame, ax: Axes) -> None:
    hue_order = ["All", "Accept"]
    order = df[df["Status"] == "All"].sort_values("Count", ascending=False)[
        "Primary Subject Area"
    ]
    barplot(
        y="Primary Subject Area",
        x="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p in ax.patches:
        width = 0 if isnan(p.get_height()) else int(p.get_width())
        ax.annotate(
            width,
            xy=(
                p.get_x() + p.get_width() + 1,
                p.get_y() + p.get_height() / 2,
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of revisions per primary subject area")


async def both() -> DataFrame:
    statement = (
        select(
            Submission.primary_subject_area,
            Submission.status,
            func.count(),
            literal("Submission"),
        )
        .group_by(Submission.primary_subject_area, Submission.status)
        .union_all(
            select(
                Revision.primary_subject_area,
                Revision.status,
                func.count(),
                literal("Revision"),
            ).group_by(Revision.primary_subject_area, Revision.status)
        )
    )
    df = DataFrame(await get_data(statement))
    df[0] = df[0].apply(lambda s: s.partition("->")[0].strip())
    df[0].replace(
        {
            "": "None",
            "Specialized and Domain-Specific Data Management": "Specialized and Domain-Specific\nData Management",
        },
        inplace=True,
    )
    df = (
        df[df[3] == "Submission"]
        .groupby(0)
        .sum()
        .join(
            df[df[1] == "Accept"].groupby(0).sum(),
            how="outer",
            lsuffix="_total",
            rsuffix="_ua",
        )
        .fillna(0)
        .astype(int)
        .rename(columns={"2_total": "All", "2_ua": "Ultimately accepted"})
    )
    return (
        df.reset_index()
        .rename(columns={0: "Primary Subject Area"})
        .melt(id_vars=["Primary Subject Area"], var_name="Status", value_name="Count")
    )


def plot_both(df: DataFrame, ax: Axes) -> None:
    hue_order = ["All", "Ultimately accepted"]
    order = df[df["Status"] == "All"].sort_values("Count", ascending=False)[
        "Primary Subject Area"
    ]
    barplot(
        y="Primary Subject Area",
        x="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p, (status, subject_area) in zip(ax.patches, product(hue_order, order)):
        width = 0 if isnan(p.get_height()) else int(p.get_width())
        total = df[
            (df["Primary Subject Area"] == subject_area) & (df["Status"] == "All")
        ]["Count"].iloc[0]
        ax.annotate(
            str(width) if status == "All" else f"{width:d} ({width/total:.0%})",
            xy=(
                p.get_x() + p.get_width() + (4 if status == "All" else 12),
                p.get_y() + p.get_height() / 2,
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of papers per primary subject area")


async def main() -> Tuple[DataFrame, DataFrame, DataFrame]:
    return await gather(submission(), revision(), both())


if __name__ == "__main__":
    install()
    s_df, r_df, b_df = run(main())
    print(s_df, r_df, sep="\n")
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/02_03_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/02_03_revision.png")
    test_plot_df(b_df, plot_both)
    plt.savefig("plots/02_03_both.png")
