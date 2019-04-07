#!/usr/bin/python3
import os
import uuid, requests, json
from datetime import date, timedelta

token = os.environ["TODOIST_TOKEN"]
N_DAYS = 40


if not token:
    raise Exception("need TODOIST_TOKEN");


def create_task(task_name, project=None, priority=1, due_string=None, due_date=None):
    return requests.post(
        "https://beta.todoist.com/API/v8/tasks",
        data=json.dumps({
            "content": task_name,
            "due_string": due_string,
            "due_date": due_date,
            "due_lang": "en",
            "priority": priority
        }),
        headers={
            "Content-Type": "application/json",
            "X-Request-Id": str(uuid.uuid4()),
            "Authorization": "Bearer %s" % token
        }).json()


start_date = date.today()
day=1

while day <= N_DAYS:
    print(start_date)
    print(day)
    create_task("День {}".format(day), due_date=str(start_date), priority=2)
    start_date += + timedelta(days=1)
    day += 1
