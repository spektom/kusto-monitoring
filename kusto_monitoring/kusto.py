import logging

from .config import get_conf

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table

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


def run_query(query: str) -> QueryResult:
    client = _get_kusto_client()
    logging.info(f"Running Kusto query: {query}")
    response = client.execute(get_conf("KUSTO_DATABASE_NAME"), query)
    return QueryResult(response)


def check_connectivity():
    run_query("print 'Checking connectivity with the cluster'")
