#!/usr/bin/env python3
"""A simple command-line to-do list."""

import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_FILE = Path.home() / ".todo.json"


def todo_file():
    return Path(os.environ.get("TODO_FILE", DEFAULT_FILE))


def load():
    path = todo_file()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        sys.exit(f"error: {path} is not valid JSON")


def save(tasks):
    path = todo_file()
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(tasks, indent=2) + "\n")
    tmp.replace(path)


def find(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    sys.exit(f"error: no task with id {task_id}")


def cmd_add(args):
    tasks = load()
    task = {
        "id": max((t["id"] for t in tasks), default=0) + 1,
        "text": " ".join(args.text),
        "done": False,
    }
    tasks.append(task)
    save(tasks)
    print(f"Added {task['id']}: {task['text']}")


def cmd_list(args):
    tasks = load()
    if not args.all:
        tasks = [t for t in tasks if not t["done"]]
    if not tasks:
        print("Nothing to do!")
        return
    width = len(str(max(t["id"] for t in tasks)))
    for task in tasks:
        mark = "x" if task["done"] else " "
        print(f"{task['id']:>{width}}. [{mark}] {task['text']}")


def cmd_done(args):
    tasks = load()
    for task_id in args.ids:
        find(tasks, task_id)["done"] = True
    save(tasks)
    print(f"Completed {', '.join(map(str, args.ids))}")


def cmd_undo(args):
    tasks = load()
    for task_id in args.ids:
        find(tasks, task_id)["done"] = False
    save(tasks)
    print(f"Reopened {', '.join(map(str, args.ids))}")


def cmd_rm(args):
    tasks = load()
    for task_id in args.ids:
        tasks.remove(find(tasks, task_id))
    save(tasks)
    print(f"Removed {', '.join(map(str, args.ids))}")


def cmd_clear(args):
    tasks = load()
    remaining = [t for t in tasks if not t["done"]]
    save(remaining)
    print(f"Cleared {len(tasks) - len(remaining)} completed task(s)")


def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description=__doc__)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("add", help="add a task")
    p.add_argument("text", nargs="+", help="task description")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", aliases=["ls"], help="list open tasks")
    p.add_argument("-a", "--all", action="store_true", help="include completed tasks")
    p.set_defaults(func=cmd_list)

    for name, func, text in (
        ("done", cmd_done, "mark tasks as completed"),
        ("undo", cmd_undo, "mark tasks as not completed"),
        ("rm", cmd_rm, "delete tasks"),
    ):
        p = sub.add_parser(name, help=text)
        p.add_argument("ids", nargs="+", type=int, metavar="id")
        p.set_defaults(func=func)

    p = sub.add_parser("clear", help="delete all completed tasks")
    p.set_defaults(func=cmd_clear)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(["list"])
    args.func(args)


if __name__ == "__main__":
    main()
