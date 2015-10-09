#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

# python standard library
import urllib.request
import urllib.parse
import ssl
import json
import platform
import zlib
import gobjects  # my own classes
import custom_logging
import messages.message
import language  # imports the _() function! (the translation feature)


class TelegramApi(object):
    """
    This class is responsible for contacting the telegram bot servers.
    
    From the documentation:
    
        The Bot API is an HTTP-based interface created for developers 
        keen on building bots for Telegram.
        To learn how to create and set up a bot
    
        Authorizing your bot
    
        Each bot is given a unique authentication token when it is 
        created. The token looks something like 
        ``123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11``, but we'll use simply 
        ``<token>`` in this document instead. You can learn about obtaining
        tokens and generating new ones in this document.
        
        Making requests
        
        All queries to the Telegram Bot API must be served over HTTPS 
        and need to be presented in this form: 
        ``https://api.telegram.org/bot<token>/METHOD_NAME``. 
        
        Like this for example:
        ``https://api.telegram.org/bot<token>/getMe``
        
        We support GET and POST HTTP methods. We support four ways of 
        passing parameters in Bot API requests:
        
            * URL query string
            * application/x-www-form-urlencoded
            * application/json (except for uploading files)
            * multipart/form-data (use to upload files)
        
        The response contains a JSON object, which always has a Boolean 
        field ‘ok’ and may have an optional String field ‘description’ 
        with a human-readable description of the result. If ‘ok’ equals 
        true, the request was successful and the result of the query 
        can be found in the ‘result’ field. In case of an unsuccessful 
        request, ‘ok’ equals false and the error is explained in the 
        ‘description’. An Integer ‘error_code’ field is also returned, 
        but its contents are subject to change in the future.
        
            * All methods in the Bot API are case-insensitive.
            * All queries must be made using UTF-8.
    
        the documentation is online under:
            https://core.telegram.org/bots/api
    """
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self,
                 ApiToken,
                 RequestTimer,
                 **OptionalObjects
                 ):

        """
        The init method...
        
        Here we set the variables like the header send to the API:
        Example:
            .. code-block:: python
            
                Header
                {
                'Content-Type': 
                'application/x-www-form-urlencoded;charset=utf-8', 
                'User-agent': 
                "BetterPollBot/0.1 (Windows; 8; 6.2.9200)"\\
                " Python-urllib/('v3.4.3:9b73f1c3e601', "\\
                "'Feb 24 2015 22:43:06') "\\
                "from https://github.com/apmzideas/BetterPollBot"
                }
        
        Variables:
            ApiToken                      ``string``
                contains the token to contact the background information
                of the bot\n
                Each bot is given a unique authentication token when it 
                is created.
            
            RequestTimer                  ``integer``
                set's the sleeping time between requests to the bot API

            Queue                         ``object``
                The queue to the main process.
                
            OptionalObjects               ``dictionary``
                contains the optional objects
                like:
                    LanguageObject        ``object``
                        contains the translation object
                        
                    LoggingObject         ``object``
                        contains the logging object needed to log
                        
                    ExitOnError           ``boolean``
                        Determines if the system should shut down
                        if an exception or error occurs.
                        The default value is False.
                        
        """

        self.ApiToken = ApiToken
        self.BotApiUrl = TelegramApi.BASE_URL + self.ApiToken

        # Predefining attribute so that it later can be used for evil.
        self.LanguageObject = None
        self.LoggingObject = None
        self.ExitOnError = False

        # This timer is needed to see if there is a problem with the telegram
        # server. If so the interval should be bigger (1 min instead given
        # time 1 sec)
        self.RequestTimer = RequestTimer
        self.GivenRequestTimer = RequestTimer

        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = (
                language.CreateTranslationObject()
            )

        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = custom_logging.Logger()

        if "ExitOnError" in OptionalObjects:
            self.ExitOnError = OptionalObjects["ExitOnError"]

        # Here we are initialising the function for the translations.
        self._ = self.LanguageObject.gettext

        self.SSLEncryption = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

