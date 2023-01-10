import pandas as pd
from apps.report.services import ReportBuilder


def convert_to_date(key: tuple) -> str:
    if len(key) == 2:
        return f"{key[0]:0>2}.{key[1]}"
    if len(key) == 3:
        return f"{key[0]:0>2}.{key[1]:0>2}.{key[2]}"

class EventReportBuilder(ReportBuilder):

    def __init__(self, data):
        super().__init__(data=data)

        self.rows = []
        for d in self.data:
            fields = d['fields']

            fields['id'] = d['id']
            fields['created_at'] = d['created_at']
            fields['sort'] = d['sort']
            fields['updated_at'] = d['updated_at']

            self.rows.append(fields)

        self.df = pd.DataFrame.from_records(self.rows)

    def _prepare_index(self, date_field, value_field):
        self.df.index = pd.to_datetime(self.df[date_field])  # format
        self.df[value_field] = self.df[value_field].astype(float)

    def report(self, groupby, value_field):
        try:
            result = self.df.groupby(by=groupby)[value_field].mean()
        except KeyError as e:
            print(self.df.columns)
            ilogger.exception(e)
        res = result.to_dict()

        # format values

        res_with_dates = {}
        for k, v in res.items():
            res_with_dates[convert_to_date(k)] = f'{v:.2f}'

        return res_with_dates

    def report_avg_per_day(self, value_field, date_field):
        self._prepare_index(date_field, value_field)
        return self.report(
            groupby=[self.df.index.day, self.df.index.month, self.df.index.year],
            value_field=value_field
        )

    def report_avg_per_month(self, value_field, date_field):
        self._prepare_index(date_field, value_field)
        return self.report(
            groupby=[self.df.index.month, self.df.index.year],
            value_field=value_field
        )

    def report_sum_per_month(self, value_field, date_field):
        self._prepare_index(date_field, value_field)
        return self.report(
            groupby=[self.df.index.month, self.df.index.year],
            value_field=value_field
        )

    def report_sum_per_day(self, value_field, date_field):
        self._prepare_index(date_field, value_field)
        return self.report(
            groupby=[self.df.index.day, self.df.index.month, self.df.index.year],
            value_field=value_field
        )
