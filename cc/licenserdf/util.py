from zope.i18n import translate

import re


TRANSLATION_BIT_RE = re.compile('\$\{([^\}]+)\}')


def inverse_translate(string, target_language, domain='cc_org'):
    """
    Translate something like "Foo ${bar} baz", where we actually
    preserve "Foo " and " baz" and translate "${bar} (using "bar" as
    the msgid)

       >>> from cc.licenserdf import cc_org_i18n
       >>> translated_string = inverse_translate(
       ...    'foo ${country.pt} baz ${license.GPL_name_full}',
       ...    target_language='en_US')
       >>> translated_string == 'foo Portugal baz GNU General Public License'
    """
    string = unicode_cleaner(string)
    translated_string = u''
    last_pos = 0
    for match in TRANSLATION_BIT_RE.finditer(string):
        translated_string += string[last_pos:match.start()]
        msgid = match.group(1)
        translation = translate(
            msgid, domain=domain, target_language=target_language)
        translated_string += unicode_cleaner(translation)
        last_pos = match.end()
    translated_string += string[last_pos:]
    return translated_string


def unicode_cleaner(string):
    if isinstance(string, unicode):
        return string

    try:
        return string.decode('utf-8')
    except UnicodeError:
        try:
            return string.decode('latin-1')
        except UnicodeError:
            return string.decode('utf-8', 'ignore')


def rdf_style_lang(cc_style_lang):
    lang_parts = cc_style_lang.lower().split('_', 1)
    if len(lang_parts) == 2:
        return '%s-%s' % (lang_parts[0], lang_parts[1])
    else:
        return lang_parts[0].lower()
