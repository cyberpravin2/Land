import asyncio
import os
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from pyrogram.enums import ParseMode
import importlib.util
import sys

# Bot configuration
API_ID = 
API_HASH = "b8aff444a27656a255bb2032a28f99c0"
BOT_TOKEN = "8414591679:AAGNMTeapuAuXU5ZvjUWJujlqrIttNynIwA"

# Initialize bot
app = Client(
    "sk1mmer_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Plugin storage
LOADED_PLUGINS = {}

# Video rotation for menu
current_menu_video_index = 0
MENU_VIDEOS = [f"VID/menu{i}.mp4" for i in range(1, 11)]

def get_next_menu_video():
    """Get next video in rotation"""
    global current_menu_video_index
    video = MENU_VIDEOS[current_menu_video_index]
    current_menu_video_index = (current_menu_video_index + 1) % len(MENU_VIDEOS)
    return video

def load_plugins():
    """Load all gateway plugins from the gateways directory"""
    plugins_dir = "gateways"
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        return
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py') and not filename.startswith('__') and filename.upper() != 'TEMPLATE.PY':
            plugin_name = filename[:-3]
            plugin_path = os.path.join(plugins_dir, filename)
            
            try:
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)
                
                if hasattr(module, 'PLUGIN_INFO'):
                    LOADED_PLUGINS[plugin_name] = module
                    print(f"✅ Loaded plugin: {plugin_name}")
                    
                    if hasattr(module, 'setup'):
                        module.setup(app)
                        print(f"✅ Registered commands for: {plugin_name}")
                else:
                    print(f"⚠️ Warning: {plugin_name} has no PLUGIN_INFO, skipping")
            except Exception as e:
                print(f"❌ Error loading plugin {plugin_name}: {e}")

