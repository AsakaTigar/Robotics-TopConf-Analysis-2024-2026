import urllib.request, urllib.parse, json, time

titles = {
    'IE-016': 'Efficient Diffusion Policy via Progressive Latent Refinement',
    'IE-017': 'Anytime-RT: Anytime Vision-Language-Action Control with Controllable Compute Ceiling'
}
results = {}
for key, t in titles.items():
    time.sleep(3)
    q = urllib.parse.quote(t)
    url = 'https://api.semanticscholar.org/graph/v1/paper/search?query=' + q + '&limit=3&fields=title,year,venue,externalIds,authors'
    print('--- ' + key + ' ---')
    print('URL: ' + url)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TraeBot/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
        j = json.loads(data)
        total = j.get('total', 0)
        papers = j.get('data', [])
        print('total: ' + str(total) + ', hits_returned: ' + str(len(papers)))
        for p in papers:
            yr = p.get('year', '')
            ve = p.get('venue', '')
            ti = p.get('title', '')
            au = [a.get('name','') for a in p.get('authors', [])]
            print('  - [' + str(yr) + ' / ' + str(ve) + '] ' + str(ti))
            print('    authors: ' + str(au))
        results[key] = {'total': total, 'hits_returned': len(papers), 'papers': papers}
    except Exception as e:
        print('  ERROR: ' + str(e))
        results[key] = {'total': 0, 'hits_returned': 0, 'papers': [], 'error': str(e)}
    print()

with open('F:/oa/Robotics-TopConf-Analysis-2024-2026/scripts/tmp_ss_retry.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('saved')
