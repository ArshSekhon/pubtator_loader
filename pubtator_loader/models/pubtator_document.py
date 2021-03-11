from spacy.language import Language
from spacy.training import offsets_to_biluo_tags
from .pubtator_entities import PubTatorEntity
from typing import List
import re
import json
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex


class PubTatorDocument:
    def __init__(self, id):
        self.id = id
        self.title_text = None
        self.abstract_text = None
        self.entities: List[PubTatorEntity] = []

    def get_space_separated_title_and_abstract(self):
        if self.title_text is not None and self.abstract_text is not None:
            return f"{self.title_text} {self.abstract_text}"
        elif self.title_text is None:
            raise Exception('Title text for this PubTator Document is "None".')
        elif self.abstract_text is None:
            raise Exception(
                'Abstract text for this PubTator Document is "None".')
        else:
            raise Exception(
                'Title and Abstract text for this PubTator Document is "None".'
            )

    def add_entity(self, mention: PubTatorEntity):
        self.entities.append(mention)

    def replace_overlapping_entities_w_longest(self):
        get_longest_entity = (lambda *entities: max(
            entities, key=lambda entity: entity.get_length()))

        return self.__replace_overlapping_entities(
            span_replacement_fn=get_longest_entity)

    def replace_overlapping_entities_w_shortest(self):
        get_shortest_entity = (lambda *entities: min(
            entities, key=lambda entity: entity.get_length()))

        return self.__replace_overlapping_entities(
            span_replacement_fn=get_shortest_entity)

    def __replace_overlapping_entities(self, span_replacement_fn):
        self.entities.sort(key=lambda entity: entity.start_index)
        processed_entities: List[PubTatorEntity] = []
        # if no merge required
        if len(self.entities) < 2:
            return

        idx = 0
        prev_entity: PubTatorEntity = self.entities[0]

        replacement = None

        while idx < len(self.entities):
            curr_entity: PubTatorEntity = self.entities[idx]
            # if not merging
            if replacement is None:
                if prev_entity.end_index >= curr_entity.start_index:
                    replacement = span_replacement_fn(prev_entity, curr_entity)
                else:
                    processed_entities.append(prev_entity)
            # if currently merging the entities
            else:
                if replacement.end_index >= curr_entity.start_index:
                    replacement = span_replacement_fn(prev_entity, curr_entity,
                                                      replacement)
                else:
                    processed_entities.append(replacement)
                    replacement = None
            prev_entity = curr_entity
            idx += 1

        if replacement:
            processed_entities.append(replacement)
        else:
            processed_entities.append(prev_entity)

        self.entities = processed_entities

    def __get_custom_tokenizer(self, nlp: Language) -> Tokenizer:
        infix_re = re.compile(
            r'''[!\"\#\$\%\&\'\(\)\*\+\,\-\.\/
            \:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]'''
        )
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

        return Tokenizer(nlp.vocab,
                         prefix_search=prefix_re.search,
                         suffix_search=suffix_re.search,
                         infix_finditer=infix_re.finditer,
                         token_match=None)

    def tokenize_and_convert_to_bilou(self, nlp: Language):
        self.replace_overlapping_entities_w_longest()
        text = self.get_space_separated_title_and_abstract()
        # we need to use a custom tokenizer to avoid the alignment issues
        # that were being caused by the punctuation being a part of the toke
        nlp.tokenizer = self.__get_custom_tokenizer(nlp)
        document = nlp(text)
        entity_offsets_semantic_types = [(entity.start_index, entity.end_index,
                                          entity.semantic_type_id)
                                         for entity in self.entities]
        entity_offsets_entity_id = [(entity.start_index, entity.end_index,
                                     entity.entity_id)
                                    for entity in self.entities]

        results = []
        sentences_started = 0
        for token, semantic_type_id, entity_id in zip(
                document,
                offsets_to_biluo_tags(document,
                                        entity_offsets_semantic_types),
                offsets_to_biluo_tags(document, entity_offsets_entity_id),
        ):
            if token.is_sent_start:
                if sentences_started == 0:
                    # begin the document with start
                    results.append(['<START>', '<START>', '<START>'])
                else:
                    # end previous sentence before beginning a new one
                    results.append(['<END>', '<END>', '<END>'])
                    results.append(['<START>', '<START>', '<START>'])
                sentences_started += 1
            results.append([token.text, semantic_type_id, entity_id])
        # end the last sentence
        results.append(['<END>', '<END>', '<END>'])
        return results

    def __str__(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=False,
                          indent=4)

    def __repr__(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=False,
                          indent=4)
