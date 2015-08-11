import ObjectHolder
import json

class Message(TelegramObject):
    
    # A Class to create and configure the message
    
    def __init__(self, ToChatId, Text, DisableWebPagePreview=False,
                 ReplyToMessageId=None ):
        
        self.ToChatId = ToChatId
        self.Text = Text
        self.DisableWebPagePreview = DisableWebPagePreview
        self.ReplyToMessageId = ReplyToMessageId
        self.ReplyMarkup = {}
        
# Parameters                    Type         Required     Description
# chat_id                       Integer      Yes          Unique identifier for the message recipient — User or GroupChat id
# text                          String       Yes          Text of the message to be sent
# disable_web_page_preview      Boolean      Optional     Disables link previews for links in this message
# reply_to_message_id           Integer      Optional     If the message is a reply, ID of the original message
# reply_markup
# ReplyKeyboardMarkup or 
# ReplyKeyboardHide or 
# ForceReply                                 Optional     Additional interface options. A JSON-serialized object for a custom reply keyboard, instructions to hide keyboard or to force a reply from the user.
    
    def ReplyKeyboardMarkup(self, Keybord, ResizeKeyboard = False, OneTimeKeyboard = False, Selective = False):
        #A method to create a custom keybord
        #This object represents a custom keyboard with reply options
        
        self.ReplyMarkup = {}
        
        self.ReplyMarkup["keyboard"] = Keybord
        if ResizeKeyboard:
            self.ReplyMarkup["resize_keyboard"] = ResizeKeyboard
        if OneTimeKeyboard:
            self.ReplyMarkup["one_time_keyboard"] = OneTimeKeyboard
        if Selective:
            self.ReplyMarkup = Selective
    
    def ReplyKeyboardHide(self, Selecttiv=False):
        #Upon receiving a message with this object, Telegram clients will hide 
        #the current custom keyboard and display the default letter-keyboard. 
        #By default, custom keyboards are displayed until a new keyboard is 
        #sent by a bot. An exception is made for one-time keyboards that are 
        #hidden immediately after the user presses a button 
        #(see ReplyKeyboardMarkup).
        
        self.ReplyMarkup = {}
        
        self.ReplyMarkup["HideKeybord"] = True
        
        if Selecttiv:
            self.ReplyMarkup["selective"]
            
    def ForceReply(self, Selecttiv=False):
        #Upon receiving a message with this object, Telegram clients will 
        #display a reply interface to the user (act as if the user has 
        #selected the bot‘s message and tapped ’Reply'). This can be 
        #extremely useful if you want to create user-friendly step-by-step 
        #interfaces without having to sacrifice privacy mode.
        
        self.ReplyMarkup = {}
        
        self.ReplyMarkup["force_reply"] = True
        
        if Selecttiv:
           self.ReplyMarkup["selective"] = True
        
    def GetMessage(self):
        #This methode will assemble the message
        DataToBeSend = { 
                        "chat_id": self.ToChatId,
                        "text": bytes(self.Text.encode("uft-8")),
                        }
        
        if self.DisableWebPagePreview:
            DataToBeSend["disable_web_page_preview"] = True
        if self.ReplyToMessageId.isdigit():
            DataToBeSend["reply_to_message_id"] = self.ReplyToMessageId
        if self.ReplyMarkup != {}:
            DataToBeSend["reply_markup"] = json.JSONEncoder().encode(ReplyMarkup)
            
        return DataToBeSend
    
