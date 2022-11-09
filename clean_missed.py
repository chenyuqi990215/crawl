import crawler_functions
import tqdm

f = open('./literature_missed.txt.txt', 'r').readlines()
out = open('./checked_cleaned_missed_literatures.txt', 'w+')
for line in tqdm.tqdm(f):
    item = line.strip()
    page_src = crawler_functions.download_page_source(item)
    if crawler_functions.check_not_found(page_src):
        continue
    out.write(f'{item}\n')
