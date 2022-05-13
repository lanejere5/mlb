# data pipeline

Lightweight data pipeline is implemented as a cloud run HTTP service.

Data is processed into a format suitable for plotting wins over 500 and
then saved to a Cloud Storage bucket.

Cloud Scheduler invokes the data pipeline each night at 00:05.
