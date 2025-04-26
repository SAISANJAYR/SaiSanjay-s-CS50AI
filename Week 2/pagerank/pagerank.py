import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pd = dict()
    if not corpus[page]:
        for p in corpus:
            pd[p] = 1/len(corpus)
    else:
        for i in corpus:
            if i in corpus[page]:
                pd[i] = damping_factor/len(corpus[page]) + (1-damping_factor)/len(corpus)
            else:
                pd[i] = (1-damping_factor)/len(corpus)

    return pd


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    counts = {page: 0 for page in corpus}
    sample_page = random.choice(list(corpus.keys()))
    counts[sample_page] += 1
    for _ in range(n-1):
        pd = transition_model(corpus, sample_page, damping_factor)
        sample_page = random.choices(list(pd.keys()), weights=pd.values(), k=1)[0]
        counts[sample_page] += 1
    #print("Fuck you!!!")
    for page in counts:
        counts[page] /= n

    return counts


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    threshold = 0.001
    pd = dict()
    for p in corpus:
        pd[p] = 1/len(corpus)  # initial rank for all pages
    while True:
        new_pd = dict()
        for page in corpus:
            new_pd[page] = (1 - damping_factor) / len(corpus)

            # Handling pages with no links as linking to all pages
            for linking_page in corpus:
                if not corpus[linking_page]:
                    new_pd[page] += damping_factor * pd[linking_page] / len(corpus)
                elif page in corpus[linking_page]:
                    new_pd[page] += damping_factor * pd[linking_page] / len(corpus[linking_page])

        # Convergence check
        diff = max(abs(new_pd[page] - pd[page]) for page in pd)
        if diff < threshold:
            break

        pd = new_pd

    return pd


if __name__ == "__main__":
    main()
