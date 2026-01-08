def validate_all_answers(answers: dict, total: int) -> bool:
    """
    Validate that all questions have been answered.
    """
    return len(answers) == total
