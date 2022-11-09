file = open('/Users/cyq/Downloads/TVTropesData/lit_tropes.csv', 'r').readlines()
literatures = []
for line in file[1:]:
    try:
        int(line.strip().split(',')[0])
    except:
        continue
    if len(line.split(',')) <= 1:
        continue
    lit = line.split(',')[1]
    if not lit.isalpha():
        continue
    literatures.append(f'Literature/{lit}')

literatures = sorted(list(set(literatures)))
with open('literature_download.txt', 'w+') as f:
    f.write('\n'.join(literatures))

literatures = set(literatures)
crawler = set()

with open('literature_list.txt', 'r') as f:
    for line in f:
        crawler.add(line.strip())

with open('literature_missed.txt', 'w+') as f:
    missed = literatures - crawler
    f.write('\n'.join(missed))