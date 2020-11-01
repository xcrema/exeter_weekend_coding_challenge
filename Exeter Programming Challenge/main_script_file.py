# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# importing various modules to use
from urllib.parse import urlparse, urljoin
import re
from requests import get
from bs4 import BeautifulSoup, Comment
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# %%
# input user given url. it can be homepage or innerpage url
url = input()

# %% [markdown]
# Feature 1:

# %%
# if user entered innerpage url then parse the domain page url
parsed_uri = urlparse(url)
homepage = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
print(homepage)

# %% [markdown]
# Feature 2:

# %%
# defing the header for request because some websites doesn't allow web crawling(like https://www.garyvaynerchuk.com)
hdr = ({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
req = get(homepage, headers=hdr)
# using beautifulsoup to parse the webpage content
soup = BeautifulSoup(req.text, 'html.parser')
result = [homepage.rstrip('/')]
# defining regex to store only valid urls
regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
# if the webpage is an image webpage then we have to ommit that page
image_url = """\.jpg\Z|\.jpeg\Z|\.jpe\Z|\.jif\Z|\.jfif\Z|\.jfi\Z|
            \.png\Z|\.gif\Z|\.webp\Z|\.tiff\Z|\.tif\Z|\.psd\Z|
            \.raw\Z|\.arw\Z|\.cr2\Z|\.nrw\Z|\.k25\Z|\.bmp\Z|\.dib\Z|
            \.heif\Z|\.heic\Z|\.ind\Z|\.indd\Z|\.indt\Z|\.jp2\Z|
            \.j2k\Z|\.jpf\Z|\.jpx\Z|\.jpm\Z|\.mj2\Z|\.svg\Z|\.svgz\Z|
            \.ai\Z|\.eps\Z|\.pdf\Z"""
# finding all the valid urls and storing them into result list
for link in soup.findAll('a'):
    temp_url = urljoin(homepage, link.get('href')).rstrip('/')
    if re.match(regex, temp_url) is not None:
        if re.search(image_url, temp_url) is None:
            result.append(temp_url)

# %% [markdown]
# Feature 3:

# %%
# storing the valid and unique urls into homepage_urls list
homepage_urls = list(set(result))
homepage_urls

# %% [markdown]
# Feature 4:

# %%
all_text = ""  # it containg the data of all the visited webpages
url_titles = list()  # it contains the url titles of all visited webpages for later usage
meta_data = {}  # it containg the meta data of webpages
webpage_size = {}  # it contains the size of visited vebpages
# comments contains all the comments present in webpage
comments = soup.find_all(string=lambda text: isinstance(text, Comment))
for url in homepage_urls:
    print(url)
    try:
        # opening each top level webpages
        html_page = get(url, headers=hdr)
        soup = BeautifulSoup(html_page.text, 'html.parser')
        # storing the webpage size
        webpage_size[url] = len(html_page.text)
        if(soup.title is not None):
            try:
                # storing the webpage title
                url_titles.append(soup.title.string)
                text = soup.find_all(text=True)
                output = ''
                # storing the content of the webpage decoposing the script, style and comments present in webpage
                for t in text:
                    if t.parent.name not in ['script', 'style']:
                        if t not in comments:
                            output += '{} '.format(t)
                all_text += output
                # storing the meta data of the webpage in dataframe format
                meta_data_of_url = pd.DataFrame(columns=["name", "content", "http-equiv", "charset"])
                meta_tag = soup.findAll('meta')
                for x in meta_tag:
                    dic = {"name": "", "content": "", "http-equiv": "", "charset": ""}
                    for key, value in x.attrs.items():
                        if key in dic.keys():
                            dic[key] = value
                    meta_data_of_url = meta_data_of_url.append(dic, ignore_index=True)
                meta_data[url] = meta_data_of_url
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


# %%
lines = (line.strip() for line in all_text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split())
# drop blank lines
all_text = ' '.join(chunk for chunk in chunks if chunk)
# removing the punctuations present in the data
all_text = re.sub(r'[^\w\s]', '', all_text)
all_text = (all_text.lower()).strip()


# %%
# removing the stopwords present in webpages because stopwords like is, the, a, an, etc are of no use in analysis of bigrams and trigrams
stop_words = set(stopwords.words('english'))
word_tokens = word_tokenize(all_text)
all_text = [w for w in word_tokens if not w in stop_words]
all_text = " ".join(all_text)

# %% [markdown]
# Feature 5:

# %%
# generating bi-grams from the stored content


def getNGrams(n_gram):
    temp_gram = list()
    temp = all_text.split()
    if(n_gram == "bi_gram"):
        t1 = 1
        t2 = 2
    if(n_gram == "tri_gram"):
        t1 = 2
        t2 = 3
    for x in range(0, len(temp)-t1):
        st = ""
        for y in range(x, x+t2):
            st = st+temp[y]+" "
        st = st.strip()
        temp_gram.append(st)
    return temp_gram


bi_gram = getNGrams("bi_gram")
tri_gram = getNGrams("tri_gram")
print(bi_gram)
print(tri_gram)

# %% [markdown]
# Outputs:

# %%
with open('output.txt', 'w', encoding="utf-8") as file:
    # writing number of top level pages present in homepage
    file.write("The number of top level pages are "+str(len(homepage_urls)))
    # writing top level page titles in file
    file.write("\n\n\n<----- Page Titles of Top level Pages ----->")
    all_urls = set(url_titles)
    x = 1
    for i in all_urls:
        file.write("\n%d %s" % (x, i.strip()))
        x += 1
    """
    file.write("\n\n\n<----- Meta Data of Each top table page ----->")

    for key, value in meta_data.items():
        file.write("\n\nURL:->%s\n"%key)
        file.write(str(value.values))
    """
# writing metadata content in metadata.csv file
for key, value in meta_data.items():
    with open('metadata.csv', 'a', encoding="utf-8") as file:
        file.write("\n\n"+str(key)+"\n\n")
    value.to_csv('metadata.csv', mode="a")


# %%
internal_links = list()  # storing internal links
external_links = list()  # storing external links
for url in homepage_urls:
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain == homepage:
        internal_links.append(url)
    else:
        external_links.append(url)


# %%
with open('output.txt', 'a', encoding="utf-8") as file:
    # writing internal links in the file
    file.write("\n\n\n<----- Internal Links ----->")
    x = 1
    for url in internal_links:
        file.write("\n%d %s" % (x, url.strip()))
        x += 1
    # writing external links in the file
    file.write("\n\n\n<----- External Links ----->")
    x = 1
    for url in external_links:
        file.write("\n%d %s" % (x, url.strip()))
        x += 1


# %%
# function to get top 20 words of the bi-gram and tri-gram generated
def getTopWords(n_gram):
    dic_gram = {}
    for i in n_gram:
        if i in dic_gram.keys():
            dic_gram[i] = dic_gram.get(i)+1
        else:
            dic_gram[i] = 1
    counts = {k: v for k, v in sorted(dic_gram.items(), key=lambda x: x[1], reverse=True)}
    top_grams = {}
    count = 0
    for key, value in counts.items():
        if count == 20:
            break
        else:
            top_grams[key] = value
        count = count+1
    return top_grams


# calling and storing top 20 words of bigrams and trigrams each
top_bigrams = getTopWords(bi_gram)
top_trigrams = getTopWords(tri_gram)


# %%
with open('output.txt', 'a', encoding="utf-8") as file:
    # writing top 20 bigrams in file
    file.write("\n\n\n<----- Top 20 Bi-Grams ----->")
    x = 1
    for key, value in top_bigrams.items():
        file.write("\n%d) %s %d" % (x, key, value))
        x += 1
    # writing top 20 trigrams in file
    file.write("\n\n\n<----- Top 20 Tri-Grams ----->")
    x = 1
    for key, value in top_trigrams.items():
        file.write("\n%d) %s %d" % (x, key, value))
        x += 1
    # writing webpage size of each top level pages
    file.write("\n\n\n<----- Webpage Size ----->")
    x = 1
    for key, value in webpage_size.items():
        file.write("\n%d) %s \t ..... \t %d" % (x, key, value))
        x += 1
    # writing min webpage size
    file.write("\n\n\n<----- Minimum Webpage Size ----->")
    file.write("\n%d" % min(list(webpage_size.values())))
    # writing max webpage size
    file.write("\n\n\n<----- Maximum Webpage Size ----->")
    file.write("\n%d" % max(list(webpage_size.values())))
    # writing average webpage size
    file.write("\n\n\n<----- Average Webpage Size ----->")
    file.write("\n%d" % (sum(list(webpage_size.values()))/len(webpage_size.values())))
