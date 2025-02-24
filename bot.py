import logging
import random
import json
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Se não for necessário não mude !
# Faz um pix aí webzin782@gmail.com please 😀

# Configurações 
TELEGRAM_TOKEN = 'token_bot'
OWNER_ID = teuid
PIX_KEY = 'webzin782@gmail.com'
DATA_FILE = 'user_data.json'

# Preços logins
LOGIN_PRICES = {
    'growth': 5.00,
    'max_titanium': 7.00,
    'pichau': 6.00,
    'boticario': 4.50,
    'renner': 5.50,
    'centauro': 5.00,
    'magalu': 6.50,
    'vivo': 5.00,
    'smiles': 4.00,
    'drogasil': 5.00,
    'vivara': 7.50,
}


user_balances = {}
gift_cards = {}


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def load_user_data():
    global user_balances
    try:
        with open(DATA_FILE, 'r') as file:
            user_balances = json.load(file)
    except FileNotFoundError:
        user_balances = {}
    except json.JSONDecodeError:
        user_balances = {}


def save_user_data():
    with open(DATA_FILE, 'w') as file:
        json.dump(user_balances, file)


def generate_gift_card(value):
    characters = string.ascii_letters + string.digits
    gift_card = ''.join(random.choice(characters) for _ in range(10))
    gift_cards[gift_card] = value
    return gift_card


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)  
    username = user.username

    if user_id not in user_balances:
        user_balances[user_id] = 1.00
        save_user_data()

    saldo = user_balances.get(user_id, 0.00)

    keyboard = [
        [InlineKeyboardButton("🎟️ | Logins", callback_data='logins')],
        [InlineKeyboardButton("💰 | Adicionar saldo", callback_data='add_saldo')],
        [InlineKeyboardButton("👤 | Suporte", url='https://t.me/Webzin116')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Olá {username} 👋 Seja Bem-vindo(a) a nossa Store.\n\n"
        f"❗Caso aqui não tiver o login que procura contate o suporte\n\n"
        f"INFOS\n\n"
        f"🆔 ID: {user_id}\n"
        f"💸 Seu Saldo: R$ {saldo:.2f}",
        reply_markup=reply_markup
    )

async def show_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id) 
    username = user.username

    saldo = user_balances.get(user_id, 0.00)

    keyboard = [
        [InlineKeyboardButton("🎟️ | Logins", callback_data='logins')],
        [InlineKeyboardButton("💰 | Adicionar saldo", callback_data='add_saldo')],
        [InlineKeyboardButton("👤 | Suporte", url='https://t.me/Webzin116')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"Olá {username} 👋 Seja Bem-vindo(a) a nossa Store.\n\n"
        f"❗Caso aqui não tiver o login que procura contate o suporte\n\n"
        f"INFOS\n\n"
        f"🆔 ID: {user_id}\n"
        f"💸 Seu Saldo: R$ {saldo:.2f}",
        reply_markup=reply_markup
    )

async def logins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔵🔴 | Growth - R$ 5.00", callback_data='growth')],
        [InlineKeyboardButton("💪 | Max Titanium - R$ 7.00", callback_data='max_titanium')],
        [InlineKeyboardButton("🎮 | Pichau - R$ 6.00", callback_data='pichau')],
        [InlineKeyboardButton("🧸 | Boticário - R$ 4.50", callback_data='boticario')],
        [InlineKeyboardButton("👔 | Renner - R$ 5.50", callback_data='renner')],
        [InlineKeyboardButton("🏀 | Centauro - R$ 5.00", callback_data='centauro')],
        [InlineKeyboardButton("🔵 | Magalu - R$ 6.50", callback_data='magalu')],
        [InlineKeyboardButton("🟣 | Vivo - R$ 5.00", callback_data='vivo')],
        [InlineKeyboardButton("🟢 | Smiles - R$ 4.00", callback_data='smiles')],
        [InlineKeyboardButton("💊 | Drogasil - R$ 5.00", callback_data='drogasil')],
        [InlineKeyboardButton("💎 | Vivara - R$ 7.50", callback_data='vivara')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Nossos Logins estão abaixo:",
        reply_markup=reply_markup
    )

async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    login_type = query.data
    price = LOGIN_PRICES.get(login_type)

    keyboard = [
        [InlineKeyboardButton(f"✅ | Confirmar - R$ {price:.2f}", callback_data=f'confirmar_{login_type}')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='logins')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Você tem certeza que deseja adquirir o login {login_type} por R$ {price:.2f}?",
        reply_markup=reply_markup
    )

async def complete_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    login_type = query.data.split('_')[1]
    user_id = str(query.from_user.id)  
    price = LOGIN_PRICES.get(login_type)

    if user_balances.get(user_id, 0) < price:
        await query.edit_message_text("❌ Sem saldo suficiente para realizar a compra")
        return

    try:
        with open(f"{login_type}.txt", "r") as file:
            lines = file.readlines()
        if not lines:
            await query.edit_message_text("Desculpe, todos os logins desse tipo já foram vendidos.")
            return
        chosen_login = random.choice(lines).strip()
        email, password = chosen_login.split(':')

       
        with open(f"{login_type}.txt", "w") as file:
            file.writelines(line for line in lines if line.strip() != chosen_login)

        user_balances[user_id] -= price
        save_user_data()

        await query.edit_message_text(
            f"✅ Compra Efetuada com Sucesso \n\n"
            f"Login: {login_type}\n"
            f"Email/CPF: {email}\n"
            f"Senha: {password}\n"
            f"Trocas são realizadas apenas no suporte: @meuuser"
        )

        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"✅ Venda Realizada\n\n"
            f"Valor: R$ {price:.2f}\n"
            f"Item: {login_type}\n"
            f"Usuário: @{query.from_user.username}\n"
            f"ID User: {user_id}"
        )
    except FileNotFoundError:
        await query.edit_message_text("☹️ Desculpe, estamos sem este login no momento")

