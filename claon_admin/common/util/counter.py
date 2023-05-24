from datetime import datetime, timedelta

import pandas as pd

from claon_admin.common.util.time import now


class DateCounter:
    def __init__(self, unit: str, data: list):
        self.unit = unit
        self.data = data

    # TODO: Need to be used only as a function not as a class object
    def get_count(self):
        day_dict = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}

        offset, freq = (52, 'W') if self.unit == "week" else (6, 'D')

        std_date = now().date()
        end_date = std_date - timedelta(weeks=1) if self.unit == "week" else std_date - timedelta(days=1)
        start_date = end_date - timedelta(weeks=offset) if self.unit == "week" else end_date - timedelta(days=offset)

        df = pd.DataFrame([d[1].date() for d in self.data], columns=['date']) # elem: created_at
        df["day"] = df["date"]
        df["year"] = df["date"].apply(lambda date: datetime.isocalendar(date)[0])
        df["week"] = df["date"].apply(lambda date: datetime.isocalendar(date)[1])

        # empty data frame init
        df_all = pd.DataFrame(pd.date_range(start_date, end_date, freq=freq), columns=['date'])
        df_all["day"] = df_all["date"].dt.date
        df_all["year"] = df_all["date"].apply(lambda date: datetime.isocalendar(date)[0])
        df_all["week"] = df_all["date"].apply(lambda date: datetime.isocalendar(date)[1])
        df_all["day_week"] = df_all["date"].apply(
            lambda date: day_dict[datetime.weekday(date)]) if self.unit == "day" else df_all.index
        df_all['count'] = 0

        for _, row in df.iterrows():
            if self.unit == "week":
                if df_all.loc[df_all[self.unit] == row[self.unit], "year"].values[0] == row["year"]:
                    df_all.loc[df_all[self.unit] == row[self.unit], 'count'] += 1
            else:
                df_all.loc[df_all[self.unit] == row[self.unit], 'count'] += 1

        return zip(df_all['day_week'].tolist(), df_all['count'].tolist())
