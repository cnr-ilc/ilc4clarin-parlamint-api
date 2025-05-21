import os
import shutil
from lxml import etree
from pathlib import Path
import zipfile
from gestoreXml import ExtractListSegFrom, elementSegXml, addJoin
from gestoreStanza import myCoNLL

async def enrich_xml(file_path, nlp):
    # Parso l'albero XML e arricchisco il file
    tree = etree.parse(file_path)
    segments = ExtractListSegFrom(file_path, tree)
    
    # Directory temporanea per i file CoNLL
    temp_dir = Path("/tmp/enrich_output")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        for segment in segments:
            id_segment = segment.attrib['{http://www.w3.org/XML/1998/namespace}id']
            text = segment.text
            nomeFileOutput = temp_dir / f"{id_segment}.ud.udner"
            
            doc = nlp(text)
            myCoNLL.write_doc2conll(doc, nomeFileOutput)
            
            new_element = elementSegXml(doc, id_segment)
            segment.text = ""  # cancella il testo di segmentElement
            
            for sentence in new_element:
                sentence = addJoin(sentence)
                segment.append(sentence)
        
        output_xml_path = temp_dir / f"{Path(file_path).stem}_enriched.xml"
        tree.write(output_xml_path, encoding="UTF-8")
        
        # Creazione del file ZIP
        zip_path = f"{Path(file_path).stem}_enriched.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_xml_path, arcname=output_xml_path.name)
            for conll_file in temp_dir.glob("*.ud.udner"):
                zipf.write(conll_file, arcname=conll_file.name)
        
        return zip_path
    finally:
        # Pulizia dei file temporanei
        shutil.rmtree(temp_dir)
