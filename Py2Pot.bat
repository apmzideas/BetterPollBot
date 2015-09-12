
REM cd C:\Users\Adrian\Documents\GitHub\BetterPollBot


py -3.4  C:\PYthon34\Tools\i18n\pygettext.py -n --keyword=_ --default-domain=Telegram --output-dir=po Telegram/*.py Telegram/Language/*.py Telegram/Messages/*.py Telegram/Parsers/*.py Telegram/Sql/*.py
pause