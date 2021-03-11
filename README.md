# PubTator Loader
![Build - Main](https://github.com/ArshSekhon/pubtator_loader/workflows/Build%20-%20Main/badge.svg) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![PyPI version](https://badge.fury.io/py/pubtator-loader.svg)](https://badge.fury.io/py/pubtator-loader)

`pubtator_loader` is a python module that allows loading corpus from PubTator format and manipulate documents as Python object.
It can also be used in combination with `spacy` to tokenize the documents and convert them to **BILUO Tags** to use for different
NLP tasks.

### PubTator Format

The PubTator format uses the following format:

```text
<PMID>|t|<TITLE>
<PMID>|a|<ABSTRACT>
<PMID>	<START OFFSET 1>	<LAST OFFSET 1>	<MENTION 1>	<TYPE 1>	<IDENTIFIER 1>
<PMID>	<START OFFSET 2>	<LAST OFFSET 2>	<MENTION 2>	<TYPE 2>	<IDENTIFIER 2>

<PMID>|t|<TITLE>
<PMID>|a|<ABSTRACT>
<PMID>	<START OFFSET 1>	<LAST OFFSET 1>	<MENTION 1>	<TYPE 1>	<IDENTIFIER 1>
<PMID>	<START OFFSET 2>	<LAST OFFSET 2>	<MENTION 2>	<TYPE 2>	<IDENTIFIER 2>
```

where:
* The first line contains the title of the paper.
* The second line contains the abstract of the paper.
* The subsequent lines contain the annotations for the entities in a tab separated format:
    * PMID
    * Start Offset
    * End Offset
    * Mention (entity text)
    * Type of Entity
    * Identifier (normalized form)

## Usage

```py
from pubtator_loader import PubTatorCorpusReader
dataset_reader = PubTatorCorpusReader('./sample_pubator_input.txt')

corpus = dataset_reader.load_corpus() 
# corpus will be a List[PubtatorDocuments]

for doc in corpus:
    print(doc)
"""
Console Output:
    {
  "id": 25763772,
  "title_text": "DCTN4 as a modifier of chronic ....",
  "abstract_text": "Pseudomonas aeruginosa (Pa) infection in cystic fibrosis .....",
  "entities": [
    {
      "document_id": 25763772,
      "start_index": 0,
      "end_index": 5,
      "text_segment": "DCTN4",
      "semantic_type_id": "T103",
      "entity_id": "UMLS:C4308010"
    },
    .
    .
    .
    {
      "document_id": 25763772,
      "start_index": 67,
      "end_index": 82,
      "text_segment": "cystic fibrosis",
      "semantic_type_id": "T038",
      "entity_id": "UMLS:C0010674"
    }
  ]
}
"""


import spacy
import scispacy

# load the scispacy model
nlp = spacy.load('en_core_sci_lg')

# Convert PubTator document to BILUO format.
doc_in_BILUO = doc.tokenize_and_convert_to_bilou(nlp)

for idx, (token, semantic_type_id, entity_id) in enumerate(doc_in_BILUO):
    print(f'{idx}\t{token}\t{semantic_type_id}\t{entity_id}')

"""
Console Output:

0         <START>          <START>     <START>
1           DCTN4      U-T116,T123  U-C4308010
2              as                O           O
3               a                O           O
4        modifier                O           O
5              of                O           O
6         chronic           B-T047  B-C0854135
7     Pseudomonas           I-T047  I-C0854135
8      aeruginosa           I-T047  I-C0854135
9       infection           L-T047  L-C0854135
10             in                O           O
11         cystic           B-T047  B-C0010674
12       fibrosis           L-T047  L-C0010674
13    Pseudomonas           B-T047  B-C0854135
14     aeruginosa           I-T047  I-C0854135
15              (           I-T047  I-C0854135
16             Pa           I-T047  I-C0854135
17              )           I-T047  I-C0854135
18      infection           L-T047  L-C0854135
19             in                O           O
20         cystic           B-T047  B-C0010674
21       fibrosis           L-T047  L-C0010674
.               .                .           .
.               .                .           .
.               .                .           .
.               .                .           .


"""
```
