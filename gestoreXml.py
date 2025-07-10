from lxml import etree as ET
import pprint
from itertools import tee  # Import per pairwise

from gestoreStanza import *

__dictionaryIDtoSpan = {}

class Link:
    def __init__(self, r, h, d):
        self.rel = r
        self.head = h
        self.dipen = d

    def getRel(self):
        return self.rel
    def getHead(self):
        return self.head
    def getDipen(self):
        return self.dipen

# Definizione di pairwise per versioni di Python precedenti alla 3.10
def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

# Definizione di isCompound
def isCompound(xmlId):
    idx = xmlId.rfind(".")
    return (xmlId.find("-", idx) != -1)


def addJoin(sentence):

    xmlIdAttribute = '{http://www.w3.org/XML/1998/namespace}id'
    keySentence = sentence.get(xmlIdAttribute)
    __tokenIdtoSpan = __dictionaryIDtoSpan[keySentence]

    __joinMap = {}
    cercaSuccessivoDelComposto = False
    keyInSospeso = ""
    spanEndKeyinSospeso = ""

    lastKey = ""

    for current, next in pairwise(__tokenIdtoSpan.items()):
        currentKey = current[0]
        spanEndCurrent = current[1][1]
        spanInitNext = next[1][0]
        lastKey = next[0]
        if isCompound(currentKey):
            cercaSuccessivoDelComposto = True
            keyInSospeso = currentKey
            spanEndKeyinSospeso = spanEndCurrent
        if cercaSuccessivoDelComposto and spanInitNext.isdigit():
            __joinMap[keyInSospeso] = (spanEndKeyinSospeso == spanInitNext)
            cercaSuccessivoDelComposto = False
            keyInSospeso = ""
            spanEndKeyinSospeso = ""
        __joinMap[currentKey] = (spanEndCurrent == spanInitNext)

    if len(__tokenIdtoSpan) == 1:
        key = list(__tokenIdtoSpan.keys())[0]
        __joinMap[key] = False
    else:
        __joinMap[lastKey] = False

    for tokenNode in sentence.iter():
        if tokenNode.tag == "w" or tokenNode.tag == "pc":
            key = tokenNode.get(xmlIdAttribute)
            if __joinMap[key]:
                tokenNode.set("join", "right")

    return sentence


def sonOf(element):
    children = list(element)
    if len(children) == 0:
        return element
    elif len(children) > 1:
        return children[-1]
    else:
        return children[0]

def parentOf(pila):
    return pila.pop(0)

def elementTagOf(tokenConll, pilaParent, xmlIdValueToken, compound=False):
    xmlIdAttribute = '{http://www.w3.org/XML/1998/namespace}id'
    
    if tokenConll[FIELD_TO_IDX[UPOS]] == "PUNCT":
        if compound:
            elementToken = ET.Element('w')
        else:
            elementToken = ET.Element('pc')
    else:
        elementToken = ET.Element('w')

    lemma = tokenConll[FIELD_TO_IDX[LEMMA]]
    xpos = tokenConll[FIELD_TO_IDX[XPOS]]
    upos = tokenConll[FIELD_TO_IDX[UPOS]]
    feats = tokenConll[FIELD_TO_IDX[FEATS]]
    msd = ""

    elementToken.set(xmlIdAttribute, xmlIdValueToken)
    if compound:
        elementToken.set("norm", tokenConll[FIELD_TO_IDX[TEXT]])
        if tokenConll[FIELD_TO_IDX[UPOS]] == "PUNCT":
            elementToken.set("lemma", tokenConll[FIELD_TO_IDX[TEXT]])
    else:
        elementToken.text = tokenConll[FIELD_TO_IDX[TEXT]]
    if lemma != "_":
        if tokenConll[FIELD_TO_IDX[UPOS]] != "PUNCT":
            elementToken.set("lemma", lemma)
    if xpos != "_":
        elementToken.set("pos", xpos)
    if upos != "_":
        msd = "UPosTag=" + upos
        if feats != "_":
            msd += "|" + feats
        elementToken.set("msd", msd)
    elif feats != "_":
        msd += feats
        elementToken.set("msd", msd)

    return elementToken

def isCompoundElement(token):
    id = token[FIELD_TO_IDX[ID]]
    return (id.find("-") != -1)

def numElementInCompound(token):
    id = token[FIELD_TO_IDX[ID]]
    idx = id.find("-")
    init = int(id[0:idx])
    end = int(id[idx+1:])
    return end - init + 1

