import requests
import argparse
import multiprocessing
from xml.dom.minidom import parseString
import json
import logging


def parse_metadata(xml_metadata, queue):
    xml_tree = parseString(xml_metadata)
    id = xml_tree.getElementsByTagName('id')[0].childNodes[0].nodeValue
    submitter = xml_tree.getElementsByTagName('submitter')[0].childNodes[0].nodeValue
    authors = xml_tree.getElementsByTagName('authors')[0].childNodes[0].nodeValue
    title = xml_tree.getElementsByTagName('title')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('comments')) == 0:
        comments = None
    else:
        comments = xml_tree.getElementsByTagName('comments')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('doi')) == 0:
        doi = None
    else:
        doi = xml_tree.getElementsByTagName('doi')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('journal_ref')) == 0:
        journal_ref = None
    else:
        journal_ref = xml_tree.getElementsByTagName('journal-ref')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('report_no')) == 0:
        report_no = None
    else:
        report_no = xml_tree.getElementsByTagName('report-no')[0].childNodes[0].nodeValue
    categories = xml_tree.getElementsByTagName('categories')[0].childNodes[0].nodeValue
    license = xml_tree.getElementsByTagName('license')[0].childNodes[0].nodeValue
    abstract = xml_tree.getElementsByTagName('abstract')[0].childNodes[0].nodeValue
    raw_versions = xml_tree.getElementsByTagName('version')
    versions = []
    for index, i in enumerate(raw_versions):
        versions.append({'version': "v{0}".format(index), 'created': i.childNodes[0].childNodes[0].nodeValue})
    update_date = xml_tree.getElementsByTagName('datestamp')[0].childNodes[0].nodeValue
    authors_parsed = []
    proc_a = authors.replace('\n', '').replace(' and ', '').replace(',and ', '')
    for i in proc_a.split(','):
        tmp = i.strip().split()
        if len(tmp) == 0:
            authors_parsed.append(["", "", ""])
        if len(tmp) == 1:
            authors_parsed.append([i.strip().split()[0].strip(), '', ''])
        if len(tmp) == 2:
            authors_parsed.append([i.strip().split()[0].strip(), i.strip().split()[1].strip(), ''])
        if len(tmp) > 2:
            authors_parsed.append(
                [i.strip().split()[0].strip(), i.strip().split()[1].strip(), i.strip().split()[2].strip()])
    queue.append(
        {'id': id, 'submitter': submitter, 'authors': authors, "title": title, "comments": comments, "doi": doi,
         "journal_ref": journal_ref, "report_no": report_no, "categories": categories, "license": license,
         "abstract": abstract, "versions": versions, "update_date": update_date,
         "authors_parsed": authors_parsed})


def download_metadata(arxiv_id, queue):
    try:
        xml_metadata = requests.get(
            "http://export.arxiv.org/oai2?verb=GetRecord&identifier=oai:arXiv.org:{0}&metadataPrefix=arXivRaw".format(
                arxiv_id)).content.decode()
        if "idDoesNotExist" in xml_metadata:
            return
        parse_metadata(metadata_list, queue)
        logging.info("arxiv_id {0} finish".format(arxiv_id))
        return
    except:
        logging.error("error in downloading metadata of arxiv_id {0}".format(arxiv_id))
        with open("arxiv_download_error.log", 'a+') as ferr:
            ferr.write("{0}\n".format(arxiv_id))


if __name__ == "__main__":
    with open("arxiv_download_error.log", 'w') as ferr:
        pass
    pool = multiprocessing.Pool(processes=4)
    manager = multiprocessing.Manager()
    metadata_list = manager.list()
    for i in range(20, 21):
        for j in range(10, 13):
            for k in range(1, 18000):
                id = "{:02}{:02}.{:05}".format(i, j, k)
                # download_metadata("{:02}{:02}.{:05}".format(i, j, k), metadata_list)
                pool.apply_async(download_metadata, (id, metadata_list,))
    pool.close()
    pool.join()
    with open("out.json", 'w') as fout:
        json.dump(list(metadata_list), fout)
