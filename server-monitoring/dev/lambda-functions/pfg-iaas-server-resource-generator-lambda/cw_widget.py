# -*- coding: utf-8 -*-
import json
import boto3
from pathlib import Path

# Initialize the CloudWatch client
cloudwatch = boto3.client('cloudwatch')

def load_json_file(file_path):
    """Load JSON data from a file."""
    with file_path.open('r') as file:
        return json.load(file)

def create_or_update_dashboard(dashboard_name, dashboard_body):
    """Create or update a CloudWatch dashboard."""
    try:
        response = cloudwatch.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(dashboard_body)
        )
        return response
    except Exception as e:
        print(f"Error creating/updating dashboard '{dashboard_name}': {e}")
        return None

def manage_dashboards():
    # Define dashboard names and their corresponding JSON files
    # todo get this values from environment varibales
    dashboards = {
        "GLOBAL_DASHBOARD": "cw_widget_json/global_dashboard.json",
        "ACCOUNTS_DASHBOARD": "cw_widget_json/accounts_dashboard.json"
    }

    # Get the directory where the Lambda function code is located
    base_path = Path(__file__).parent

    for dashboard_name, json_file in dashboards.items():
        # Construct the full path to the JSON file
        json_file_path = base_path / json_file

        # Load dashboard body from JSON file
        try:
            dashboard_body = load_json_file(json_file_path)
        except Exception as e:
            print(f"Error reading JSON file '{json_file}': {e}")
            continue

        # Check if the dashboard exists
        existing_dashboards = cloudwatch.list_dashboards()
        existing_dashboard_names = {dashboard['DashboardName'] for dashboard in existing_dashboards['DashboardEntries']}

        if dashboard_name in existing_dashboard_names:
            # Dashboard exists; check for widgets
            try:
                dashboard_info = cloudwatch.get_dashboard(DashboardName=dashboard_name)
                existing_widgets = json.loads(dashboard_info['DashboardBody']).get('widgets', [])

                if existing_widgets:
                    print(f"Dashboard '{dashboard_name}' already exists with widgets. No action taken.")
                    continue
                else:
                    print(f"Dashboard '{dashboard_name}' exists but has no widgets. Updating it now.")
            except Exception as e:
                print(f"Error retrieving dashboard '{dashboard_name}': {e}")
                continue
        else:
            print(f"Dashboard '{dashboard_name}' does not exist. Creating it now.")

        # Create or update the dashboard with the loaded JSON data
        response = create_or_update_dashboard(dashboard_name, dashboard_body)
        if response:
            action = "created" if dashboard_name not in existing_dashboard_names else "updated"
            print(f"Dashboard '{dashboard_name}' {action} successfully. Response: {response}")