@app.on_message(filters.command(["start", "Start"], prefixes=[".", "/", "!", "$"]))
async def start_command(client, message):
    """Send a message when the command /start is issued."""
    from utils.database import db
    from utils.admin import check_banned, check_maintenance
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    db.add_user(user_id, username)
    
    if await check_banned(client, message):
        return
    if await check_maintenance(client, message):
        return
    
    keyboard = [
        [
            InlineKeyboardButton("Gates ♻️", callback_data="gates"),
            InlineKeyboardButton("Tools 🛠", callback_data="tools"),
        ],
        [
            InlineKeyboardButton("Channel 🥷", url="https://t.me/+VEFfBVi7mnpkZGJl"),
            InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"[朱](t.me/sunilxd) 𝙒𝙚𝙡𝙘𝙤𝙢𝙚\n\n"
        f"[㊄](t.me/sunilxd)We present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"[╰┈➤](t.me/sunilxd) 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 1.0"
    )
    
    try:
        video_file = get_next_menu_video()
        if os.path.exists(video_file):
            await message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await message.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error in start command: {e}")
        await message.reply_text(
            caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

@app.on_callback_query()
async def button_callback(client, callback_query):
    """Handle button callbacks"""
    query = callback_query
    await query.answer()
    
    original_message = (
        f"<a href='https://t.me/sunilxd'>朱</a> 𝙒𝙚𝙡𝙘𝙤𝙢𝙚\n\n"
        f"<a href='https://t.me/sunilxd'>㊄</a> We present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"<a href='https://t.me/sunilxd'>╰┈➤</a> 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 1.0"
    )
    
    if query.data == "gates":
        # Build dynamic gate list from loaded plugins
        auth_gates = []
        charge_gates = []
        for name, module in LOADED_PLUGINS.items():
            info = module.PLUGIN_INFO
            cmd = info['commands'][0]
            prefix = info['prefixes'][0]  # use first prefix, typically '.'
            gate_type = info.get('type', 'check')
            if gate_type in ['auth', 'check']:
                auth_gates.append((cmd, prefix, info.get('description', 'No description')))
            elif gate_type == 'charge':
                charge_gates.append((cmd, prefix, info.get('description', 'No description')))
        
        # Build message
        message_lines = [
            "#SunilXD                                                                                𝙒𝙚𝙡𝙘𝙤𝙢𝙚 -» >_\n\n"
            f"║<a href='https://t.me/sunilxd'>㊕</a>║ 𝙏𝙤𝙩𝙖𝙡 -» {len(LOADED_PLUGINS)}\n"
            f"║<a href='https://t.me/sunilxd'>㊡</a>║ 𝙊𝙣 -» {len([p for p in LOADED_PLUGINS.values() if p.PLUGIN_INFO.get('status') == 'active'])} ✅\n"
            f"║<a href='https://t.me/sunilxd'>㊤</a>║ 𝙊𝙛𝙛 -» {len([p for p in LOADED_PLUGINS.values() if p.PLUGIN_INFO.get('status') != 'active'])} ❌\n\n"
            "〈<a href='https://t.me/sunilxd'>ゼ</a>〉𝙎𝙚𝙡𝙚𝙘𝙩 𝙩𝙝𝙚 𝙩𝙮𝙥𝙚 𝙤𝙛 𝙜𝙖𝙩𝙚 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙛𝙤𝙧 𝙮𝙤𝙪𝙧 𝙪𝙨𝙚!"
        ]
        keyboard = [
            [InlineKeyboardButton("Auth", callback_data="auth"),
             InlineKeyboardButton("Charge", callback_data="charge")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        await query.edit_message_caption(
            caption="\n".join(message_lines),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "auth":
        # Build auth gate list
        auth_gates = []
        for name, module in LOADED_PLUGINS.items():
            info = module.PLUGIN_INFO
            if info.get('type') in ['auth', 'check']:
                cmd = info['commands'][0]
                prefix = info['prefixes'][0]
                desc = info.get('description', 'No description')
                status = "On ✅" if info.get('status') == 'active' else "Off ❌"
                auth_gates.append(f"〈<a href='https://t.me/sunilxd'>朱</a>〉 {desc} -» {prefix}{cmd} -» {status}")
        
        message = "〈<a href='https://t.me/sunilxd'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘼𝙪𝙩𝙝\n\n" + "\n".join(auth_gates) + "\n\n"
        keyboard = [[InlineKeyboardButton("Back", callback_data="gates")]]
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "charge":
        # Build charge gate list
        charge_gates = []
        for name, module in LOADED_PLUGINS.items():
            info = module.PLUGIN_INFO
            if info.get('type') == 'charge':
                cmd = info['commands'][0]
                prefix = info['prefixes'][0]
                desc = info.get('description', 'No description')
                status = "On ✅" if info.get('status') == 'active' else "Off ❌"
                charge_gates.append(f"〈<a href='https://t.me/sunilxd'>朱</a>〉 {desc} -» {prefix}{cmd} -» {status}")
        
        message = "〈<a href='https://t.me/sunilxd'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘾𝙝𝙖𝙧𝙜𝙚𝙙\n\n" + "\n".join(charge_gates) + "\n\n"
        keyboard = [[InlineKeyboardButton("Back", callback_data="gates")]]
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "tools":
        message = (
            "〈<a href='https://t.me/sunilxd'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝙏𝙤𝙤𝙡𝙨 🛠\n\n"
            "<a href='https://t.me/sunilxd'>朱</a> 𝘽𝙞𝙣 -» info bin\n"
            "<a href='https://t.me/sunilxd'>零</a> 𝘾𝙢𝙙 -» .bin -» Free\n"
            "<a href='https://t.me/sunilxd'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="back")]]
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == "exit":
        await query.message.delete()
    
    elif query.data == "back":
        keyboard = [
            [
                InlineKeyboardButton("Gates ♻️", callback_data="gates"),
                InlineKeyboardButton("Tools 🛠", callback_data="tools"),
            ],
            [
                InlineKeyboardButton("Channel 🥷", url="https://t.me/+VEFfBVi7mnpkZGJl"),
                InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            video_file = "VID/menu1.mp4"
            if os.path.exists(video_file):
                media = InputMediaVideo(media=video_file, caption=original_message, parse_mode=ParseMode.HTML)
                await query.edit_message_media(media=media, reply_markup=reply_markup)
            else:
                await query.edit_message_caption(
                    caption=original_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"Error in back button: {e}")
            await query.edit_message_caption(
                caption=original_message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

def main():
    """Start the bot"""
    folders = ['VID', 'Banned', 'Maintenance', 'HIT']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Created folder: {folder}")
    
    print("🤖 Loading plugins...")
    load_plugins()
    print(f"✅ Loaded {len(LOADED_PLUGINS)} plugins")
    
    from utils.admin import setup_admin_commands
    setup_admin_commands(app)
    
    from utils.user_tools import setup_user_tools
    setup_user_tools(app)
    
    from utils.card_generator import setup_card_generator
    setup_card_generator(app)
    
    from utils.file_handlers import setup_file_handlers
    setup_file_handlers(app)
    
    print("🚀 Starting bot...")
    app.run()

if __name__ == "__main__":
    main()