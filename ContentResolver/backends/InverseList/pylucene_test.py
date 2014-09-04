#encoding=utf8
import os,sys,glob
import lucene
import StringIO
from lucene import SimpleFSDirectory, System, File, Document, Field, StandardAnalyzer, IndexWriter, Version
from spider.conf import settings
def luceneIndexer(contents):
    lucene.initVM()
    

    INDEXIDR= settings.INDEX_DIR

    indexdir= SimpleFSDirectory(File(INDEXIDR))
    
    analyzer= StandardAnalyzer(Version.LUCENE_30)

    index_writer= IndexWriter(indexdir,analyzer,True,\

    IndexWriter.MaxFieldLength(512))
    for tfile in contents:
        print"Indexing: ", tfile

        document= Document()

        content= tfile.getvalue()

        document.add(Field("text",content,Field.Store.YES,\
                           Field.Index.ANALYZED))
        index_writer.addDocument(document)
        print"Done: ", tfile
        index_writer.optimize()
        print index_writer.numDocs()
    index_writer.close()
        
currentdir=os.path.abspath(os.path.dirname(__file__))
try:
    os.makedirs(os.path.join(currentdir,'index'), 'rw')
except:
    pass

if __name__ == '__main__':
    output=StringIO.StringIO()
    output.write('''
        好不容易在GAE上做了个网站（我爱记账网），某些地方访问已经被GFW了，
        真是的，咋就这么难呢！解决的方法是用OpenDNS的服务，
        将自己电脑的DNS第一个设为：208.67.222.222即可，ping 52jizhang.appspot.com是美国的IP， 
        但网站又不只是给自己用的，哪能让所有的用户都将自己的DNS全改了呢 ？
    ''')
    
    luceneIndexer([output], os.path.join(currentdir,'index'))





 
