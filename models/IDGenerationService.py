class IDGenerationService:
    def __init__(self, initial_value=1):
        self.current_id = initial_value

    def get_unique_id(self):
        unique_id = self.current_id
        self.current_id += 1
        return unique_id


# Initialize the ID generation service
id_service = IDGenerationService()
