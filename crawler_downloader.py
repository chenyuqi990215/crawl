#! python3
import crawler_functions
import string
from time import sleep
from copy import deepcopy
import requests

# CONSTANTS
CRAWL_PAUSE = 1
requests.adapters.DEFAULT_RETRIES = 5

from retrying import retry
import os

import collections
import pickle

general_log = crawler_functions.get_logger('Tropes_log')
error_log = crawler_functions.get_logger('Tropes_error')
candidate_log = crawler_functions.get_logger('Tropes_candidate')
redirect_log = crawler_functions.get_logger('Tropes_redirect')
link_log = crawler_functions.get_logger('Tropes_link')

@retry(stop_max_attempt_number=10000)
def working():
    error_log.info("Retrying...")
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
        redirect_list = []
        data = open('checked_redirected_trope_list.txt', 'r').readlines()
        for line in data:
            redirect_list.append(line.strip())

    else:
        subindex_list = collections.deque()
        closed_data = set()
        subindex_list.append(('Tropes', ['Tropes']))
        trope_list = []
        checked_trope_list = []
        redirect_list = []
        data = open('checked_missed_tropes.txt', 'r').readlines()
        for line in data:
            subindex_list.append((line.strip(), [line.strip()]))
            trope_list.append(line.strip())
        open('tropes_list.txt', 'w+')
        open('checked_trope_list.txt', 'w+')
        open('checked_redirected_trope_list.txt', 'w+')

    while len(subindex_list) > 0:
        subindex, path = subindex_list.popleft()
        link_log.info(f'{subindex}: {" -> ".join(path)}')
        if subindex in closed_data:
            continue

        general_log.info('Current subindex page: ' + subindex)
        page_src = crawler_functions.download_page_source(subindex, logging=general_log)
        sleep(CRAWL_PAUSE)

        # Subindexes
        current_page_subindex_list = crawler_functions.get_subindexes_from_index(
            page_src)  # gets subindexes from current page

        closed_data.add(subindex)

        if crawler_functions.check_not_found(page_src):
            error_log.info(f'Not found error: {subindex}')
        elif crawler_functions.check_redirect(page_src, only_score=True):
            redirect_list.append(subindex)
            redirect_index = crawler_functions.check_redirect(page_src, only_score=False)
            with open('checked_redirected_trope_list.txt', 'w+') as output_trope_list:
                redirect_log.info(f'Redirect Found: {subindex} Redirect To {redirect_index}')
                redirect_list = list(set(redirect_list))
                output_trope_list.write('\n'.join(sorted(redirect_list)))
        else:
            checked_trope_list.append(subindex)
            with open('checked_trope_list.txt', 'w') as output_trope_list:
                checked_trope_list = list(set(checked_trope_list))
                output_trope_list.write('\n'.join(sorted(checked_trope_list)))

        if current_page_subindex_list is None:
            error_log.info('IndexError for page: ' + subindex)
            continue
        
        filter_page_subindexes_list = []
        candidate_subindex_list = []
        total_candidates = crawler_functions.candidates(subindex)  # candidates: subindex/AToE
        
        for page_subindex in current_page_subindex_list:
            if page_subindex in total_candidates:
                candidate_subindex_list.append(page_subindex)
            elif len(page_subindex.split('/')) == 1 and crawler_functions.check_tropes(page_subindex):
                new_path = deepcopy(path) + [page_subindex]
                filter_page_subindexes_list.append((page_subindex, deepcopy(new_path)))

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
            new_path = deepcopy(path) + [tropes]
            subindex_list.append((tropes, deepcopy(new_path)))

        if len(candidate_tropes) > 0:
            candidate_log.info(f"Candidate Tropes: {subindex} -> {','.join(candidate_tropes)}")

        crawler_functions.catch_exception('A', current_tropes, subindex, logging=error_log)
        trope_list.extend(current_tropes)  # gets tropes

        # Write to file list of tropes
        with open('tropes_list.txt', 'w') as output_trope_list:
            trope_list = list(set(trope_list))
            output_trope_list.write('\n'.join(sorted(trope_list)))

        # Save for restore
        pickle.dump(subindex_list, open('checked_queue_tropes.pkl', 'wb'))
        pickle.dump(closed_data, open('checked_set_tropes.pkl', 'wb'))

working()