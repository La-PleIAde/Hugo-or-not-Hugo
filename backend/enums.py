from enum import Enum


class AgeInterval(str, Enum):
    _17_or_less = "17 ans ou moins"
    _18_20 = "18-20"
    _21_29 = "21-29"
    _30_39 = "30-39"
    _40_49 = "40-49"
    _50_59 = "50-59"
    _60_or_more = "60 ans ou plus"


class EducationLevel(str, Enum):
    _under_secondary = "Inférieur au diplôme d'études secondaires"
    _secondary = "Diplôme d'études secondaires ou équivalent"
    _no_degree = " A fait des études supérieures, mais pas de diplôme"
    _technical = "DUT/BTS"
    _graduate = "Licence"
    _postgraduate = "Diplôme d’études supérieures (master, doctorat...)"


class HugoStyleFamiliarity(str, Enum):
    _1 = "Très peu familier"
    _2 = "Peu familier"
    _3 = "Neutre"
    _4 = "Un peu familier"
    _5 = "Très familier"


class ParagraphCategory(str, Enum):
    hugo = "hugo_paragraphs"
    other = "other_paragraphs"

    other2hugo = "other2hugo"
    neutralized = "hugo2neutral"
    restored = "restored_hugo"


class Author(str, Enum):
    genai = "Généré par l'IA"

    hugo = "Victor Hugo"

    colette = "Colette"
    daudet = "Alphonse Daudet"
    dumas = "Alexandre Dumas"
    maupassant = "Guy de Maupassant"
    verne = "Jules Verne"
    zola = "Émile Zola"


class QuestionCategory(str, Enum):
    A = "Hugo VS Other"
    B = "Hugo VS Neutralized"
    C = "Hugo VS Other2Hugo"
    D = "Hugo VS Restored"
    E = "Irrelevant"


class Choice(str, Enum):
    left = "left"
    right = "right"
