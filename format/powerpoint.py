# coding: utf-8

# このモジュールは、PowerPoint ファイルのテキストを抽出するためのクラスを提供します。
import zipfile
import io
import numpy as np
import struct
import xml.etree.ElementTree as ET

class PPT_CFB_Header:
    def read(self, file):
        self.signature = file.read(8)
        self.clsid = file.read(16)
        self.minor_version = struct.unpack('<H', file.read(2))[0]
        self.major_version = struct.unpack('<H', file.read(2))[0]
        self.byte_order = struct.unpack('<H', file.read(2))[0]
        self.sector_shift = struct.unpack('<H', file.read(2))[0]
        self.mini_sector_shift = struct.unpack('<H', file.read(2))[0]
        self.reserved = file.read(6)
        self.number_of_directory_sectors = struct.unpack('<I', file.read(4))[0]
        self.number_of_fat_sectors = struct.unpack('<I', file.read(4))[0]
        self.first_directory_sector_location = struct.unpack('<I', file.read(4))[0]
        self.transaction_signature_number = struct.unpack('<I', file.read(4))[0]
        self.mini_stream_cutoff_size = struct.unpack('<I', file.read(4))[0]
        self.first_mini_fat_sector_location = struct.unpack('<I', file.read(4))[0]
        self.number_of_mini_fat_sectors = struct.unpack('<I', file.read(4))[0]
        self.first_difat_sector_location = struct.unpack('<I', file.read(4))[0]
        self.number_of_difat_sectors = struct.unpack('<I', file.read(4))[0]
        self.difat = np.frombuffer(file.read(436), dtype=np.int32)
        
        # 0埋めを読み取る
        file.read(4096 - 512)
        
class PPT:
    def read(self, file):
        self.cfb_header = PPT_CFB_Header()
        self.cfb_header.read(file)
        
class PPTX:
    def read(self, file):
        
        components = zipfile.ZipFile(io.BytesIO(file.data), 'r')
        
        name_spaces = {
            "a" : "http://schemas.openxmlformats.org/drawingml/2006/main",
            "p" : "http://schemas.openxmlformats.org/presentationml/2006/main",
        }
        
        texts = []
        for name in components.namelist():
            # slide text and notes
            if name.startswith('ppt/slides/slide') or name.startswith('ppt/notesSlides/notesSlide'):
                with components.open(name) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    
                    text_nodes = root.findall('.//a:t', name_spaces)
                    for text_node in text_nodes:
                        texts.append(text_node.text)
        return texts