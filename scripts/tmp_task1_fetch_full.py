import urllib.request
import xml.etree.ElementTree as ET
import json
import sys

ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom'}

def fetch_arxiv_ids(id_list):
    ids = ','.join(id_list)
    url = f"http://export.arxiv.org/api/query?id_list={ids}"
    print(f"[FETCH] {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'TraeEvidenceBot/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode('utf-8')
    return data

def extract_entries(xml_data):
    root = ET.fromstring(xml_data)
    entries = []
    for entry in root.findall('atom:entry', ATOM_NS):
        d = {}
        id_el = entry.find('atom:id', ATOM_NS)
        d['id'] = id_el.text if id_el is not None else ''
        title_el = entry.find('atom:title', ATOM_NS)
        d['title'] = ' '.join((title_el.text or '').split()) if title_el is not None else ''
        summary_el = entry.find('atom:summary', ATOM_NS)
        d['summary'] = ' '.join((summary_el.text or '').split()) if summary_el is not None else ''
        authors = []
        for a in entry.findall('atom:author', ATOM_NS):
            name = a.find('atom:name', ATOM_NS)
            if name is not None and name.text:
                authors.append(name.text.strip())
        d['authors'] = authors
        d['authors_str'] = '; '.join(authors)
        published = entry.find('atom:published', ATOM_NS)
        d['published'] = published.text if published is not None else ''
        entries.append(d)
    return entries

def search_arxiv_title(title, max_results=3):
    import urllib.parse
    q = f"ti:\"{title}\""
    url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(q)}&max_results={max_results}"
    print(f"[SEARCH-TI] {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TraeEvidenceBot/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
        root = ET.fromstring(data)
        total = root.find('atom:totalResults', ATOM_NS)
        total_count = int(total.text) if total is not None else 0
        entries = extract_entries(data)
        return {
            'query': q,
            'totalResults': total_count,
            'hits_returned': len(entries),
            'top_entry': entries[0] if entries else None,
            'all_titles': [e['title'] for e in entries]
        }
    except Exception as e:
        return {'query': q, 'error': str(e), 'totalResults': 0, 'hits_returned': 0, 'top_entry': None, 'all_titles': []}

def search_semantic_scholar(title, limit=3):
    import urllib.parse
    q = urllib.parse.quote(title)
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit={limit}&fields=title,year,venue,externalIds,authors"
    print(f"[SEARCH-SS] {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TraeEvidenceBot/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
        j = json.loads(data)
        total = j.get('total', 0)
        papers = j.get('data', [])
        top = papers[0] if papers else None
        return {
            'total': total,
            'hits_returned': len(papers),
            'top_entry': {
                'title': top.get('title', '') if top else '',
                'year': top.get('year', '') if top else '',
                'venue': top.get('venue', '') if top else '',
                'externalIds': top.get('externalIds', {}) if top else {},
                'authors': [a.get('name','') for a in top.get('authors',[])] if top else []
            } if top else None,
            'all_titles': [p.get('title','') for p in papers]
        }
    except Exception as e:
        return {'error': str(e), 'total': 0, 'hits_returned': 0, 'top_entry': None, 'all_titles': []}

def main():
    results = {}

    print("=" * 60)
    print("STEP 1: Fetch full abstracts for IE-014 and IE-015")
    print("=" * 60)
    xml = fetch_arxiv_ids(['2505.08243', '2601.09708'])
    entries = extract_entries(xml)
    for e in entries:
        aid = e['id'].split('/abs/')[-1]
        e['summary_len'] = len(e['summary'])
        print(f"\n--- {aid} ---")
        print(f"Title: {e['title']}")
        print(f"Authors: {e['authors_str']}")
        print(f"Summary length: {e['summary_len']} chars")
        if e['summary_len'] >= 900:
            print(f"  [OK] >= 900 chars requirement satisfied")
        else:
            print(f"  [WARN] < 900 chars")
        print(f"Published: {e['published']}")
        results[aid] = e

    print("\n" + "=" * 60)
    print("STEP 2: arXiv title search for IE-016 / IE-017")
    print("=" * 60)
    titles = {
        'IE-016': "Efficient Diffusion Policy via Progressive Latent Refinement",
        'IE-017': "Anytime-RT: Anytime Vision-Language-Action Control with Controllable Compute Ceiling"
    }
    search_results = {}
    for key, t in titles.items():
        print(f"\n--- {key} arXiv ti search ---")
        arxiv_res = search_arxiv_title(t)
        print(f"  totalResults: {arxiv_res['totalResults']}")
        print(f"  hits_returned: {arxiv_res['hits_returned']}")
        print(f"  all titles: {arxiv_res['all_titles']}")

        print(f"\n--- {key} Semantic Scholar ---")
        ss_res = search_semantic_scholar(t)
        print(f"  total: {ss_res['total']}")
        print(f"  hits_returned: {ss_res['hits_returned']}")
        if ss_res['top_entry']:
            te = ss_res['top_entry']
            print(f"  top title: {te['title']}")
            print(f"  top year/venue: {te['year']} / {te['venue']}")
            print(f"  top authors: {te['authors']}")
        print(f"  all titles: {ss_res['all_titles']}")

        authoritative_sources = (1 if arxiv_res['totalResults'] > 0 else 0) + (1 if ss_res['hits_returned'] > 0 else 0)
        decision = 'pending_verification' if authoritative_sources < 2 else 'ok'
        search_results[key] = {
            'title': t,
            'arxiv': arxiv_res,
            'semantic_scholar': ss_res,
            'source_c': {'status': 'not searched (cost / auth-free search unavailable)'},
            'authoritative_sources': authoritative_sources,
            'decision': decision
        }
        print(f"  authoritative_sources = {authoritative_sources} → DECISION = {decision}")

    results['abstracts'] = {k: v for k, v in results.items() if k in ('2505.08243', '2601.09708')}
    results['searches'] = search_results

    out_path = "F:/oa/Robotics-TopConf-Analysis-2024-2026/scripts/tmp_task1_fetch_full_output.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Output written to {out_path}")

if __name__ == '__main__':
    main()
