import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize

class DataPreprocessor:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

    def normalize(self, text):
        # إزالة التكرار الزائد وتوحيد الكلمات (مثال: sooo => so)
        text = re.sub(r"(.)\1{2,}", r"\1\1", text)  # الحرف المتكرر أكثر من مرتين إلى مرتين فقط
        return text

    def preprocess(self, text):
        # 1. Lowercase
        text = text.lower()

        # 2. Remove special characters and digits
        text = re.sub(r"[^a-z\s]", "", text)

        # 3. Normalize repeated letters
        text = self.normalize(text)

        # 4. Tokenize
        tokens = word_tokenize(text)

        # 5. Remove stopwords
        tokens = [word for word in tokens if word not in self.stop_words]

        # 6. Lemmatization
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]

        # 7. Stemming
        tokens = [self.stemmer.stem(word) for word in tokens]

        return " ".join(tokens)

    def preprocess_documents(self, documents):
        """
        الوثائق المدخلة بصيغة [(doc_id, text)]
        ترجع [(doc_id, original_text, processed_text)]
        """
        processed = []
        for doc_id, text in documents:
            try:
                cleaned = self.preprocess(text)
                processed.append((doc_id, text, cleaned))
            except Exception as e:
                print(f"❌ Error processing doc {doc_id}: {e}")
        return processed
