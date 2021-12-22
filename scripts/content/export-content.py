from sumologic import SumoLogic
import argparse
import textwrap
import json
import sys
import time
import logging


logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.WARN)
log = logging.getLogger()


class AsyncJobStatus:
    IN_PROGRESS = "InProgress"
    SUCCESS = "Success"
    FAILED = "Failed"


api_to_content_type_map = {
    "SavedSearchWithScheduleSyncDefinition": "Search",
    "DashboardSyncDefinition": "Report",
    "DashboardV2SyncDefinition": "Dashboard",
    "MetricsSearchSyncDefinition": "MetricsV2",
    "LookupTableSyncDefinition": "Lookups",
}


def _get_folder_identifier(folder_id):
    hex_folder_id = None
    if folder_id == "Personal":
        rsp = api_client.get_personal_folder()
        personal_folder = _handle_response(rsp)
        hex_folder_id = personal_folder['id']
    elif folder_id.isdigit():
        hex_folder_id = "{0:x}".format(int(folder_id))
    else:
        try:
            int(folder_id, 16)
            hex_folder_id = folder_id
        except ValueError as ve:
            log.error(f"Invalid folder identifier: '{folder_id}. Must be "
                "folder identifier or 'Personal'")
            sys.exit(1)
    return hex_folder_id


def _get_content_type(api_type):
    return api_to_content_type_map.get(api_type)


def _handle_response(rsp):
    if not rsp.ok:
        body = rsp.text
        if rsp.headers['content-type'] == 'application/json':
            body = json.dumps(rsp.json(), indent=4)
        log.error(f"Request '{rsp.request.method} {rsp.url}' failed. code: {rsp.status_code}, "
                "error: {body}")

    rsp.raise_for_status()
    return rsp.json()


def _wait_for_export_job(content_id, job_id, wait_time=60*2):
    timeout = time.time() + wait_time
    while time.time() < timeout:
        rsp = api_client.check_export_status(content_id, job_id)
        job_status = _handle_response(rsp)
        if job_status['status'] != AsyncJobStatus.IN_PROGRESS:
            break
        time.sleep(1)

    if job_status['status'] == AsyncJobStatus.IN_PROGRESS:
        raise Exception(f"Timed out waiting for job: {job_id}")
    elif job_status['status'] == AsyncJobStatus.FAILED:
        raise Exception(f"Job '{job_id}' failed: {job_status['error']}")

    return job_status


def export_item(content_id):
    rsp = api_client.export_content(content_id)
    job_id = _handle_response(rsp)['id']
    log.info(f"Export job id: {job_id}")

    status = _wait_for_export_job(content_id, job_id)

    rsp = api_client.get_export_content_result(content_id, job_id)
    content = _handle_response(rsp)
    return content


def traverse_tree(folder_id, content_type):
    log.info(f"Exporting from root folder: {folder_id}")
    folders = [folder_id]
    path = []
    while folders:
        folder_id = folders.pop()
        rsp = api_client.get_folder(folder_id)
        folder = _handle_response(rsp)
        path.append(folder['name'])
        cur_path = "/".join(path)
        for child in folder['children']:
            item_id = child['id']
            if child['itemType'] == "Folder":
                folders.append(item_id)
            elif child['itemType'] == content_type:
                item_name = child['name']
                log.info(f"Exporting item: {item_name}, type={content_type}, id={item_id}")
                item = export_item(item_id)
                print(f"## Item: '{cur_path}/{item_name}'")
                print(json.dumps(item, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
            Traverse the content tree starting with the given root folder and export all content of a type.
            Content is dumped to stdout in JSON format.

            Examples:
            1. Export all log searches under folder "0000000007FFD79D":
                 python export-content <access_id> <access_key> -f 0000000007FFD79D -t SavedSearchWithScheduleSyncDefinition

            2. Export all dashboards under folder "Personal" folder:
                 python export-content <access_id> <access_key> -t DashboardSyncDefinition
        """),
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("access_id", help="Provide sumologic access_id")
    parser.add_argument("access_key", help="Provide sumologic access_key")
    parser.add_argument("-f", "--folder", dest="folder", default="Personal",
        help="Root folder identifier to start traversal. Defaults to 'Personal' folder.")
    parser.add_argument("-t", "--type", dest="api_content_type", required=True,
        choices=[
            "SavedSearchWithScheduleSyncDefinition",
            "DashboardSyncDefinition",
            "DashboardV2SyncDefinition",
            "MetricsSearchSyncDefinition",
            "LookupTableSyncDefinition",
        ],
        help="Content type to export")
    args = parser.parse_args()

    api_client = SumoLogic(args.access_id, args.access_key)
    content_type = _get_content_type(args.api_content_type)
    folder_id = _get_folder_identifier(args.folder)
    traverse_tree(folder_id, content_type)
