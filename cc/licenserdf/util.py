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
    translated_string = ''
    last_pos = 0
    for match in TRANSLATION_BIT_RE.finditer(string):
        translated_string += string[last_pos:match.start()]
        msgid = match.group(1)
        translation = translate(
            msgid, domain=domain, target_language=target_language)
        translated_string += translation
        last_pos = match.end()
    translated_string += string[last_pos:]
    return translated_string
