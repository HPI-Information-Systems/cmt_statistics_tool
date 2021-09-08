from datetime import datetime
from typing import Callable, Iterable, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import DataFrame
from seaborn import despine, set_theme
from sqlalchemy.engine.row import Row
from sqlalchemy.sql.selectable import CompoundSelect, Select

from vldb.tables import async_session


async def get_data(statement: Union[Select, CompoundSelect]) -> Iterable[Row]:
    async with async_session() as session:
        return (await session.execute(statement)).fetchall()


def format_sort_track(
    df: DataFrame, track_column: str, revision: bool = False
) -> DataFrame:
    fmt = "Research -> %B %Y" if not revision else "Research -> %B %Y Revision"
    f = lambda s: datetime.strptime(s, fmt).strftime("%y/%m")  # noqa: E731
    df[track_column] = df[track_column].apply(f)
    return df.sort_values(track_column)


def test_plot_df(df: DataFrame, plot_fn: Callable[[DataFrame, Axes], None]) -> Figure:
    set_theme(context="talk", style="ticks", palette="colorblind")
    fig, ax = plt.subplots(figsize=(13, 7), dpi=100)
    plot_fn(df, ax)
    despine(ax=ax)
    plt.tight_layout()
    return fig


"""
wont use:
- 01_03_revision and 01_03_submission, because 01_03_both conveys the same info
- 01_04_submission and 01_04_revision in favour of 01_04_both
- 02_02_revision, because a percentage in 02_01_revision conveys the same info
- 02_03_submission and 02_03_revision in favour of 02_03_both
- 02_04_revision and 02_04_submission in favour of 02_04_both
- 03_02_submission and 03_02_revision in favour of 03_02_both
"""
