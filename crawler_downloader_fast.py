#! python3
import crawler_functions
import string
from time import sleep
from copy import deepcopy
import requests

# CONSTANTS
CRAWL_PAUSE = 0.5
requests.adapters.DEFAULT_RETRIES = 5

import os

import collections
import pickle

general_log = crawler_functions.get_logger('Tropes_log')
error_log = crawler_functions.get_logger('Tropes_error')
candidate_log = crawler_functions.get_logger('Tropes_candidate')

def working():
    # restore information
    if os.path.exists('checked_queue_tropes.pkl'):
        subindex_list = pickle.load(open('checked_queue_tropes.pkl', 'rb'))
        closed_data = pickle.load(open('checked_set_tropes.pkl', 'rb'))
        trope_list = []
        data = open('tropes_list.txt', 'r').readlines()
        for line in data:
            trope_list.append(line.strip())
        checked_trope_list = []
        data = open('checked_trope_list.txt', 'r').readlines()
        for line in data:
            checked_trope_list.append(line.strip())
    else:
        subindex_list = collections.deque()
        closed_data = set()
        subindex_list.append('Tropes')
        trope_list = []
        checked_trope_list = []

    while len(subindex_list) > 0:
        subindex = subindex_list.popleft()
        if subindex in closed_data:
            continue

        general_log.info('Current subindex page: ' + subindex)
        page_src = crawler_functions.download_page_source(subindex, logging=general_log)
        sleep(CRAWL_PAUSE)

        # Subindexes
        try:
            current_page_subindex_list = crawler_functions.get_subindexes_from_index(
                page_src)  # gets subindexes from current page
        except:
            continue

        closed_data.add(subindex)

        if crawler_functions.check_not_found(page_src):
            error_log.info(f'Not found error: {subindex}')
        else:
            checked_trope_list.append(subindex)

        if current_page_subindex_list is None:
            error_log.info('IndexError for page: ' + subindex)
            continue

        filter_page_subindexes_list = []
        candidate_subindex_list = []
        total_candidates = crawler_functions.candidates(subindex)  # candidates: subindex/AToE

        for page_subindex in current_page_subindex_list:
            if page_subindex in total_candidates:
                candidate_subindex_list.append(page_subindex)
            elif len(page_subindex.split('/')) == 1:
                filter_page_subindexes_list.append(page_subindex)

        current_page_subindex_list = deepcopy(filter_page_subindexes_list)

        if len(candidate_subindex_list) > 0:
            candidate_log.info(f"Candidate Subindex: {subindex} -> {','.join(candidate_subindex_list)}")

        for current_page_subindex in current_page_subindex_list:
            subindex_list.append(current_page_subindex)

        # Tropes
        current_tropes = crawler_functions.get_tropes_from_page(page_src)

        filter_tropes = []
        candidate_tropes = []
        for tropes in current_tropes:
            if tropes in total_candidates:
                candidate_tropes.append(tropes)
            elif len(tropes.split('/')) == 1 and crawler_functions.check_tropes(tropes):
                filter_tropes.append(tropes)

        current_tropes = deepcopy(filter_tropes)

        for tropes in current_tropes:
            subindex_list.append(tropes)

        if len(candidate_tropes) > 0:
            candidate_log.info(f"Candidate Tropes: {subindex} -> {','.join(candidate_tropes)}")

        crawler_functions.catch_exception('A', current_tropes, subindex, logging=error_log)
        trope_list.extend(current_tropes)  # gets tropes

    with open('checked_trope_list.txt', 'w') as output_trope_list:
        checked_trope_list = list(set(checked_trope_list))
        output_trope_list.write('\n'.join(sorted(checked_trope_list)))

    # Write to file list of tropes
    with open('tropes_list.txt', 'w') as output_trope_list:
        trope_list = list(set(trope_list))
        output_trope_list.write('\n'.join(sorted(trope_list)))

working()