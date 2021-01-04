# arXiv spider

A simple spider to crawl metadata of arxiv papers.

## Usage

### requirements

Python 3.5+

### Input arguments

Run `python3 arxiv_spider.py -h` to see help, or refer to the following table:

| argument | description | default |
|----------|-------------|---------|
| -s yymm      | start month (contain) | 0704    |
| -e yymm      | end month (contain) | 0704 |
| -m int | maximum number of metadata to be archived | 1073741824 (consider to be a large number like +INF) |
| -p int | processes used when downloading to accelerate | 1 |
| -r filename | download metadata of a list of arxiv_id specified by a file | | 
| -d arxiv_id | download the specified arxiv_id| |

### examples

* `python arxiv_spider.py -s 1001 -e 1010` download metadata of all papers submitted between Jan 2010 and Oct 2010
* `python arxiv_spider.py -s 1001 -e 1001 -m 1000` download metadata of first 100000 papers (ordered by submit time) submitted in Jan 2010
* `python arxiv_spider.py -d 0710.0010` download metadata of paper whose id is 0710.0010 (that is, the 10th paper in Oct 2007)
* `python arxiv_spider.py -r arxiv_ids.log` download metadata of papers specified by file `arxiv_ids.log`

The format of arxiv_id can be found [here](https://arxiv.org/help/arxiv_identifier).

The format of `arxiv_ids.log` is a file that contains a list of arxiv_ids separated by '\n', like
```text
2010.00005
1105.1432
...
0708.1234
```

Worth to mention that the program will log all arxiv_id that failed to download (due to network reason, for example) in `arxiv_download_error.log`, so run `python arxiv_spider.py -r arxiv_download_error.log` will retry all failed metadata downloading attempts.

## Output

The metadata will be stored in `metadata_yymmddhhmmss.json`.
The output format is identical to the official [arXiv Dataset](https://www.kaggle.com/Cornell-University/arxiv).
The metadata normally contains authors, abstract, title, submit time, doi(if there is), etc. More information on what was recorded can be seen [here](https://arxiv.org/help/bulk_data).

The arxiv_id of all failure attempts will be saved in `arxiv_download_error.log`


## Common reason of failure

The program uses arXiv Open Archives Initiative (OAI) interface to download data, which has a connection limit.
One common reason that cause the failure is the user requests the OAI too often.
The server will return 503 or reset the connection if one ip requests more than about 30000 times a day.
Thus, though the program supports multiprocessing to accelerate the download procedure, I highly recommend you to download with only one thread.

## license

The code in under MIT License, however, the metadata of arXiv may have other limitations.
It is nice to check these sites before using the metadata and obey the arXiv TOU.
* [arXiv Code of Conduct](https://arxiv.org/help/policies/code_of_conduct)
* [Terms of Use for arXiv APIs](https://arxiv.org/help/api/tou)