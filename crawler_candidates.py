import collections
import crawler_functions
from time import sleep
from copy import deepcopy
# CONSTANTS
CRAWL_PAUSE = 1

candidate_log = crawler_functions.get_logger('Candidate_log')


data = open('Tropes_candidate.log', 'r').readlines()
index_list = collections.deque()
for line in data:
    indexs = line.split('->')[1]
    index_list.extend(indexs.strip().split(','))


checked_trope_list = []
data = open('checked_trope_list.txt', 'r').readlines()
for line in data:
    checked_trope_list.append(line.strip())

closed_data = set(checked_trope_list)

subindex_list = collections.deque()
candidate_new_trope_list = []
while len(index_list) > 0:
    index = index_list.popleft()

    candidate_log.info('Current index page: ' + index)
    page_src = crawler_functions.download_page_source(index, '', logging=candidate_log)
    sleep(CRAWL_PAUSE)

    # Subindexes
    current_page_trope_list = crawler_functions.get_tropes_from_page(page_src)
    if current_page_trope_list is None:
        candidate_log.info('IndexError for page: ' + index)
        continue

    for current_page_trope in current_page_trope_list:
        if len(current_page_trope.split('/')) == 1 and crawler_functions.check_tropes(current_page_trope):
            if current_page_trope not in checked_trope_list:
                subindex_list.append(current_page_trope)
                candidate_log.info('find: ' + current_page_trope)
            else:
                candidate_log.info('hit: ' + current_page_trope)
        else:
            candidate_log.info('invalid: ' + current_page_trope)


while len(subindex_list) > 0:
    subindex = subindex_list.popleft()
    if subindex in closed_data:
        continue

    candidate_log.info('Current index page: ' + subindex)
    page_src = crawler_functions.download_page_source(subindex, logging=candidate_log)
    sleep(CRAWL_PAUSE)
    closed_data.add(subindex)

    # Subindexes
    current_page_subindex_list = crawler_functions.get_subindexes_from_index(
        page_src)  # gets subindexes from current page

    if crawler_functions.check_not_found(page_src):
        candidate_log.info(f'Not found error: {subindex}')
    else:
        checked_trope_list.append(subindex)
        candidate_new_trope_list.append(subindex)
        with open('candidate_new_trope_list.txt', 'w') as output_trope_list:
            candidate_new_trope_list = list(set(candidate_new_trope_list))
            output_trope_list.write('\n'.join(sorted(candidate_new_trope_list)))

    if current_page_subindex_list is None:
        candidate_log.info('IndexError for page: ' + subindex)
        continue

    filter_page_subindexes_list = []
    candidate_subindex_list = []
    total_candidates = crawler_functions.candidates(subindex)  # candidates: subindex/AToE

    for page_subindex in current_page_subindex_list:
        if page_subindex in total_candidates:
            candidate_subindex_list.append(page_subindex)
        elif len(page_subindex.split('/')) == 1 and crawler_functions.check_tropes(page_subindex):
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


