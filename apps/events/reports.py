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

    def report_avg_per_day(self, value_field, date_field):

        df = pd.DataFrame.from_records(self.rows)

        df.index = pd.to_datetime(df[date_field])  # format

        df[value_field] = df[value_field].astype(float)

        try:
            result = df.groupby(by=[df.index.day, df.index.month, df.index.year])[value_field].mean()
        except KeyError as e:
            print(df.columns)
            ilogger.exception(e)
            return

        return result.to_json()

    def report_avg_per_month(self, value_field, date_field):

        df = pd.DataFrame.from_records(self.rows)

        df.index = pd.to_datetime(df[date_field])  # format

        df[value_field] = df[value_field].astype(float)

        try:
            result = df.groupby(by=[df.index.month, df.index.year])[value_field].mean()
        except KeyError as e:
            print(df.columns)
            ilogger.exception(e)
            return

        return result.to_json()

    def report_sum_per_month(self, value_field, date_field):

        df = pd.DataFrame.from_records(self.rows)

        df.index = pd.to_datetime(df[date_field])  # format

        df[value_field] = df[value_field].astype(float)

        try:
            result = df.groupby(by=[df.index.month, df.index.year])[value_field].sum()
        except KeyError as e:
            print(df.columns)
            ilogger.exception(e)
            return

        return result.to_json()

    def report_sum_per_day(self, value_field, date_field):

        df = pd.DataFrame.from_records(self.rows)

        df.index = pd.to_datetime(df[date_field])  # format

        df[value_field] = df[value_field].astype(float)

        try:
            result = df.groupby(by=[df.index.day, df.index.month, df.index.year])[value_field].sum()
        except KeyError as e:
            print(df.columns)
            ilogger.exception(e)
            return

        return result.to_json()
