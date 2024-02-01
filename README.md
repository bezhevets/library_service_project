# library_service_project

### How to run Celery and Celery Beat

``celery -A library_service_project worker -l INFO --pool=solo``

#### Celery Beat

```celery -A library_service_project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler```
