from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'telegram_bot_builder')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Pydantic models
class BotConfig(BaseModel):
    name: str
    description: str
    features: List[str]
    commands: List[str]
    has_inline_buttons: bool = False
    has_webhook: bool = False
    has_database: bool = False
    token_var_name: str = "BOT_TOKEN"

class BotTemplate(BaseModel):
    id: str
    name: str
    description: str
    code: str
    features: List[str]
    created_at: datetime

# Bot code templates
BOT_TEMPLATES = {
    "echo": {
        "name": "Bot Echo Simple",
        "description": "Bot qui répète tous les messages reçus",
        "code": '''import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fonction pour la commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie un message de bienvenue quand la commande /start est utilisée."""
    await update.message.reply_text(
        'Salut ! Je suis un bot echo. Envoyez-moi un message et je le répéterai !'
    )

# Fonction pour la commande /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie un message d'aide quand la commande /help est utilisée."""
    await update.message.reply_text(
        'Commandes disponibles:\\n'
        '/start - Commencer\\n'
        '/help - Afficher cette aide\\n'
        '\\nEnvoyez-moi un message et je le répéterai !'
    )

# Fonction pour répéter les messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Répète le message de l'utilisateur."""
    await update.message.reply_text(f"Vous avez dit: {update.message.text}")

# Fonction principale
def main() -> None:
    """Démarre le bot."""
    # Remplacez 'YOUR_BOT_TOKEN' par votre token de bot
    TOKEN = os.getenv('{token_var}', 'YOUR_BOT_TOKEN')
    
    # Créer l'application
    application = Application.builder().token(TOKEN).build()
    
    # Ajouter les handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Démarrer le bot
    print("Bot démarré ! Appuyez sur Ctrl+C pour arrêter.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
''',
        "features": ["echo", "commands"]
    },
    "commands": {
        "name": "Bot avec Commandes",
        "description": "Bot avec plusieurs commandes personnalisées",
        "code": '''import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fonction pour la commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande de démarrage."""
    user = update.effective_user
    await update.message.reply_text(
        f'Salut {user.first_name} ! 👋\\n'
        f'Je suis votre bot personnel. Tapez /help pour voir toutes les commandes.'
    )

# Fonction pour la commande /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'aide."""
    help_text = '''
🤖 **Commandes disponibles:**

/start - Commencer
/help - Afficher cette aide
/info - Informations sur le bot
/time - Heure actuelle
/echo [message] - Répéter un message
/ping - Tester la connexion

Envoyez-moi un message et je vous répondrai !
    '''
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Fonction pour la commande /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche les informations du bot."""
    await update.message.reply_text(
        '📊 **Informations du bot:**\\n'
        '• Version: 1.0.0\\n'
        '• Créé avec: python-telegram-bot\\n'
        '• Fonctionnalités: Commandes personnalisées\\n'
        '• Statut: En ligne ✅',
        parse_mode='Markdown'
    )

# Fonction pour la commande /time
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche l'heure actuelle."""
    from datetime import datetime
    now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    await update.message.reply_text(f"🕐 Heure actuelle: {now}")

# Fonction pour la commande /echo
async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Répète le message fourni."""
    if context.args:
        message = ' '.join(context.args)
        await update.message.reply_text(f"🔊 Echo: {message}")
    else:
        await update.message.reply_text("Usage: /echo [votre message]")

# Fonction pour la commande /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Teste la connexion."""
    await update.message.reply_text("🏓 Pong! Bot en ligne.")

# Fonction pour gérer les messages text
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les messages texte."""
    message = update.message.text.lower()
    
    responses = {
        'bonjour': 'Bonjour ! Comment allez-vous ?',
        'salut': 'Salut ! 👋',
        'merci': 'De rien ! 😊',
        'comment ca va': 'Ça va bien, merci ! Et vous ?',
        'au revoir': 'Au revoir ! À bientôt ! 👋'
    }
    
    for key, response in responses.items():
        if key in message:
            await update.message.reply_text(response)
            return
    
    await update.message.reply_text(
        "Je ne comprends pas ce message. Tapez /help pour voir les commandes disponibles."
    )

# Fonction principale
def main() -> None:
    """Démarre le bot."""
    TOKEN = os.getenv('{token_var}', 'YOUR_BOT_TOKEN')
    
    # Créer l'application
    application = Application.builder().token(TOKEN).build()
    
    # Ajouter les handlers de commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("ping", ping))
    
    # Handler pour les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Démarrer le bot
    print("Bot avec commandes démarré ! Appuyez sur Ctrl+C pour arrêter.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
''',
        "features": ["commands", "responses"]
    },
    "buttons": {
        "name": "Bot avec Boutons Inline",
        "description": "Bot avec boutons interactifs",
        "code": '''import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fonction pour la commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande de démarrage avec boutons."""
    keyboard = [
        [InlineKeyboardButton("📊 Informations", callback_data='info')],
        [InlineKeyboardButton("🎮 Jeux", callback_data='games'),
         InlineKeyboardButton("⚙️ Paramètres", callback_data='settings')],
        [InlineKeyboardButton("❓ Aide", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '🤖 **Bienvenue !**\\n'
        'Choisissez une option ci-dessous:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Fonction pour la commande /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal."""
    keyboard = [
        [InlineKeyboardButton("🏠 Accueil", callback_data='home')],
        [InlineKeyboardButton("📈 Statistiques", callback_data='stats'),
         InlineKeyboardButton("🔧 Outils", callback_data='tools')],
        [InlineKeyboardButton("📞 Contact", callback_data='contact'),
         InlineKeyboardButton("🆘 Support", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '📋 **Menu Principal**\\n'
        'Sélectionnez une option:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Fonction pour gérer les boutons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les clics sur les boutons."""
    query = update.callback_query
    await query.answer()
    
    # Réponses selon le bouton cliqué
    responses = {
        'info': {
            'text': '📊 **Informations du Bot**\\n\\n'
                   '• Version: 1.0.0\\n'
                   '• Créé avec: python-telegram-bot\\n'
                   '• Fonctionnalités: Boutons interactifs\\n'
                   '• Statut: En ligne ✅',
            'buttons': [
                [InlineKeyboardButton("🔙 Retour", callback_data='back')]
            ]
        },
        'games': {
            'text': '🎮 **Section Jeux**\\n\\n'
                   'Choisissez un jeu:',
            'buttons': [
                [InlineKeyboardButton("🎲 Dé", callback_data='dice'),
                 InlineKeyboardButton("🎰 Casino", callback_data='casino')],
                [InlineKeyboardButton("🔙 Retour", callback_data='back')]
            ]
        },
        'settings': {
            'text': '⚙️ **Paramètres**\\n\\n'
                   'Configurez votre bot:',
            'buttons': [
                [InlineKeyboardButton("🔔 Notifications", callback_data='notifications')],
                [InlineKeyboardButton("🌐 Langue", callback_data='language')],
                [InlineKeyboardButton("🔙 Retour", callback_data='back')]
            ]
        },
        'help': {
            'text': '❓ **Aide**\\n\\n'
                   '**Commandes disponibles:**\\n'
                   '/start - Commencer\\n'
                   '/menu - Afficher le menu\\n'
                   '/help - Afficher cette aide\\n\\n'
                   '**Comment utiliser:**\\n'
                   '1. Cliquez sur les boutons\\n'
                   '2. Naviguez dans les menus\\n'
                   '3. Utilisez les commandes',
            'buttons': [
                [InlineKeyboardButton("🔙 Retour", callback_data='back')]
            ]
        },
        'dice': {
            'text': '🎲 **Jeu de Dé**\\n\\n'
                   'Cliquez pour lancer le dé!',
            'buttons': [
                [InlineKeyboardButton("🎲 Lancer", callback_data='roll_dice')],
                [InlineKeyboardButton("🔙 Retour", callback_data='games')]
            ]
        },
        'roll_dice': {
            'text': '🎲 **Résultat du dé:** {}\\n\\n'
                   'Voulez-vous rejouer?'.format(__import__('random').randint(1, 6)),
            'buttons': [
                [InlineKeyboardButton("🎲 Relancer", callback_data='roll_dice')],
                [InlineKeyboardButton("🔙 Retour", callback_data='games')]
            ]
        },
        'back': {
            'text': '🤖 **Bienvenue !**\\n'
                   'Choisissez une option ci-dessous:',
            'buttons': [
                [InlineKeyboardButton("📊 Informations", callback_data='info')],
                [InlineKeyboardButton("🎮 Jeux", callback_data='games'),
                 InlineKeyboardButton("⚙️ Paramètres", callback_data='settings')],
                [InlineKeyboardButton("❓ Aide", callback_data='help')]
            ]
        }
    }
    
    # Réponse par défaut
    if query.data not in responses:
        await query.edit_message_text(
            f"🔧 Fonction '{query.data}' en cours de développement...\\n\\n"
            f"Cette fonctionnalité sera bientôt disponible!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Retour", callback_data='back')]
            ]),
            parse_mode='Markdown'
        )
        return
    
    response = responses[query.data]
    reply_markup = InlineKeyboardMarkup(response['buttons'])
    
    await query.edit_message_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Fonction principale
def main() -> None:
    """Démarre le bot."""
    TOKEN = os.getenv('{token_var}', 'YOUR_BOT_TOKEN')
    
    # Créer l'application
    application = Application.builder().token(TOKEN).build()
    
    # Ajouter les handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Démarrer le bot
    print("Bot avec boutons démarré ! Appuyez sur Ctrl+C pour arrêter.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
''',
        "features": ["buttons", "interactive"]
    }
}

