#!/usr/bin/python
import shutil

class garbageCollector:

    def __init__(self,dp):
        self.directoryPath = dp
    
    def deleteDirTree(self, path):
        shutil.rmtree(self.directoryPath + path) 
    
    # TODO czyszczenie paternami i bardziej rozbudowane sprzatanie