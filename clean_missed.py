import crawler_functions
import tqdm

f = open('./checked_missed_tropes.txt', 'r').readlines()
out = open('./checked_cleaned_missed_tropes.txt', 'w+')
for line in tqdm.tqdm(f):
    item = line.strip()
    page_src = crawler_functions.download_page_source(item)
    if crawler_functions.check_not_found(page_src):
        continue
    if crawler_functions.get_subindexes_from_index(page_src) is None:
        continue
    flag, redirect = crawler_functions.check_redirect(page_src)
    if flag:
        out.write(f'{redirect}\n')
    else:
        out.write(f'{item}\n')
