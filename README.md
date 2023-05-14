kusto-monitoring
=================

Simplistic monitoring tool based on Kusto queries.

## Pre-requisites

1. Install the following system prerequisites:

```
apt install --no-install-recommends \
      python3 \
      python3-pip \
      python3-venv \
      python3-wheel \
      python3-numpy \
      python3-pandas
```

2. Create an instance of [Azure Communication Service](https://azure.microsoft.com/en-us/products/communication-services/), which will be used for delivering email alerts.

## Configuration

1. Setup Python virtual environment

```
python3 -mvenv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy `config.ini.template` to `config.ini` and fill-in all the details about your Kusto cluster, database, table and the app.

## Defining new alerts

Add a new `.kql` file containing a query to run.
The first line of the file must be a comment containing a schedule for the query in crontab format.

For instance:

```
// 0 0,3,6,9,12,15,18,21 * * *
// This query will run every three hours:
AzureMonitorAlerts
| where Timestamp > ago(1d)
| where AlertText has 'my alert'
| summarize count(), dcount(Cluster)
```

## Running

```
./run.sh
```
