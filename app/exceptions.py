class TaskNotFoundException(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id

class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

class NotAuthorizeException(Exception):
    def __init__(self, message: str = "Not authorize to perform this action"):
        self.message = message


class DuplicateEntryException(Exception):
    def __init__(self, field: str):
        self.field = field