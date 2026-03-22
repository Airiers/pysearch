import spacy
import re

texte = "Actualités : OpenAI veut bâtir son propre GitHub, et ce n'est pas anodin"
texte2 = "Royaume-Uni : une controverse autour du projet de loi sur l’IA et le copyright"

nlp = spacy.load("fr_core_news_sm")

stopwords = {
    "être","avoir","faire","dire","aller",
    "probablement","encore","déjà","fini",
    "autour","contre","avec","sans"
}

def expand(title):

    # enlever citations et ponctuation forte
    title = re.sub(r"«.*?»", "", title)
    title = title.replace("Actualités :", "")

    doc = nlp(title)

    keywords = []

    for token in doc:

        if (
            token.pos_ in ["PROPN","NOUN"]  # noms propres ou noms
            and token.lemma_.lower() not in stopwords
            and len(token.text) > 2
        ):
            keywords.append(token.text)

    return " ".join(keywords[:5])

print(expand(texte))
print(expand(texte2))