def myStaticDecrement():
    if not hasattr(myStaticDecrement, "counter"):
        myStaticDecrement.counter = 2
    myStaticDecrement.counter -= 1
    return myStaticDecrement.counter

def namedEntityAutomata(elementCurrent, tokenConll, stato, pila, xmlIdValueToken):
    ner = tokenConll[FIELD_TO_IDX[NER]]
    tagBio = ner[0:2]
    named = ner[2:]
    nextState = 0

    if stato == 0:
        if tagBio == "S-":
            if isCompoundElement(tokenConll):
                elementNamed = ET.SubElement(elementCurrent, 'name')
                elementNamed.set("type", named)
                pila.insert(0, elementNamed)
                elementCurrent = elementNamed
                myStaticDecrement.counter = numElementInCompound(tokenConll) - 1
                temp = elementTagOf(tokenConll, pila, xmlIdValueToken)
                elementCurrent.append(temp)
                elementCurrent = temp
                pila.insert(0, elementCurrent)
                nextState = 33
                return nextState, elementCurrent
            else:
                elementNamed = ET.SubElement(elementCurrent, 'name')
                elementNamed.set("type", named)
                pila.insert(0, elementNamed)
                elementCurrent = elementNamed
                elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
                elementCurrent = parentOf(pila)
                elementCurrent = pila[0]
                return nextState, elementCurrent
        elif tagBio == "B-":
            elementNamed = ET.SubElement(elementCurrent, 'name')
            elementNamed.set("type", named)
            pila.insert(0, elementNamed)
            elementCurrent = elementNamed
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
            nextState = 1
            return nextState, elementCurrent
        elif isCompoundElement(tokenConll):
            myStaticDecrement.counter = numElementInCompound(tokenConll) - 1
            temp = elementTagOf(tokenConll, pila, xmlIdValueToken)
            elementCurrent.append(temp)
            elementCurrent = temp
            pila.insert(0, elementCurrent)
            nextState = 3
            return nextState, elementCurrent
        elif tagBio == "-":
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
            return nextState, elementCurrent
    elif stato == 1:
        if tagBio == "I-":
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
            nextState = 1
            return nextState, elementCurrent
        if tagBio == "E-":
            if isCompoundElement(tokenConll):
                myStaticDecrement.counter = numElementInCompound(tokenConll) - 1
                temp = elementTagOf(tokenConll, pila, xmlIdValueToken)
                elementCurrent.append(temp)
                elementCurrent = temp
                pila.insert(0, elementCurrent)
                nextState = 33
                return nextState, elementCurrent
            else:
                elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
                elementCurrent = parentOf(pila)
                elementCurrent = pila[0]
                return nextState, elementCurrent
        if tagBio == "-":
            elementCurrent = sonOf(elementCurrent)
            pila.insert(0, elementCurrent)
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken, True))
            nextState = 2
            return nextState, elementCurrent
    elif stato == 2:
        if tagBio == "I-":
            elementCurrent = parentOf(pila)
            elementCurrent = pila[0]
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
            nextState = 1
            return nextState, elementCurrent
        if tagBio == "E-":
            elementCurrent = parentOf(pila)
            elementCurrent = parentOf(pila)
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken))
            elementCurrent = pila[0]
            return nextState, elementCurrent
        if tagBio == "-":
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken, True))
            nextState = 2
            return nextState, elementCurrent
    elif stato == 3:
        if myStaticDecrement.counter > 0:
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken, True))
            nextState = 3
            myStaticDecrement()
            return nextState, elementCurrent
        if myStaticDecrement.counter == 0:
            elementCurrent = parentOf(pila)
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken, True))
            elementCurrent = pila[0]
            nextState = 0
            return nextState, elementCurrent
    elif stato == 33:
        if myStaticDecrement.counter > 0:
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken, True))
            nextState = 33
            myStaticDecrement()
            return nextState, elementCurrent
        if myStaticDecrement.counter == 0:
            elementCurrent = parentOf(pila)
            elementCurrent.append(elementTagOf(tokenConll, pila, xmlIdValueToken, True))
            elementCurrent = parentOf(pila)
            elementCurrent = pila[0]
            nextState = 0
            return nextState, elementCurrent

def ExtractListSegFrom(fileTeiXml, tree):
    print("Call ExtractListSegFrom <-- " + fileTeiXml)
    root = tree.getroot()
    segTag = '{http://www.tei-c.org/ns/1.0}seg'
    xmlIdAttribute = '{http://www.w3.org/XML/1998/namespace}id'
    result = []
    for segmentElement in root.iter(segTag):
        result.append(segmentElement)
    return result

