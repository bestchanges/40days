#!/usr/bin/env python3
from datetime import timedelta
from string import Template

import todoist
import yaml
import argparse

parser = argparse.ArgumentParser(description='Import 40days program to Todoist.')
parser.add_argument('--yaml', help="YAML file with tasks plan", required=True)
parser.add_argument('--token', help="Todoist API token. Can be obtained Todoist -> settings -> integrations -> Token API", required=False)

args = parser.parse_args()

file = open(args.yaml)
data = yaml.load(file, Loader=yaml.FullLoader)
todoist_token = args.token
if not todoist_token:
    todoist_token = data['token']
api = todoist.TodoistAPI(todoist_token)
api.reset_state()
api.sync()


def prepare_data(data):
    date_start = data['period']['start']
    date_finish = date_start + timedelta(days=data['period']['duration'])
    data['period']['end'] = date_finish
    for task in data['tasks']:
        if 'date_string_append' in task:
            task['date_string'] += ' ' + task['date_string_append']
            task.pop('date_string_append')
        t = Template(task['date_string'])
        task['date_string'] = t.substitute(
            period_start=data['period']['start'],
            period_end=data['period']['end'],
        )


def find_project(name):
    matches = [x for x in api.state['projects'] if x['name'] == name]
    if matches:
        return matches[0]
    return None


def add_project(project_name, **kwargs):
    project = api.projects.add(project_name, **kwargs)
    api.commit()
    return project


def delete_project(project):
    api.projects.delete([project['id']])


def clear_projects(name):
    matches = [x['id'] for x in api.state['projects'] if x['name'] == name]
    if matches:
        api.projects.delete(matches)
        api.commit()


if __name__ == '__main__':
    prepare_data(data)

    for task in data['tasks']:
        project_name = task.pop('project')
        project = find_project(project_name) or add_project(project_name)
        task['project_id'] = project['id']
        print(task)
        existing = [x['id'] for x in api.state['items'] if x['content'] == task['content']]
        if existing:
            api.items.delete(existing)
        result = api.items.add(**task)
        api.commit()
        print(result)
