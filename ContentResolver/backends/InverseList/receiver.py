#!/usr/bin/env python
#encoding=utf8
import sys

import lucene

from lucene import SimpleFSDirectory, System, File, Document, Field,StandardAnalyzer, IndexSearcher, Version,QueryParser

from spider.ContentResolver.backends.InverseList.pylucene_test import currentdir
import os
"""

PyLucene retriver simple example

"""

INDEXDIR = os.path.join(currentdir,'index')

def luceneRetriver(query):

        lucene.initVM()

        indir= SimpleFSDirectory(File(INDEXDIR))

        lucene_analyzer= StandardAnalyzer(Version.LUCENE_30)

        lucene_searcher= IndexSearcher(indir)

        my_query= QueryParser(Version.LUCENE_30,"text",\

        lucene_analyzer).parse(query)

        MAX= 1000

        total_hits =lucene_searcher.search(my_query,MAX)

        print"Hits: ",total_hits.totalHits

        for hit in total_hits.scoreDocs:

            print"Hit Score: ",hit.score, "Hit Doc:",hit.doc, "HitString:",hit.toString()
            
            doc= lucene_searcher.doc(hit.doc)

            print doc.get("text").encode("utf-8")
luceneRetriver(u"容 易 在")