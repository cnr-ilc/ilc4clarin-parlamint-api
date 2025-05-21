# ilc4clarin-parlamint-api

**API for linguistic enrichment and analysis of the Italian ParlaMint corpus in TEI-XML format**

## Overview

This repository provides a web service interface to the processing pipeline originally developed in [LinguisticallyAnnotatedCorpus-TEI-Parlamint-IT](https://github.com/cnr-ilc/LinguisticallyAnnotatedCorpus-TEI-Parlamint-IT). The original tool produces linguistically annotated parliamentary corpora in TEI-XML format from raw or partially processed data.

The API exposes two main functionalities:

- **/enrich** – performs linguistic annotation of parliamentary texts using Stanza NLP and converts them into TEI-XML.
- **/analyze** – runs post-hoc linguistic analysis on already TEI-encoded texts.

## Description

The service processes parliamentary texts (e.g. interventions from the Italian Senate, 2013–2022) and outputs data conforming to the [ParlaMint](https://clarin.eu/parlamint) TEI-XML standard. The underlying pipeline performs tokenization, lemmatization, POS tagging, dependency parsing, and NER using [Stanza](https://stanfordnlp.github.io/stanza/), and structures the output according to Parla-CLARIN TEI guidelines.

## API Endpoints

### `POST /parlamint-api/api/enrich`

Upload a plain text file. The API returns a TEI-XML file with full linguistic annotation.

### `POST /parlamint-api/api/analyze`

Upload a TEI-XML file. The API runs further analysis or validation and returns enhanced output.

## Input Format

- Input: `multipart/form-data` with a `file` field (plain text for `/enrich`, TEI-XML for `/analyze`)
- Output: JSON with metadata or direct file return depending on deployment

## Usage Example

```bash
curl -X POST http://<host>/parlamint-api/api/enrich \
  -F "file=@intervento.txt"
````

## Deployment

The API is built with [FastAPI](https://fastapi.tiangolo.com/) and can be deployed as a container or WSGI app. See `Dockerfile` and `docker-compose.yml` (if provided) for quick setup.

## License

* **API Code**: Licensed under MIT.
* **Linguistic models**: For non-commercial use, under **CC BY-NC-SA**. Additional restrictions may apply depending on original datasets.

## Related Projects

* [LinguisticallyAnnotatedCorpus-TEI-Parlamint-IT](https://github.com/cnr-ilc/LinguisticallyAnnotatedCorpus-TEI-Parlamint-IT)
* [ParlaMint project](https://www.clarin.eu/parlamint)
* [Stanza NLP](https://stanfordnlp.github.io/stanza/)

---

Maintained by [CNR-ILC](https://www.ilc.cnr.it/) as part of the ILC4CLARIN infrastructure.
