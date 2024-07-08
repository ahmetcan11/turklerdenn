"""Hello Analytics Reporting API V4."""
import os
import re
import json
from datetime import datetime, timedelta
from utils.updateViewsTask import update_views
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'utils/turklerden-7372617f8483.json'
VIEW_ID = '412712656'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'utils/turklerden-7372617f8483.json'
postsSubPathsDict = {}

class UniqueUsersByPath:
    def __init__(self, property_id, path):
        self.property_id = property_id
        self.path = path

    def run_report(self):
        pattern = r"/posts/.*"
        client = BetaAnalyticsDataClient()
        today = datetime.today()
        end_date = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        response = client.run_report(request)

        for row in response.rows:
            text = str(row.dimension_values[0])
            # Use re.search to find the first match in the text
            match = re.search(pattern, text)
            if match:
                postsSubPathsDict[row.dimension_values[0].value] = row.metric_values[0].value


def write_unique_users_to_file():
    unique_users_by_path = UniqueUsersByPath(property_id="412712656", path="/posts/")
    unique_users_by_path.run_report()
    aggregated_data = {}
    for key, value in postsSubPathsDict.items():
        normalized_key = key
        aggregated_data[normalized_key] = value
    # with open(f"views/{yesterday}.json", 'w') as json_file:
    #     json.dump(aggregated_data, json_file, indent=4)
    update_views(aggregated_data)
    return aggregated_data
