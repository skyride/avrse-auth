from avrseauth.celery import app


@app.task(name="fetch_groups", expires=3600)
def fetch_groups():
    pass