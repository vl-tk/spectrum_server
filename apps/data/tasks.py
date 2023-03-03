from celery import shared_task


@shared_task
def rebuild_abc_report():
    # NOT USED
    pass
    # from apps.data.views_reports import CHZReport6View
    # CHZReport6View().generate_report_records_to_db()
