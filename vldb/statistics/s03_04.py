"""Other: Number of papers per country/region (pie)"""
from asyncio import run

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame, concat
from uvloop import install

from vldb.statistics import test_plot_df
from vldb.statistics.s03_02 import both


def plot_both(df: DataFrame, ax: Axes) -> None:
    n = 2
    df = df.loc[df["Status"] == "Ultimately Accepted"]
    df = df.sort_values("Count", ascending=False)
    other = df.loc[df["Count"] < n]
    other = DataFrame(
        [["Other", "Ultimately Accepted", other["Count"].sum()]], columns=df.columns
    )
    df = concat([df.loc[df["Count"] >= n], other])
    ax.set_ylim((0, 1))
    ax.pie(
        df["Count"],
        labels=df["Country/Region"] + " (" + df["Count"].astype(str) + ")",
        autopct="%1.1f%%",
        # wedgeprops={"width": 1 / 2},
    )
    ax.axis("equal")
    ax.set_title(
        "Fraction of ultimately accepted papers per country/region\n(primary contact or first non-null country/region)"
    )


async def main() -> DataFrame:
    return await both()


if __name__ == "__main__":
    install()
    b_df = run(main())
    print(b_df, sep="\n")
    test_plot_df(b_df, plot_both)
    plt.savefig("plots/03_04_both.png")
