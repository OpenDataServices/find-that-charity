import urllib.request
import argparse
import zipfile
from bs4 import BeautifulSoup
import re
import bcp
import os

def main():
    parser = argparse.ArgumentParser(description='Fetch needed data sources.')
    parser.add_argument('--dual', type=str,
                        default='https://gist.github.com/drkane/22d62e07346084fafdcc7d9f5e1cd661/raw/bec666d1bc5c6efb8503a90f76ac0c6236ebc183/dual-registered-uk-charities.csv',
                        help='CSV with dual registered charities in')
    parser.add_argument('--oscr', type=str,
                        default=None, help="ZIP file containing Scottish charity data")
    parser.add_argument('--ccew', type=str,
                        default="http://data.charitycommission.gov.uk/", help="URL of page containing Charity Commission data")
    args = parser.parse_args()

    # retrieve dual registered charities
    urllib.request.urlretrieve(args.dual, "data/dual-registered-uk-charities.csv")
    print("[Dual] Dual registered charities fetched")

    # get oscr data
    if args.oscr:
        with zipfile.ZipFile(args.oscr) as oscrzip:
            files = oscrzip.infolist()
            if len(files)!=1:
                raise ValueError("More than one file in OSCR zip")
            with open("data/oscr.csv", "wb") as oscrcsv:
                oscrcsv.write(oscrzip.read(files[0]))
            print("[OSCR] data extracted")

    # get charity commission data
    ccew_html = urllib.request.urlopen(args.ccew)
    ccew_out = "data\ccew.zip"
    ccew_folder = "data\ccew"
    if ccew_html.status!=200:
        raise ValueError("[CCEW] Could not find Charity Commission data page. Status %s %s" % (ccew_data.status, ccew_data.reason))
    ccew_html = ccew_html.read()
    ccew_soup = BeautifulSoup(ccew_html, 'html.parser')
    zip_regex = re.compile("http://apps.charitycommission.gov.uk/data/.*?/RegPlusExtract.*?\.zip")
    ccew_data_url = ccew_soup.find("a", href=zip_regex)["href"]
    print("[CCEW] Using url: %s" % ccew_data_url)
    urllib.request.urlretrieve(ccew_data_url, ccew_out)
    print("[CCEW] ZIP downloaded")

    with zipfile.ZipFile(ccew_out) as ccew_zip:
        if not os.path.isdir(ccew_folder):
            os.makedirs(ccew_folder)
        for f in ccew_zip.infolist():
            bcp_content = ccew_zip.read(f)
            csv_content = bcp.convert(bcp_content.decode("latin1"))
            csv_filename = f.filename.replace(".bcp", ".csv")
            with open( os.path.join(ccew_folder, csv_filename), "w", encoding="latin1" ) as a:
                a.write(csv_content.replace('\x00', ''))
                print("[CCEW] write %s" % csv_filename)

    # @TODO get charity commission register of mergers

    # @TODO scrape Northern Ireland register of charities

if __name__ == '__main__':
    main()