async def add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("👤 | Suporte", url='https://t.me/Webzin116')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Para adicionar saldo copie a chave pix abaixo realize a transferência do valor e envie ao suporte.(Nao temos pix automático!)\n\n"
        f"Chave Pix:\n{PIX_KEY}",
        reply_markup=reply_markup
    )

async def add_saldo_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)  
    if user_id != str(OWNER_ID):
        await update.message.reply_text("❗ Somente o administrador pode usar este comando.")
        return

    try:
        command, target_id, value = update.message.text.split()
        target_id = str(target_id) 
        value = float(value.replace(',', '.'))
        if target_id in user_balances:
            user_balances[target_id] += value
            await update.message.reply_text(f"✅ Saldo de R$ {value:.2f} adicionado ao usuário {target_id}.")
        else:
            user_balances[target_id] = value
            await update.message.reply_text(f"✅ Saldo de R$ {value:.2f} adicionado ao usuário {target_id}.")
        save_user_data()
    except (ValueError, IndexError):
        await update.message.reply_text("Use /add <ID do usuário> <valor>")

async def generate_gift_card_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)  
    if user_id != str(OWNER_ID):
        await update.message.reply_text("❗ Somente o administrador pode usar este comando.")
        return

    try:
        command, value = update.message.text.split()
        value = float(value.replace(',', '.'))
        gift_card = generate_gift_card(value)

        keyboard = [
            [InlineKeyboardButton("🎁 Gift Card Gerado", callback_data=f'resgatar_{gift_card}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Gift card gerado com sucesso no valor de R$ {value:.2f}\n"
            f"Gift Card: {gift_card}\n\n"
            "Para resgatar, use o comando /resgatar"
        )
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🎁 Gift Card Gerado\n\n"
            f"Valor: R$ {value:.2f}\n"
            f"Gift Card: {gift_card}\n"
            f"Resgate em: @meubot"
        )
    except (ValueError, IndexError):
        await update.message.reply_text("Use /gen <valor>")

async def redeem_gift_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)  

    try:
        command, gift_card = update.message.text.split()
        if gift_card in gift_cards:
            value = gift_cards.pop(gift_card)
            user_balances[user_id] += value
            save_user_data()
            await update.message.reply_text(
                f"🎁 Parabéns, o Gift Card foi resgatado e já está debitado na sua conta!"
            )
        else:
            await update.message.reply_text(
                "☹️ Desculpe, o gift card já foi resgatado ou não existe."
            )
    except (ValueError, IndexError):
        await update.message.reply_text("Comando inválido. Use /resgatar {gift card}")

def main() -> None:
    load_user_data()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_saldo_admin))
    application.add_handler(CommandHandler("gen", generate_gift_card_command))
    application.add_handler(CommandHandler("resgatar", redeem_gift_card))
    application.add_handler(CallbackQueryHandler(show_start_menu, pattern='start'))
    application.add_handler(CallbackQueryHandler(logins, pattern='logins'))
    application.add_handler(CallbackQueryHandler(confirm_purchase, pattern='^growth$|^max_titanium$|^pichau$|^boticario$|^renner$|^centauro$|^magalu$|^vivo$|^smiles$|^drogasil$|^vivara$'))
    application.add_handler(CallbackQueryHandler(complete_purchase, pattern='^confirmar_'))
    application.add_handler(CallbackQueryHandler(add_saldo, pattern='add_saldo'))

    
    application.run_polling()

if __name__ == '__main__':
    main()