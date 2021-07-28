from sumologic import SumoLogic
import argparse
import os.path
import json


def extant_file(arg):
    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError("{0} does not exist".format(arg))

    return arg


def get_api_endpoint(deployment):
    if deployment == "us1":
        return "https://api.sumologic.com/api"
    elif deployment in ["ca", "au", "de", "eu", "jp", "us2", "fed", "in"]:
        return "https://api.%s.sumologic.com/api" % deployment
    else:
        return 'https://%s-api.sumologic.net/api' % deployment


def get_explorer_id(explorer_name):
    explorer_views = sumologic_cli.get_explorer_views()
    if explorer_views:
        for explorer_view in explorer_views["data"]:
            if explorer_name == explorer_view["name"]:
                return explorer_view["id"]
    raise Exception("Explorer View with name %s not found" % explorer_name)


def get_explorer(explorer_name):
    explorer_views = sumologic_cli.get_explorer_views()
    if explorer_views:
        for explorer_view in explorer_views["data"]:
            if explorer_name == explorer_view["name"]:
                return explorer_view
    raise Exception("Explorer View with name %s not found" % explorer_name)


def create_explorer_view(explorer_name, level, filter=None):
    content = {
        "name": explorer_name,
        "level": level
    }
    if filter is not None:
        content["filter"] = filter
    try:
        response = sumologic_cli.create_explorer_view(content)
        job_id = response.json()["id"]
        print("%s EXPLORER -  creation successful with ID %s" % (explorer_name, job_id))
        return {"EXPLORER_NAME": response.json()["name"]}, job_id
    except Exception as e:
        if hasattr(e, 'response') and "errors" in e.response.json():
            errors = e.response.json()["errors"]
            for error in errors:
                if error.get('code') == 'topology:duplicate':
                    print("EXPLORER -  Duplicate Exists for Name %s" % explorer_name)
                    return

        raise e


def delete_explorer_view(explorer_name):
    try:
        explorer_id = get_explorer_id(explorer_name)
        response = sumologic_cli.delete_explorer_view(explorer_id)
        print("EXPLORER - Completed Explorer deletion for Name %s, response - %s" % (
            explorer_name, response.text))
    except Exception as e:
        print("EXPLORER - Exception while deleting the Explorer view %s," % e)


def prepare_parser():
    parser = argparse.ArgumentParser(description='Creates hierarchy in sumologic org.')
    parser.add_argument("-d", "--deployment", dest="deployment", help="Provide sumologic deployment ex us1,ca,au,de,eu,jp,us2,fed,in", required=True)
    parser.add_argument("-c", "--access_id", dest="access_id", help="Provide sumologic access_id", required=True)
    parser.add_argument("-k", "--access_key", dest="access_key", help="Provide sumologic access_key", required=True)
    parser.add_argument("-f", "--hierarchy_filepath", dest="hierarchy_filepath", help="Provide path to json file containing hierarchy", required=True, metavar="FILE", type=extant_file)

    return parser.parse_args()

if __name__ == '__main__':

    options = prepare_parser()
    with open(options.hierarchy_filepath, 'r') as f:
        hierarchy_data = json.load(f)
    api_endpoint = get_api_endpoint(options.deployment)
    sumologic_cli = SumoLogic(options.access_id, options.access_key, api_endpoint)

    delete_explorer_view(hierarchy_data['name'])
    create_explorer_view(hierarchy_data['name'], hierarchy_data['level'], hierarchy_data['filter'])

