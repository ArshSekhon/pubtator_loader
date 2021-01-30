from pubtator_loader.models.pubtator_document import PubTatorDocument
from pubtator_loader.models.pubtator_entities import PubTatorEntity
from copy import deepcopy


def test_pubtator_document_overlap_resolution():
    document = PubTatorDocument(1)
    document.add_entity(PubTatorEntity(1, 0, 15, '1', '1', '1'))
    document.add_entity(PubTatorEntity(1, 0, 6, '2', '2', '2'))
    document.add_entity(PubTatorEntity(1, 0, 8, '3', '3', '3'))
    document.add_entity(PubTatorEntity(1, 8, 15, '4', '4', '4'))
    document.add_entity(PubTatorEntity(1, 10, 25, '5', '5', '5'))
    document.add_entity(PubTatorEntity(1, 26, 31, '6', '6', '6'))
    document.add_entity(PubTatorEntity(1, 33, 35, '7', '7', '7'))

    document_copy = deepcopy(document)

    document.replace_overlapping_entities_w_longest()
    assert len(document.entities) == 3
    assert ([(entity.start_index, entity.end_index, entity.text_segment)
             for entity in document.entities] == [(10, 25, '5'), (26, 31, '6'),
                                                  (33, 35, '7')])

    document_copy.replace_overlapping_entities_w_shortest()
    assert len(document_copy.entities) == 4
    assert ([(entity.start_index, entity.end_index, entity.text_segment)
             for entity in document_copy.entities] == [(0, 6, '2'),
                                                       (8, 15, '4'),
                                                       (26, 31, '6'),
                                                       (33, 35, '7')])