def generate_bot_code(config: BotConfig) -> str:
    """Génère le code du bot basé sur la configuration."""
    base_template = "echo"
    
    # Choisir le template de base selon les fonctionnalités
    if config.has_inline_buttons:
        base_template = "buttons"
    elif len(config.commands) > 2:
        base_template = "commands"
    
    template = BOT_TEMPLATES[base_template]
    code = template["code"]
    
    # Remplacer les variables
    code = code.replace("{token_var}", config.token_var_name)
    
    # Ajouter les commandes personnalisées si nécessaire
    if config.commands and base_template == "echo":
        # Ajouter les commandes personnalisées au template echo
        custom_commands = []
        for cmd in config.commands:
            if cmd not in ["start", "help"]:
                custom_commands.append(f'''
# Fonction pour la commande /{cmd}
async def {cmd}_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande personnalisée /{cmd}."""
    await update.message.reply_text(f"Commande /{cmd} exécutée!")
''')
        
        if custom_commands:
            # Insérer les commandes personnalisées
            code = code.replace("# Fonction principale", "\n".join(custom_commands) + "\n\n# Fonction principale")
            
            # Ajouter les handlers
            handlers = []
            for cmd in config.commands:
                if cmd not in ["start", "help"]:
                    handlers.append(f'    application.add_handler(CommandHandler("{cmd}", {cmd}_command))')
            
            if handlers:
                code = code.replace(
                    '    application.add_handler(CommandHandler("help", help_command))',
                    '    application.add_handler(CommandHandler("help", help_command))\n' + '\n'.join(handlers)
                )
    
    return code

