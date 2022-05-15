from argparse import Action
from socket import timeout
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ChatAction
from CesarCipher import encdec
from fnmatch import translate
from autocorrect import Speller

spell=Speller(lang="es")
CIFRAR_TEXTO = 0
PEDIR_CLAVE=1
DESCIFRAR_TEXTO=2
LETTERS    = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def start(update, context):
    
    update.message.reply_text('Hola Bienvenido, qué deseas hacer?\n\n/cifrar para cifrar un mensaje\n/descifrar para descifrar un mensaje')


def cifrar_command_handler(update, context):
    update.message.reply_text('Envíame el texto a cifrar')
    return CIFRAR_TEXTO

def descifrar_command_handler(update, context):
    update.message.reply_text('Envíame el texto a descifrar')
    return DESCIFRAR_TEXTO

def decode(message,key):
    translated = ""
    for symbol in message:
        if symbol in LETTERS:
            num = LETTERS.find(symbol)
            num = num + key
            if num >= len(LETTERS):
                num -= len(LETTERS)
            elif num < 0:
                num += len(LETTERS)

            translated += LETTERS[num]
        else:
            translated += symbol
    return translated

def dec(message):
    words=message.split()
    translated=[]
    sw=True
    key=0
    cap=[]
    while sw:
        print("sigo")
        if key>26:
            sw=False
            return "El mensaje ingresado no está en español o no son palabras"
        for word in words:
            palabra=word.lower()
            a=spell.get_candidates(palabra)
            b=[]
            for can in a:
                if can[0]>0:
                    b.append(can[1])
            if palabra in b:
                print(word)
                translated.append(word)
                sw=False
            elif word.isdigit():
                translated.append(word)
                sw=False
            else:
                translated=[]
                sw=True
                key+=1
                words=decode(message,key).split()
                print(words)
                break
    return translated

def encdec(message, key):
    translated = ""   
    for symbol in message:
        if symbol in LETTERS:
            num = LETTERS.find(symbol)            
            num = num + key
            if num >= len(LETTERS):
                num -= len(LETTERS)
            elif num < 0:
                num += len(LETTERS)

            translated += LETTERS[num]
        else:
            translated += symbol
            
            
    return translated

def send_text(message, chat):
    chat.send_action(
        action=ChatAction.TYPING,
        timeout=None
    )
    chat.send_message(text=message)


def cifrar_texto(update, context):
    text = update.message.text
    print(text)
    context.user_data["text"] = text
    update.message.chat.send_message(text="Envíe el numero de clave")
    return PEDIR_CLAVE

def pedir_clave(update, context):
    if(update.message.text.isdigit()):
        key = int(update.message.text)
    else:
        update.message.chat.send_message(text="Debe digitar un numero válido")
        return PEDIR_CLAVE
    print(key)
    text=context.user_data["text"]
    ciphertext=encdec(text, key)
    chat=update.message.chat
    send_text(ciphertext, chat)
    return ConversationHandler.END

def descifrar_texto(update, context):
    text = update.message.text
    print(text)
    deciphertext=dec(text)
    print("descifrado",deciphertext)
    chat=update.message.chat
    send_text(" ".join(deciphertext), chat)
    return ConversationHandler.END

if __name__ == '__main__':

    updater = Updater(token='5328278176:AAGIlohpSu1q8hYrTaUmSCv8djvCNXk66PY', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('cifrar', cifrar_command_handler),
            CommandHandler('descifrar', descifrar_command_handler)
        ],
        states={
            CIFRAR_TEXTO: [MessageHandler(Filters.text, cifrar_texto)],
            PEDIR_CLAVE: [MessageHandler(Filters.text, pedir_clave)],
            DESCIFRAR_TEXTO:[MessageHandler(Filters.text, descifrar_texto)]
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()