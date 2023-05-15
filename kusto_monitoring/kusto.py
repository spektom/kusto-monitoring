import logging

from .config import get_conf

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data.exceptions import KustoMultiApiError

_client = None


def _get_kusto_client():
    global _client
    if _client is None:
        kcsb = KustoConnectionStringBuilder.with_aad_device_authentication(
            get_conf("KUSTO_CLUSTER_URL")
        )
        kcsb.authority_id = get_conf("AAD_TENANT_ID")
        _client = KustoClient(kcsb)
    return _client


class QueryResult:
    def __init__(self, response):
        results = response.primary_results[0]
        df = dataframe_from_result_table(results)
        self.df = df.set_index(results.columns[0].column_name)

    def is_empty(self):
        return len(self.df) == 0

    def to_html(self):
        return self.df.to_html()


def run_query(query: str, retries: int = 1) -> QueryResult:
    client = _get_kusto_client()
    retryable_errors = ["0x80DA0006"]
    while retries > 0:
        retries -= 1
        try:
            logging.debug(f"Running Kusto query: {query}")
            return QueryResult(client.execute(get_conf("KUSTO_DATABASE_NAME"), query))
        except KustoMultiApiError as e:
            if retries > 0 and any(err in str(e) for err in retryable_errors):
                logging.warning(f"Query execution error: {e}. Retrying in 1 minute.")
            else:
                raise


def check_connectivity():
    run_query("print 'Checking connectivity with the cluster'")
