import os, sys
from pandas import DataFrame
import numpy
from optparse import OptionParser
import time
import urllib2
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.cross_validation import KFold
from time import gmtime, strftime
from bs4 import BeautifulSoup, Comment
import re

NEWLINE = '\n'
SKIP_FILES = set(['cmds'])
document_test_count = 0

###############################################################################
def make_list(text):
	if (text != ''):
		ar = re.findall(r"[a-zA-Z]+", text)
	else:
		return []
	y = [s for s in ar if len(s) > 2]
	return y
###############################################################################
# Fce pro nacteni trenovacich vzorku
def read_files(path):
  for root, dir_names, file_names in os.walk(path):
    for path in dir_names:
      read_files(os.path.join(root, path))
    if (len(file_names) > 100):
      file_names = file_names[:100]
    for file_name in file_names:
      if file_name not in SKIP_FILES:
        file_path = os.path.join(root, file_name)
        if os.path.isfile(file_path):
          past_header, lines = False, []
          f = open(file_path)
          text = f.read()
          f.close()
          yield file_path, text
###############################################################################
# Analyza HTML
def analyze_page(data):
	data = data.lower()
	data = data.replace('</scr" + nothing + "ipt>','')
	soup = BeautifulSoup(data, "lxml")
	to_extract = soup.findAll('script')
	[item.extract() for item in to_extract]
	to_extract = soup.findAll('style')
	[item.extract() for item in to_extract]
	to_extract = soup.findAll(text=lambda text:isinstance(text, Comment))
	[item.extract() for item in to_extract]

	title = []
	description = []
	keywords = []
	rating_html = []
	images_alt = []
	content = []

	# Knihovna beautifulSoup obcas pada, proto try, except
	# Seznam slov - titulek
	try:
		title = soup.title.string
		title.encode('utf-8')
		title = make_list(title)
	except:
		pass

	# Seznam slov - popisek
	try:
		description = soup.find("meta", {"name":"description"})['content']
		description = make_list(description)
	except:
		pass

	# Seznam slov - klicova slova
	try:
		keywords = soup.find("meta", {"name":"keywords"})['content']
		keywords = make_list(keywords)
	except:
		pass

	# Seznam slov - rating_in_html
	try:
		rating_html = soup.find("meta", {"name":"rating"})['content']
		rating_html = make_list(rating_html)
	except:
		pass

	# Seznam slov - popisky obrazku
	images_alt = []
	for image in soup.findAll("img"):
		image_all_alts = image.get('alt', '')
		if (image_all_alts != None):
			images_alt = images_alt + re.findall(r"[a-zA-Z]+", image_all_alts)
	
	# content z body
	if (soup.body):
		content = soup.body.get_text()
		content = make_list(content)

	structured_text = []
	
	if (rating_html):
		structured_text.append("ratingporn")
	for a in title:
		structured_text.append("CFTIT"+a)
	for a in description:
		structured_text.append("CFDESC"+a)
	for a in keywords:
		structured_text.append("CFKW"+a)
	for a in images_alt:
		structured_text.append("CFALT"+a)
	for a in content:
		structured_text.append(a)

	#print structured_text
	return "\n".join(structured_text)
###############################################################################
# Fce pro nacteni testovacich dokumentu
def getTestData(path):
  examples = []
  tmp_text = ""
  past_header, lines = False, []
  f = open("data_last/bad_structured/bad_porn/pixies_emporium_com")
  #f = open("data_last/ok_structured/ok_valid/strandshotel_com")
  tmp_text = f.read()
  f.close()
  examples.append(tmp_text)
  return examples
###############################################################################
def build_data_frame(path, classification):
  data_frame = DataFrame({'text': [], 'class': []})
  for file_name, text in read_files(path):
    data_frame = data_frame.append(
        DataFrame({'text': [text], 'class': [classification]}, index=[file_name]))
  return data_frame
###############################################################################
# Nacteni trenovacich dat klasifikatoru
def getData():
  HAM = 0
  SPAM = 1

  SOURCES = [
      ('data_last/bad_structured',	SPAM),
      ('data_last/ok_structured',	HAM),
      ]

  data = DataFrame({'text': [], 'class': []})
  for path, classification in SOURCES:
    data = data.append(build_data_frame(path, classification))

  return data
###############################################################################
# Fce pro vyhodnocen pres TP, FN, TN, FP a Fmeasure
def make_test(name, data, pipeline, examples):
  pipeline.fit(numpy.asarray(data['text']), numpy.asarray(data['class']))
  result = pipeline.predict(examples)
  return sum(result)
###############################################################################
# Fce
def main():

  site_data = ""
  if (len(sys.argv) == 2):
    #print sys.argv[1]
    url = sys.argv[1]
    site_data = urllib2.urlopen(url).read()

  if not (site_data):
    examples = getTestData("data_last/bad_structured")
  else:
    examples = [analyze_page(site_data)]

  examples_white = []

  document_test_count = 200
  data = getData()
  data = data.reindex(numpy.random.permutation(data.index))
    
  start_time = time.time()
  pipeline = Pipeline([('vectorizer',  TfidfVectorizer(stop_words='english')),('classifier',  MultinomialNB())])
  result = make_test("TF - MultinomialNB", data, pipeline, examples)
  if (result):
    print "Porn"
  else:
    print "Legit"
  #print time.time() - start_time
###############################################################################
if __name__ == "__main__":
  main()
  sys.exit()

