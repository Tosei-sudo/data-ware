# coding: utf-8

# このモジュールは、PowerPoint ファイルのテキストを抽出するためのクラスを提供します。
import zipfile
import io
import xml.etree.ElementTree as ET

class DOCX:
    def read(self, file):
        
        components = zipfile.ZipFile(io.BytesIO(file.data), 'r')
        
        name_spaces = {
            "a" : "http://schemas.openxmlformats.org/drawingml/2006/main",
            "p" : "http://schemas.openxmlformats.org/presentationml/2006/main",
            "w" : "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "ns0" : "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        }
        
        texts = []
        for name in components.namelist():
            # slide text and notes
            if name == 'word/document.xml':
                with components.open(name) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    
                    text_nodes = root.findall('.//w:t', name_spaces)
                    for text_node in text_nodes:
                        texts.append(text_node.text)
        return texts