def getInitSpan(misc):
    j = misc.find("|")
    if "start" in misc and "|" in misc and j > 11:
        return misc[11:j]
    else:
        return "warning_getInitSpan"

def getEndSpan(misc):
    j = misc.rfind("=")
    if "end_char=" in misc:
        return misc[j+1:]
    else:
        return "warning_getEndSpan"

def elementSegXml(doc, nomeSegmento):
    global __dictionaryIDtoSpan
    xmlIdAttribute = '{http://www.w3.org/XML/1998/namespace}id'
    elementSeg = ET.Element('seg')
    elementSeg.set(xmlIdAttribute, nomeSegmento)
    pilaParent = []
    pilaParent.insert(0, elementSeg)
    numSentence = 0
    for sentence in doc.sentences:
        numSentence += 1
        xmlIdValueSentence = nomeSegmento + "." + str(numSentence)
        elementSentence = ET.SubElement(elementSeg, 's')
        elementSentence.set(xmlIdAttribute, xmlIdValueSentence)
        pilaParent.insert(0, elementSentence)
        stato = 0
        linkGrp = []
        elementCurrent = elementSentence
        __tokenIDtoSpan = {}
        setSuccTokenSpurious = False
        for token_dict in sentence.to_dict():
            token_conll = myCoNLL.convert_token_dict(token_dict)
            if isCompoundElement(token_conll) and numElementInCompound(token_conll) == 1:
                tokenSpurious = token_conll
                setSuccTokenSpurious = True
                continue
            if setSuccTokenSpurious:
                token_conll[FIELD_TO_IDX[TEXT]] = tokenSpurious[FIELD_TO_IDX[TEXT]]
                token_conll[FIELD_TO_IDX[MISC]] = tokenSpurious[FIELD_TO_IDX[MISC]]
                token_conll[FIELD_TO_IDX[NER]] = tokenSpurious[FIELD_TO_IDX[NER]]
                setSuccTokenSpurious = False
            idToken = token_conll[FIELD_TO_IDX[ID]]
            xmlIdValueToken = xmlIdValueSentence + "." + idToken
            if token_conll[FIELD_TO_IDX[DEPREL]] != "_" and token_conll[FIELD_TO_IDX[DEPREL]] != "<PAD>":
                r = token_conll[FIELD_TO_IDX[DEPREL]].replace(':', '_')
                if token_conll[FIELD_TO_IDX[DEPREL]] == "iob":
                    r = "iobj"
                if token_conll[FIELD_TO_IDX[HEAD]] == "0":
                    h = ""
                else:
                    h = token_conll[FIELD_TO_IDX[HEAD]]
                if token_conll[FIELD_TO_IDX[HEAD]] != "0" and token_conll[FIELD_TO_IDX[DEPREL]] == "root":
                    r = "dep"
                d = token_conll[FIELD_TO_IDX[ID]]
                a = Link(r, h, d)
                linkGrp.append(a)
            elif token_conll[FIELD_TO_IDX[DEPREL]] == "<PAD>":
                r = "dep"
                h = token_conll[FIELD_TO_IDX[HEAD]]
                d = token_conll[FIELD_TO_IDX[ID]]
                a = Link(r, h, d)
                linkGrp.append(a)
            spanInit = getInitSpan(token_conll[FIELD_TO_IDX[MISC]])
            spanEnd = getEndSpan(token_conll[FIELD_TO_IDX[MISC]])
            __tokenIDtoSpan[xmlIdValueToken] = (spanInit, spanEnd)
            stato, elementCurrent = namedEntityAutomata(elementCurrent, token_conll, stato, pilaParent, xmlIdValueToken)
        elementLinkGroup = ET.SubElement(elementSentence, 'linkGrp')
        elementLinkGroup.set("targFunc", "head argument")
        elementLinkGroup.set("type", "UD-SYN")
        __tokenIdtoSpan = __dictionaryIDtoSpan[xmlIdValueSentence] = __tokenIDtoSpan
        for l in linkGrp:
            elementLink = ET.SubElement(elementLinkGroup, 'link')
            elementLink.set("ana", "ud-syn:" + l.getRel())
            if l.getHead() == "":
                head = "#" + xmlIdValueSentence
            else:
                head = "#" + xmlIdValueSentence + "." + l.getHead()
            dip = "#" + xmlIdValueSentence + "." + l.getDipen()
            elementLink.set("target", head + " " + dip)
        pilaParent.pop(0)
    return elementSeg
