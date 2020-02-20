import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt

def removeStopwords(meal_component):
    if not pd.isna(meal_component):
        stop_words = set(stopwords.words('german'))

        tokens = word_tokenize(meal_component)
        filtered = [w for w in tokens if not w in stop_words]
        meal_component = ' '.join(filtered)
    
    return meal_component

def removeBrackets(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace(r"\s*\(.*\)\s*", "")
        meal_component = meal_component.replace("( ", "")
        meal_component = meal_component.replace(" )", "")
        meal_component = meal_component.replace(r"\s*\[.*\]\s*", "")
        meal_component = meal_component.replace(r"\s*\{.*\}\s*", "")
        return meal_component

def removeApostrophes(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace(r"\s*\(.*\)\s*", "")
        meal_component = meal_component.replace('"', "")
        meal_component = meal_component.replace("'", "")
        meal_component = meal_component.replace("`", "")
        meal_component = meal_component.replace('" ', "")
        meal_component = meal_component.replace("' ", "")
        meal_component = meal_component.replace("` ", "")
        meal_component = meal_component.replace(' "', "")
        meal_component = meal_component.replace(" '", "")
        meal_component = meal_component.replace(" `", "")
        return meal_component

def cleanSpaces(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace(r"- ", "-")
        meal_component = meal_component.replace(r" -", "-")
    return meal_component

def mealStemmer(meal_component):
    if not pd.isna(meal_component):
        stemmer = SnowballStemmer("german")
        return stemmer.stem(meal_component)

def bag_of_menu(data):
    # all menu components of one menu form one entry in the corpus
    data = data.dropna()
    menus = data.groupby(['date', 'meal_line'])['meal_component'].apply(lambda x: "%s" % ' '.join(x))
    corpus = pd.DataFrame(menus).meal_component
    print(corpus)
    # one-hot encode the menus 
    vectorizer = CountVectorizer()
    x =vectorizer.fit_transform(corpus).todense()
    print(x)
    # vectorizer.vocabulary_
    z = linkage(x)
    print(z)
    plt.figure()
    dn = dendrogram(z)
    plt.show()