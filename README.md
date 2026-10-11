# todo-cli

A simple command-line to-do list. One Python file, no dependencies (Python 3.8+).

## Usage

```sh
python3 todo.py add buy milk      # Added 1: buy milk
python3 todo.py list              # open tasks (also the default with no command)
python3 todo.py list --all        # include completed tasks
python3 todo.py done 1 2          # mark tasks as completed
python3 todo.py undo 1            # reopen a task
python3 todo.py rm 2              # delete a task
python3 todo.py clear             # delete all completed tasks
```

Tasks are stored in `~/.todo.json`. Set `TODO_FILE` to use a different file.

To run it as `todo` from anywhere:

```sh
chmod +x todo.py
ln -s "$PWD/todo.py" /usr/local/bin/todo
```

## Tests

```sh
python3 -m unittest
```
