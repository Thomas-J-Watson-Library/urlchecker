#!python
#
# Project:   seospidercli.py
# Usage  :   python seospidercli.py
# Author :   Michael Cummings
# Company:   Watson Library, Metropolitan Museum of Art
# Require:   Properties in Global configuration section below.
# Require:   Licensed copy of SEO Spider which has been configured to
#            just report Response Codes.
# Require:   Copy of dolist.bat, a Windows batch from this repository
#            which has been EDITED for local paths, located in this
#            directory.
# Require:   The user's Windows PATH includes Python and SEO Spider.
# Other  :   Be sure to read details in the README file found on
#            the github repository for this project.
# Date   :   January 2024

import sys
import os
import csv
import fnmatch
import subprocess
from random import randint

# ---------------------------------------
# CONSTANTS (See README file for detail)
# Do not change.
# ---------------------------------------
DATA_DIR = "data"
DATA_FILE = "sierra_urls.csv"
PART_FILE_PREFIX = "part"
RPT = "logfile.csv"
LINK_SUFFIX = "_links.csv"
# --------------------------------------
# Global configuration. Edit as needed.
# --------------------------------------
MAX_LINES_PER_FILE = 499
HTML_ERRORS_LIST = ['0', '401', '403', '404', '500', '501', '503']


def validate():
    try:
        os.chdir(DATA_DIR)
    except Exception as d:
        print("Start this script in parent directory of {DATA_DIR}. Exiting")
        exit(9)
    try:
        with open(DATA_FILE, 'r') as check:
            filefound = 'ok'
    except FileNotFoundError as e:
        print("Place your data csv file in directory {DATA_DIR}. Exiting.")
        exit(8)


