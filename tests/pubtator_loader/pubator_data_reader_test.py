from pubtator_loader.pubtator_corpus_reader import PubTatorCorpusReader


def test_load_corpus():
    dataset_reader = PubTatorCorpusReader(
        './tests/fixtures/sample_pubator_reader_input.txt')
    corpus = dataset_reader.load_corpus()

    assert len(corpus) == 3
    assert (corpus[0].title_text
            == ('DCTN4 as a modifier of chronic Pseudomonas'
                ' aeruginosa infection in cystic fibrosis | some text |')
            and (corpus[0].abstract_text
                 == ('Pseudomonas aeruginosa (Pa) infection in cystic '
                     'fibrosis (CF) patients.')))

    assert (
        corpus[1].title_text
        == 'Nonylphenol diethoxylate inhibits apoptosis induced in PC12 cells'
        and corpus[1].abstract_text
        == 'Nonylphenol and short-chain nonylphenol ethoxylates such as NP2 '
        'EO are present in aquatic environment as wastewater contaminants, '
        'and their toxic effects.')

    assert (corpus[2].title_text
            == 'Prevascularized silicon membranes for the enhancement of '
            'transport to implanted medical devices'
            and corpus[2].abstract_text
            == 'Recent advances in drug delivery and sensing devices '
            'for in situ applications.')

    assert len(corpus[0].entities) == 6
    assert len(corpus[1].entities) == 4
    assert len(corpus[2].entities) == 5

    assert ([
        f'{entry.document_id}\t{entry.start_index}\t{entry.end_index}'
        f'\t{entry.text_segment}\t{entry.semantic_type_id}\t{entry.entity_id}'
        for entry in corpus[0].entities
    ] == [
        '25763772\t0\t5\tDCTN4\tT103\tUMLS:C4308010',
        '25763772\t23\t63\tchronic Pseudomonas aeruginosa '
        'infection\tT038\tUMLS:C0854135',
        '25763772\t67\t82\tcystic fibrosis\tT038\tUMLS:C0010674',
        '25763772\t83\t120\tPseudomonas aeruginosa '
        '(Pa) infection\tT038\tUMLS:C0854135',
        '25763772\t124\t139\tcystic fibrosis\tT038\tUMLS:C0010674',
        '25763772\t141\t143\tCF\tT038\tUMLS:C0010674'
    ])