# API Routes
@app.get("/api/templates")
async def get_templates():
    """Retourne tous les templates disponibles."""
    templates = []
    for key, template in BOT_TEMPLATES.items():
        templates.append({
            "id": key,
            "name": template["name"],
            "description": template["description"],
            "features": template["features"]
        })
    return templates

@app.post("/api/generate")
async def generate_bot(config: BotConfig):
    """Génère le code du bot basé sur la configuration."""
    try:
        code = generate_bot_code(config)
        
        # Sauvegarder la configuration en base
        bot_data = {
            "id": str(uuid.uuid4()),
            "name": config.name,
            "description": config.description,
            "features": config.features,
            "commands": config.commands,
            "has_inline_buttons": config.has_inline_buttons,
            "has_webhook": config.has_webhook,
            "has_database": config.has_database,
            "token_var_name": config.token_var_name,
            "code": code,
            "created_at": datetime.now()
        }
        
        await db.bots.insert_one(bot_data)
        
        return {
            "success": True,
            "code": code,
            "bot_id": bot_data["id"],
            "requirements": [
                "python-telegram-bot==20.7",
                "python-dotenv==1.0.0"
            ],
            "setup_instructions": [
                "1. Créez un bot via @BotFather sur Telegram",
                "2. Copiez le token du bot",
                "3. Créez un fichier .env avec BOT_TOKEN=votre_token",
                "4. Installez les dépendances: pip install python-telegram-bot python-dotenv",
                "5. Lancez le bot: python bot.py"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bots")
async def get_bots():
    """Retourne tous les bots générés."""
    bots = []
    async for bot in db.bots.find().sort("created_at", -1):
        bots.append({
            "id": bot["id"],
            "name": bot["name"],
            "description": bot["description"],
            "features": bot["features"],
            "created_at": bot["created_at"]
        })
    return bots

@app.get("/api/bots/{bot_id}")
async def get_bot(bot_id: str):
    """Retourne un bot spécifique."""
    bot = await db.bots.find_one({"id": bot_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot non trouvé")
    return bot

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str):
    """Supprime un bot."""
    result = await db.bots.delete_one({"id": bot_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bot non trouvé")
    return {"success": True}

@app.get("/api/")
async def root():
    return {"message": "API du générateur de bots Telegram"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)