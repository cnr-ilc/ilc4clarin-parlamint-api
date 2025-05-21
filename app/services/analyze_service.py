from lxml import etree

def analyze_xml(file_path):
    log = []
    
    tree = etree.parse(file_path)
    root = tree.getroot()
    
    tag_counts = {
        's': 0,
        'w': 0,
        'name': 0,
        'pc': 0,
        'linkGrp': 0,
        'link': 0
    }
    
    for tag in tag_counts.keys():
        tag_counts[tag] = len(root.findall(f".//{{http://www.tei-c.org/ns/1.0}}{tag}"))
    
    for tag, count in tag_counts.items():
        log.append(f"Number of <{tag}> tags: {count}")
    
    return "\n".join(log)
