class PorterStemmerRU:
    """Алгоритм стемминга Портера для русского языка"""

    def __init__(self):
        self.vowel = 'аеиоуыэюя'
        self.perfectiveground = ['в', 'вши', 'вшись']
        self.reflexive = ['сь', 'ся']
        self.adjective = ['ее', 'ие', 'ые', 'ое', 'ими', 'ыми', 'ей', 'ий', 'ой', 'ем', 'им', 'ым', 'ом', 'его', 'ого',
                          'ему', 'ому', 'их', 'ых', 'ую', 'юю', 'ая', 'яя', 'ою', 'ею']
        self.participle = ['ем', 'нн', 'вш', 'ющ', 'щ']
        self.verb = ['ила', 'ыла', 'ена', 'ейте', 'уйте', 'ите', 'или', 'ыли', 'ей', 'уй', 'ил', 'ыл', 'им', 'ым', 'ен',
                     'ило', 'ыло', 'ено', 'ят', 'ует', 'уют', 'ит', 'ыт', 'ены', 'ить', 'ыть', 'ишь', 'ую', 'ю']
        self.noun = ['а', 'ев', 'ов', 'ие', 'ье', 'е', 'иями', 'ями', 'ами', 'еи', 'ии', 'и', 'ией', 'ей', 'ой', 'ий',
                     'й', 'иям', 'ям', 'ием', 'ем', 'ам', 'ом', 'о', 'у', 'ах', 'иях', 'ях', 'ы', 'ь', 'ию', 'ью', 'ю',
                     'ия', 'ья', 'я']
        self.rvre = ['я', 'а', 'о', 'е', 'ь', 'и']
        self.derivational = ['ост', 'ость']

    def stem(self, word):
        if isinstance(word, str):
            word = word.lower()
        else:
            return word

        # Шаг 1
        for suffix in self.perfectiveground:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                break

        # Шаг 2
        for suffix in self.reflexive:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                break

        # Шаг 3
        for suffix in self.adjective:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                break
        word = self.__replace(word, self.participle, '')

        # Шаг 4
        for suffix in self.verb:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                break
        word = self.__replace(word, self.noun, '')

        # Шаг 5
        for suffix in self.derivational:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                break

        for suffix in self.rvre:
            if word.endswith(suffix):
                if len(word) > 1:
                    word = word[:-len(suffix)]
                break
        return word

    def __replace(self, word, suffixes, replacement):
        for suffix in suffixes:
            if word.endswith(suffix):
                word = word[:-len(suffix)] + replacement
                break
        return word
