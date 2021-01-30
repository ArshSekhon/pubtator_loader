import json


class PubTatorEntity:
    def __init__(self, document_id, start_index, end_index, text_segment,
                 semantic_type_id, entity_id):
        self.document_id = document_id
        self.start_index = int(start_index)
        self.end_index = int(end_index)
        self.text_segment = text_segment
        self.semantic_type_id = semantic_type_id
        self.entity_id = entity_id

    def get_length(self):
        return self.end_index - self.start_index

    def __str__(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True,
                          indent=4)

    def __repr__(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True,
                          indent=4)
