
REM cd C:\Users\Adrian\Documents\GitHub\BetterPollBot


py -3.4  C:\PYthon34\Tools\i18n\pygettext.py -n --keyword=_ --default-domain=Telegram --output-dir=translation_template src/*.py src/language/*.py src/messages/*.py src/parsers/*.py src/sql/*.py
pause