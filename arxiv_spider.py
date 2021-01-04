import os
import sys
import time

import requests
from argparse import ArgumentParser
import multiprocessing
from xml.dom.minidom import parseString
import json
import logging


def parse_metadata(xml_metadata, output_file):
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
    if len(xml_tree.getElementsByTagName('license')) == 0:
        license = None
    else:
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
    jsond = json.dumps(
        {'id': id, 'submitter': submitter, 'authors': authors, "title": title, "comments": comments, "doi": doi,
         "journal-ref": journal_ref, "report-no": report_no, "categories": categories, "license": license,
         "abstract": abstract, "versions": versions, "update_date": update_date,
         "authors_parsed": authors_parsed})
    with open(output_file, 'a+') as fout:
        fout.write(jsond + '\n')


def download_metadata(arxiv_id, output_file):
    try:
        xml_metadata = requests.get(
            "http://export.arxiv.org/oai2?verb=GetRecord&identifier=oai:arXiv.org:{0}&metadataPrefix=arXivRaw".format(
                arxiv_id),timeout=5).content.decode()
        if "idDoesNotExist" in xml_metadata:
            return
        parse_metadata(xml_metadata, output_file)
        print("INFO:arxiv_id {0} finish".format(arxiv_id))

        return
    except:
        print("ERROR:error in downloading metadata of arxiv_id {0}".format(arxiv_id))
        with open("arxiv_download_error.log", 'a+') as ferr:
            ferr.write("{0}\n".format(arxiv_id))


def parse_argument(args):
    parser = ArgumentParser()
    parser.add_argument("-s", "--start-yymm", type=str, default="0704",
                        help="The start (contain) year and month, in format yymm, like 1101 (rep Jan 2011)")
    parser.add_argument("-e", "--end-yymm", type=str, default="2012",
                        help="The end (contain) year and month, in format yymm, like 1101 (rep Jan 2011)")
    parser.add_argument("-m", "--maximum", type=int, default=1073741824,
                        help="Maximum metadata number. Specify this if you only want a small amount of metadata")
    parser.add_argument("-p", "--process", type=int, default=1,
                        help="Use multi-process to download.")
    parser.add_argument("-r", "--recover", type=str, default="",
                        help="Download some arxiv_id specified by file like arxiv_download_error.log")
    parser.add_argument("-d", "--download", type=str, default="",
                        help="Download the given arxiv_id only.")
    return parser.parse_args(args)


def id2month(i: int) -> int:
    a = (i - 101) % 12
    if a != 0:
        return a
    else:
        return 12


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args_dict = parse_argument(sys.argv[1:])
    download_arxiv_id_list = []
    try:
        raw_submit_number = requests.get("https://arxiv.org/stats/get_monthly_submissions").content.decode()
        submit_number = [int(x.split(',')[1]) for x in raw_submit_number.split()[1:]]
    except:
        logging.error("Fail to connect to arxiv. Please check your network status")
        exit(-1)
    if len(args_dict.download) > 1:
        download_arxiv_id_list.append(args_dict.download)
    elif len(args_dict.recover) > 1:
        with open(args_dict.recover, 'r') as fin:
            for i in fin.readlines():
                download_arxiv_id_list.append(i.strip())
    else:
        cnt = 0
        month_start = args_dict.start_yymm
        month_end = args_dict.end_yymm
        assert int(month_end) >= int(month_start)
        start_id = int(month_start[:2]) * 12 + int(month_start[2:]) + 101
        end_id = int(month_end[:2]) * 12 + int(month_end[2:]) + 101
        for i in range(start_id, end_id + 1):
            for j in range(1, submit_number[i] + 1):
                cnt += 1
                if cnt > args_dict.maximum:
                    break
                if i < 282:
                    download_arxiv_id_list.append("{:02}{:02}.{:04}".format((i - 102) // 12, id2month(i), j))
                else:
                    download_arxiv_id_list.append("{:02}{:02}.{:05}".format((i - 102) // 12, id2month(i), j))
    if not os.path.exists("arxiv_download_error.log"):
        with open("arxiv_download_error.log", 'w') as ferr:
            pass
    if args_dict.process > 1:
        logging.warning(
            "Please notice that terms of Use for arXiv APIs limited the maximum connection to 1 every 3 seconds.")
    pool = multiprocessing.Pool(processes=args_dict.process)
    output_file = "metadata_{0}.json".format(time.strftime("%y%m%d%H%M%S", time.localtime()))
    with open(output_file, 'w') as fout:
        pass
    for i in download_arxiv_id_list:
        pool.apply_async(download_metadata, (i, output_file,))
        time.sleep(3)
    pool.close()
    pool.join()
