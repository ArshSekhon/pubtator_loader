from enum import Enum
import re

from pubtator_loader.models.pubtator_document import PubTatorDocument
from pubtator_loader.models.pubtator_entities import PubTatorEntity


class PubTatorCorpusReader:
    class LineType(Enum):
        TITLE = 'TITLE'
        ABSTRACT = 'ABSTRACT'
        MENTION = 'MENTION'
        DOC_SEP = 'DOCUMENT SEPARATOR'

    def __init__(self, file_path):
        self.file_path = file_path
        self.__document_being_read = None
        self.corpus = []

        self.valid_transitions = {
            None: [self.LineType.DOC_SEP, self.LineType.TITLE],
            # Title must be followed by abstract
            self.LineType.TITLE: [self.LineType.ABSTRACT],
            # abstract can be followed by mentions or the next title
            # (if no mentions exist)
            self.LineType.ABSTRACT:
            [self.LineType.MENTION, self.LineType.DOC_SEP],
            # mention must be followed by another mention or document separator
            self.LineType.MENTION:
            [self.LineType.MENTION, self.LineType.DOC_SEP],
            # document separator must be followed by another title
            # or document separator
            self.LineType.DOC_SEP:
            [self.LineType.TITLE, self.LineType.DOC_SEP]
        }

    def load_corpus(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            return self.__parse_lines(lines)

    def __parse_lines(self, content_lines):
        prev_line_type = None
        for line_number, line in enumerate(content_lines):
            try:
                curr_line_type = self.__get_line_type(line, line_number)
                self.__validate_line_type_transition(prev_line_type,
                                                     curr_line_type)
                if (curr_line_type == self.LineType.ABSTRACT
                        or curr_line_type == self.LineType.TITLE):
                    line_info = re.split('[|]', line, maxsplit=2)
                else:
                    line_info = re.split('[\t]', line, maxsplit=5)

                if curr_line_type == self.LineType.DOC_SEP:
                    self.corpus.append(self.__document_being_read)
                    self.__document_being_read = None

                elif curr_line_type == self.LineType.TITLE:
                    if self.__document_being_read is not None:
                        self.corpus.append(self.__document_being_read)
                    self.__document_being_read = PubTatorDocument(
                        int(line_info[0]))
                    self.__document_being_read.title_text = (
                        line_info[2].rstrip('\n'))

                elif curr_line_type == self.LineType.ABSTRACT:
                    self.__document_being_read.abstract_text = (
                        line_info[2].rstrip('\n'))

                elif curr_line_type == self.LineType.MENTION:
                    self.__document_being_read.add_entity(
                        PubTatorEntity(int(line_info[0]), int(line_info[1]),
                                       int(line_info[2]), line_info[3],
                                       line_info[4],
                                       line_info[5].rstrip('\n')))
                prev_line_type = curr_line_type
            except Exception as e:
                raise Exception('ERROR occured when parsing line'
                                f' #{line_number}. Exception {e}')

        if self.__document_being_read is not None:
            self.corpus.append(self.__document_being_read)

        return self.corpus

    def __validate_line_type_transition(self, prev_line_type, curr_line_type):
        if curr_line_type not in self.valid_transitions[prev_line_type]:
            raise Exception("Unexpected transition between line types found "
                            f"'{prev_line_type}' => '{curr_line_type}'."
                            f" '{prev_line_type}' can only be followed by"
                            f" {self.valid_transitions[prev_line_type]}")

    def __get_line_type(self, line, line_number):
        tokens = re.split('[\t\n|]', line)[:-1]

        if tokens[0] == '' and len(tokens) == 1:
            return self.LineType.DOC_SEP
        if tokens[1] == 'a':
            return self.LineType.ABSTRACT
        if tokens[1] == 't':
            return self.LineType.TITLE
        if len(tokens) == 6:
            return self.LineType.MENTION

        raise Exception(f"Unexpected content received on line #{line_number}"
                        ", the line/data"
                        f" may have been corrupted. Content: '{line}'")