#         this looks like this:
#         {
#         'Content-Type':
#             'application/x-www-form-urlencoded;charset=utf-8',
#         'User-agent': "BetterPollBot/0.1 (Windows; 8; 6.2.9200) \
#       Python-urllib/('v3.4.3:9b73f1c3e601', 'Feb 24 2015 22:43:06') \
#       from https://github.com/apmzideas/BetterPollBot"
#         }

        self.Headers = {
            'User-agent': (
                gobjects.__AppName__ + '/' +
                str(gobjects.__version__) + ' (' +
                '; '.join(platform.system_alias(
                    platform.system(),
                    platform.release(),
                    platform.version()
                )
                ) +
                ') Python-urllib/' +
                str(platform.python_build()) +
                ' from ' + gobjects.__hosted__
            ),
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8",
            "Accept-Encoding": "gzip"
        }

        # Test if the content can be compressed or nor
        self.Compressed = True
        self.LoggingObject.info(self._("Starting self check"))
        self.BotName = self.GetMe()

    def GetBotName(self):
        """
        This method returns the given bot name from the API.
        
        Variables:
            \-
        """
        return self.BotName

    def SendRequest(self, Request):
        """
        This method will send the request to the telegram server.
        
        It will return the in the end the response from the servers.
        
        Variables:
            Request                       ``object``
                this variable is generated before the request is being
                send to the telegram bot API

        """

        # Reset the request timer if needed.
        if self.RequestTimer != self.GivenRequestTimer:
            self.RequestTimer = self.GivenRequestTimer
        try:
            with urllib.request.urlopen(
                    Request,
                    context=self.SSLEncryption
            ) as Request:
                if self.Compressed is True:
                    if Request.info().get("Accept-Encoding") == "gzip":
                        TheResponse=zlib.decompress(Request.read(),
                                                    16+zlib.MAX_WBITS)
                    else:
                        self.Compressed = False
                        del self.Headers["Accept-Encoding"]

                        TheResponse = Request.read()
                else:
                    TheResponse = Request.read()
            return json.loads(TheResponse.decode("utf-8"))

        except urllib.error.HTTPError as Error:
            if Error.code == 400:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )
                                    ) + " " +
                    self._("The server cannot or will not process the request "
                           "due to something that is perceived to be a client "
                           "error (e.g., malformed request syntax, invalid "
                           "request message framing, or deceptive request "
                           "routing)."
                           ),
                )
            elif Error.code == 401:
                self.LoggingObject.critical(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The ApiToken you are using has not been found in "
                           "the system. Try later or check the ApiToken for "
                           "spelling errors."),
                )
            elif Error.code == 403:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The address is forbidden to access, please try "
                           "later."),
                )
            elif Error.code == 404:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The requested resource was not found. This status "
                           "code can also be used to reject a request without "
                           "closer reason. Links, which refer to those error "
                           "pages, also referred to as dead links."),
                )
            elif Error.code == 502:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The server could not fulfill its function as a "
                           "gateway or proxy, because it has itself obtained "
                           "an invalid response. Please try later."),
                )
                self.RequestTimer = 60000.0
            elif Error.code == 504:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The server could not fulfill its function as a "
                           "gateway or proxy, because it has not received a "
                           "reply from it's servers or services within a "
                           "specified period of time.")
                )

            # For the recursive loop, so that the system can handel itself
            # better
            if self.ExitOnError:
                self.LoggingObject.info(self._("Exiting the system!"))
                raise SystemExit

    def GetMe(self):
        """
        A method to confirm the ApiToken exists.
        
        It returns the response from the request, this includes the
        bot name.
        
        Variables:
           \ -
        """
        request = urllib.request.Request(
            self.BotApiUrl + "/getMe",
            headers=self.Headers
        )

        return self.SendRequest(request)

    def GetUpdates(self, CommentNumber=None):
        """
        A method to get the Updates from the Telegram API.
        
        It does as well to confirm the old comments so that only 
        new responses have to be processed.
        
        Notes:\n
        1. This method will not work if an outgoing web hook is set up.
        2. In order to avoid getting duplicate updates, recalculate offset
           after each server response.
        
        Variables:
            CommentNumber                 ``None or integer``
                this variable set's the completed request id
                
        """

        DataToBeSend = {
                        # "limit": 1,
                        "timeout": 0
                        }

        if CommentNumber:
            DataToBeSend["offset"] = CommentNumber
        # data have to be bytes
        MessageData = urllib.parse.urlencode(DataToBeSend).encode('utf-8')

        Request = urllib.request.Request(self.BotApiUrl + "/getUpdates",
                                              data=MessageData,
                                              headers=self.Headers)

        # send Request and get JSONData    
        JSONData = self.SendRequest(Request,)

        if JSONData is not None:
            if JSONData["ok"]:
                return JSONData

        return None

    def SendMessage(self, MessageObject):
        """
        A method to send messages to the TelegramApi
        
        Variables:
            MessageObject                 ``object``
                this variable is the object with the content of the
                message to be send, as well as other options.
        """

        # data have to be bytes
        MessageData = urllib.parse.urlencode(
            MessageObject.GetMessage()).encode('utf-8')

        Request = urllib.request.Request(self.BotApiUrl + "/sendMessage",
                                         data=MessageData,
                                         headers=self.Headers
                                         )

        return self.SendRequest(Request,)

    def ForwardMessage(self, ChatId, FromChatId, MessageId):
        """
        A method to forward a received message
        
        This function will maybe be build in the future for now
        it's not doing anything.
        """
        MessageData = {}
        pass

if __name__ == "__main__":
    print('online')
    import pprint

    OrgTok = "80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY"
    FalTok = "80578257:AAEt5aH64bD6P3hqumKYFJAyHTGWEgcyEY"
    a = TelegramApi(OrgTok,
                    500)

    Update = a.GetUpdates(469262639 + 1)
    print(Update)
    try:
        print(Update["result"][len(Update["result"]) - 1]["update_id"])

        MessageObject = messages.message.MessageToBeSend(
            Update["result"][len(Update["result"]) - 1]["message"]
            ["chat"]["id"], "1"
        )
        MessageObject.ReplyKeyboardMarkup(
                                          Keybord=[["Top Left",
                                                    "Top Right"],
                                                   ["Bottom Left",
                                                    "Bottom Right" ]
                                                   ],
                                          ResizeKeyboard=True,
                                          OneTimeKeyboard=True,
                                          Selective=False
                                          )
        # MessageObject.ForceReply()
        MessageObject.ReplyKeyboardHide(Selective=True)

        print(a.SendMessage(MessageObject))
    except:
        pass
#     if a:
#         pprint.PrettyPrinter(indent=4).pprint((a.GetMe()))
#         pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
#     else:
#         print("None")
    print('offline')
