
class DuplicateEntryError(Exception):
    """Exception raised for unique constraint violations."""
    def __init__(self, message="Unique constraint violated"):
        self.message = message
        super().__init__(self.message)