def split_csv(input_file, output_prefix, max_lines,):
    # ------------------------------------------------------------------------
    # This function will break up a very large file, DATA_FILE, into multiple
    # files having MAX_LINES_PER_FILE. This is recommended rather than
    # sending SEO Spider batches of tens of thousands at once. The files
    # will have PART_FILE_PREFIX in their name.
    # ------------------------------------------------------------------------
    print('SEO SPIDER VIA CLI   :')
    current_file_num = 0
    current_lines = 0
    data_line = []
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if current_lines == max_lines:
                current_lines = 0
                with open(f'{output_prefix}_{current_file_num}.csv',
                          'w', newline='') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows(data_line)
                data_line = []
                current_file_num += 1
            data_line.append(row)
            current_lines += 1
    # -------------------------------------------------
    # Print remainder after breaking into smaller parts
    # -------------------------------------------------
    if data_line:
        with open(f'{output_prefix}_{current_file_num}.csv',
                  'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(data_line)


def extract_links(LINK_SUFFIX):
    # --------------------------------------------------------
    # This function creates another file for each segment of
    # the original file. The files created contain  ONLY the
    # URL column. The URL is the only thing SEO Spider accepts.
    # --------------------------------------------------------
    parts_list = fnmatch.filter(os.listdir(), 'part*')
    for part_name in parts_list:
        with open(part_name, 'rt', newline='') as csvfile:
            csv_in = csv.reader(csvfile)
            target_file = part_name.split('.')[0] + LINK_SUFFIX
            with open(target_file, 'w') as url_data:
                for row in list(csv_in):
                    print(row[1], file=url_data)


def submit_batches():
    # --------------------------------------------------------
    # This function passes the file or files containing lists
    # of links to SEO Spider via the command line interface.
    # It calls a separate Windows bat file, which contains
    # the full path to the code and data directory on this pc.
    # --------------------------------------------------------
    links_list = fnmatch.filter(os.listdir(), '*links.csv')
    os.chdir("..")
    for file_name in links_list:
        print('BEGIN PROCESSING FILE:', file_name)
        # ------------------------------------------------------------------
        # Pass the file to SEO Spider through a Windows batch file.
        # Each file may take minutes to process depending on the link count.
        # ------------------------------------------------------------------
        cmdCommand = "dolist.bat data\\" + file_name
        process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        #
        print('END PROCESSING FILE  :', file_name)
        # print(output)


def match_seo_bib():
    # ------------------------------------------------------------
    # This function saves a file containing  the Sierra bib id,
    # url, and html error response code reported by SEO Spider.
    # The url in the SEO Spider response files named *res* is
    # used as a matchpoint in files that contain bib ids and urls.
    # ------------------------------------------------------------
    os.chdir(DATA_DIR)
    seo_results = fnmatch.filter(os.listdir(), 'res*')
    for seo_filename in seo_results:
        # Find the corresponding .csv file to the current response file
        bib_no_prefix = seo_filename.replace('res_', '')
        bib_filename = bib_no_prefix.replace('_links.csv', '.csv')
        print(f"Matching between     : {seo_filename} and {bib_filename}.")
        # open the file with rows containing bib id and url. Make a list.
        with open(bib_filename, 'rt', newline='') as original_file:
            bib_list = list(csv.reader(original_file))
            # ... also open the SEO spider response
            with open(seo_filename, 'rt', newline='') as input_file:
                responses = csv.reader(input_file)
                # Look in SEO response file for specified HTML error codes.
                # Codes should be column three, or index[2] of each row.
                for rr in responses:
                    if rr[2] in HTML_ERRORS_LIST:
                        # Look  for a line  in the corresponding bib file
                        # matches the url of the error row
                        # e.g., res_part_0_links.txt and part_0.csv
                        for bib in bib_list:
                            # ------------------------------------------------
                            # DECOMMENT THESE TO VIEW/UNDERSTAND THE PROCESS
                            # print(f"INFO:bib, {bib}")
                            # print(f"INFO:bib[0],{bib[0]}")
                            # print(f"INFO:rr,{rr}")
                            # print(f"INFO:rr[0],{rr[0]}")
                            # print(f"INFO:rr[2],{rr[2]}")
                            # ------------------------------------------------
                            if {bib[1]} == {rr[0]}:
                                # print this on the console
                                lbl = "Logged link error    : "
                                print(f"{lbl}{bib[0]},{rr[0]},{rr[2]}")
                                # append to the log file
                                with open(f"{RPT}", "at", newline="\n") as L:
                                    print(f"{bib[0]},{rr[0]},{rr[2]}", file=L)
                    # else:


def cleanup():
    # ------------------------------------------------------------
    # This function saves a copy of the data file(s) and the file
    # that identifies bibs with bad links. The files are saved to
    # a directory named logid_NNNN where NNNN is a random number.
    # ------------------------------------------------------------
    print("\nSaving results.")
    backup_dir_no = randint(1000, 10000)
    os.mkdir("logid_"+str(backup_dir_no))
    cc_csv = f"copy .\\*.csv logid_"+str(backup_dir_no)+"\\"
    os.system(cc_csv)
    os.system("del .\\*.csv")
    #
    print(f"\nData files and log are saved in the directory ")
    print(f"named {DATA_DIR}\\logid_{backup_dir_no}. \n")
    print(f"{RPT} may be uploaded into Sierra CreateLists.")


if __name__ == '__main__':
    validate()
    # ----------------------------------------------
    # Stage 1: Split large file in manageable chunks.
    # Save results in *part*
    # ------------------------------------------------
    split_csv(DATA_FILE, PART_FILE_PREFIX, MAX_LINES_PER_FILE)
    parts_list = fnmatch.filter(os.listdir(), 'part_*')

    # ------------------------------------------------
    # Stage 2: Generate files containing only links.
    # Save results in *link*
    # ------------------------------------------------
    extract_links(LINK_SUFFIX)
    links_list = fnmatch.filter(os.listdir(), '*link*')

    # ------------------------------------------------
    # Stage 3: Send link files to SEO Spider via the
    # command line interface. Save results in *res*
    # ------------------------------------------------
    submit_batches()

    # ------------------------------------------------
    # Stage 4: Create one file of bib + links that have
    # error response codes found in HTML_ERRORS_LIST.
    # ------------------------------------------------
    match_seo_bib()

    # ------------------------------------------------
    # Stage 5: Archive the files from the current
    # run in a sub-directory.
    # ------------------------------------------------
    cleanup()

# EOF
