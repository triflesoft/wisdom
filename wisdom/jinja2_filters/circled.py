DECORATIONS = {
    '1': '\u2776',
    '2': '\u2777',
    '3': '\u2778',
    '4': '\u2779',
    '5': '\u277A',
    '6': '\u277B',
    '7': '\u277C',
    '8': '\u277D',
    '9': '\u277E',
    '10': '\u277F',
}


def discover_circled(text):
    return text


def generate_circled(text):
    return DECORATIONS.get(text, text)
