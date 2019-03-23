from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class ReportRun(CreateableAPIResource, ListableAPIResource):
    OBJECT_NAME = "reporting.report_run"
