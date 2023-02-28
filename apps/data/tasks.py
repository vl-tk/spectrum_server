from celery import shared_task


@shared_task
def rebuild_abc_report():
    from apps.data.views_reports import CHZReport6View
    CHZReport6View().prepare_report()
