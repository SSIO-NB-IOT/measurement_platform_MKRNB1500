from influxdb_client import InfluxDBClient
import pandas as pd


class InfluxDBEndPoint():

    def __init__(self, url : str,token :str, organisation :str,bucket_list : list[str]):
        self.bucket_list = bucket_list
        self.organisation = organisation
        self.client = InfluxDBClient(url=url,token=token,org= organisation)

    def query_database(self, query:str) -> pd.DataFrame:
        return self.client.query_api().query_data_frame(org= self.organisation,query = query)

    def request_mission_values(self,monitoring_campain_duration:str) -> dict:
        assert isinstance(monitoring_campain_duration, str)
        bucket_dict = {}
        for bucket in self.bucket_list:
            query = self._get_bucket_and_sum_query(bucket,monitoring_campain_duration)
            bucket_dict[bucket] = self.query_database( query)['_value']
        return bucket_dict

    def clean_influxDB(self):
        self.query_database(query=self._clean_data_base_query())

    def _clean_data_base_query(self) -> str:
        return "DROP SERIES FROM /.*/"

    def _get_bucket_and_sum_query(self,bucket :str,monitoring_campain_duration:str) -> str:
        
        return f"from(bucket: {bucket}) |> range(start: -{monitoring_campain_duration}) |> aggregateWindow(every: {monitoring_campain_duration}, fn: sum, createEmpty: false)"


if __name__ == "__main__":
    INFLUXDB_TOKEN="6PsVg3S01_BMDaAB-XNdNOsrEOIHXeKKoxVxMWbWfQ0Uer070XWE1aLqOqejozhZN7Aep_QY3ol-kpxfeeLl8g=="

    # Connect to InfluxDB
    url = "http://localhost:8086"
    org = "nb_iot"
    monitoring_campain_duration_str = "1h"
    influx_endpoint = InfluxDBEndPoint(url=url,
        organisation=org,
        token=INFLUXDB_TOKEN,
        bucket_list=["packetReceived"])
    print(influx_endpoint.request_mission_values(monitoring_campain_duration_str))
    influx_endpoint.clean_influxDB()
    