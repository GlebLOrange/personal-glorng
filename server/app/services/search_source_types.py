from enum import StrEnum


class SearchSourceType(StrEnum):
    RECIPE = "recipe"
    NEWS = "news"
    TASK = "task"
    EXPENSE = "expense"
    FEEDBACK = "feedback"
    URL = "url"
    RESUME = "resume"
