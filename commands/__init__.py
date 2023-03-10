from .createAprilTagModel import entry as createAprilTagModel

commands = [
    createAprilTagModel,
]


def start():
    for command in commands:
        command.start()


def stop():
    for command in commands:
        command.stop()
