from enum import StrEnum


class SearchSourceType(StrEnum):
    RECIPE = "recipe"
    TASK = "task"
    EXPENSE = "expense"
    FEEDBACK = "feedback"
    URL = "url"
    RESUME = "resume"
