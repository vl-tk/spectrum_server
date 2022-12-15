import pandas as pd

from apps.report.services import ReportBuilder


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

    def report(self, groupby, value_field):
        try:
            result = self.df.groupby(by=groupby)[value_field].mean()
        except KeyError as e:
            print(self.df.columns)
            ilogger.exception(e)
            return
        return result.to_json()

    def report_avg_per_day(self, value_field, date_field):

        self.df.index = pd.to_datetime(self.df[date_field])  # format

        self.df[value_field] = self.df[value_field].astype(float)

        return self.report(
            groupby=[self.df.index.day, self.df.index.month, self.df.index.year],
            value_field=value_field
        )

    def report_avg_per_month(self, value_field, date_field):

        self.df.index = pd.to_datetime(self.df[date_field])  # format

        self.df[value_field] = self.df[value_field].astype(float)

        return self.report(
            groupby=[self.df.index.month, self.df.index.year],
            value_field=value_field
        )

    def report_sum_per_month(self, value_field, date_field):

        self.df.index = pd.to_datetime(self.df[date_field])  # format

        self.df[value_field] = self.df[value_field].astype(float)

        return self.report(
            groupby=[self.df.index.month, self.df.index.year],
            value_field=value_field
        )

    def report_sum_per_day(self, value_field, date_field):

        self.df.index = pd.to_datetime(self.df[date_field])  # format

        self.df[value_field] = self.df[value_field].astype(float)

        return self.report(
            groupby=[self.df.index.day, self.df.index.month, self.df.index.year],
            value_field=value_field
        )
