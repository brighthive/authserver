class RecordNotFoundError(Exception):
    def __init__(self, record_id):
        super().__init__()
        self.record_id = record_id
