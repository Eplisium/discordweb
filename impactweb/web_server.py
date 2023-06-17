#--------------------------------------------------------------------------------
#-----------------"Impact Web" Developed by Eplisium-------------------------------
#-------------------------------------------------------------------------------- 
import discord
import logging
import asyncio
import json
import os
import aiohttp_jinja2
import jinja2
import base64
from discord.ext import commands
from aiohttp import web, ClientSession
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from jinja2 import Environment, FileSystemLoader
from cryptography import fernet
from wutil.webconfig import bot_token3, client_id, client_secret

# Set intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = True
intents.members = True


# Initialize bot
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None, fetch_offline_members=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    activity = discord.Activity(type=discord.ActivityType.watching, name='Website')
    await bot.change_presence(activity=activity)

# Bot event to restore roles on member join
@bot.event
async def on_member_join(member):
    await restore_roles(member.guild, member)

# Create web application
app = web.Application()

# Set up session middleware
key_str = 'uN4IZsoQXPpoTO9BSSYuRP6Jsv-ml1OFioHPuWCg0_M='
key = base64.urlsafe_b64decode(key_str)
setup(app, EncryptedCookieStorage(key))

# Set up aiohttp_jinja2 with correct templates folder path
aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

# Web server index route
async def index(request):
    template = "index.html"
    server_id = 752320387995533403
    server = bot.get_guild(server_id)
    
    if server:
        user_count = sum(1 for member in server.members if not member.bot)
        bot_count = sum(1 for member in server.members if member.bot)
    else:
        user_count = 0
        bot_count = 0

    return aiohttp_jinja2.render_template(template, request, context={
        'server': server,
        'user_count': user_count,
        'bot_count': bot_count,
    })

# Save and restore roles functions
def save_roles(guild_id, user_id, roles):
    folder_name = 'function'
    os.makedirs(folder_name, exist_ok=True)
    guild_roles_file = os.path.join(folder_name, f'roles_{guild_id}.json')
    
    if os.path.exists(guild_roles_file):
        with open(guild_roles_file, 'r') as file:
            roles_data = json.load(file)
    else:
        roles_data = {}

    roles_data[str(user_id)] = [role.id for role in roles]

    with open(guild_roles_file, 'w') as file:
        json.dump(roles_data, file)

async def restore_roles(guild, member):
    bot_member = guild.get_member(bot.user.id)
    bot_highest_role_position = max([r.position for r in bot_member.roles])

    folder_name = 'function'
    os.makedirs(folder_name, exist_ok=True)
    guild_roles_file = os.path.join(folder_name, f'roles_{guild.id}.json')

    if os.path.exists(guild_roles_file):
        with open(guild_roles_file, 'r') as file:
            roles_data = json.load(file)

        user_roles = roles_data.get(str(member.id), [])
        for role_id in user_roles:
            role = guild.get_role(role_id)
            
            if role and role != guild.default_role and role.position < bot_highest_role_position:
                await member.add_roles(role)

# Avatar getting
def generate_avatar_url_with_hash(user_id, avatar_hash, discriminator):
    if avatar_hash:
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
    else:
        return f"https://cdn.discordapp.com/embed/avatars/{int(discriminator) % 5}.png"
    return avatar_url

async def get_users(request):
    session = await get_session(request)
    user_id = session.get('user_id')
    avatar_hash = session.get('avatar_hash')
    server_id = 752320387995533403
    server = bot.get_guild(server_id)

    if user_id:
        user = bot.get_user(int(user_id))
        if user:
            username = f'{user.name}#{user.discriminator}'
            avatar_url = generate_avatar_url_with_hash(user.id, avatar_hash, user.discriminator)
        else:
            username = None
            avatar_url = None
    else:
        username = None
        avatar_url = None

    members = []
    for guild in bot.guilds:
        for member in guild.members:
            if member not in members:
                members.append(member)

    
    user_count = sum(1 for member in members if not member.bot)
    bot_count = sum(1 for member in members if member.bot)

    search = request.rel_url.query.get('search', '')
    sort = request.rel_url.query.get('sort', '')

    if search:
        search = search.lower()
        members = [member for member in members if search in member.name.lower() or search == str(member.id) or search in str(member.status)]

    members_data = []
    for member in members:
        member_avatar_hash = member.avatar.key if member.avatar else None
        member_avatar_url = generate_avatar_url_with_hash(member.id, member_avatar_hash, member.discriminator)
        highest_role = member.roles[-1] if member.roles else None

        user_data = {
            'user': member,
            'mod_discriminator': int(member.discriminator) % 5,
            'status': str(member.status),
            'status_int': status_to_int(str(member.status)),
            'avatar': member_avatar_hash,
            'member_avatar_url': member_avatar_url,
            'highest_role': highest_role,
        }

        members_data.append(user_data)

    if sort == "recent":
        members_data.sort(key=lambda x: x['user'].joined_at, reverse=True)
    elif sort == "oldest":
        members_data.sort(key=lambda x: x['user'].joined_at)
    elif sort == "username":
        members_data.sort(key=lambda x: x['user'].name)
    elif sort == "id":
        members_data.sort(key=lambda x: x['user'].id)
    elif sort == "status":
        members_data.sort(key=lambda x: (x['user'].status, x['user'].name))

    return aiohttp_jinja2.render_template('users.html', request, {
        'username': username,
        'users': members_data,
        'sort': sort,
        'search': search,
        'avatar_url': avatar_url,
        'member_avatar_url': member_avatar_url,
        'server': server,
        'user_count': user_count,
        'bot_count': bot_count,
    })

async def get_user_status(request):
    user_id = request.match_info.get('user_id', None)
    if not user_id or not user_id.isdigit():
        raise web.HTTPBadRequest(text="Invalid user ID")
    
    user_id = int(user_id)
    member = None

    for guild in bot.guilds:
        member = guild.get_member(int(user_id))
        if member:
            break

    if member:
        return web.json_response({'status': str(member.status)})
    else:
        return web.json_response({'error': 'User not found'})

# Ordering Online Status sorting 
def status_to_int(status):
    if status == 'online':
        return 1
    elif status == 'idle':
        return 2
    elif status == 'dnd':
        return 3
    else:
        return 4

env = Environment(loader=FileSystemLoader('templates'))
env.filters['status_to_int'] = status_to_int
app['aiohttp_jinja2_environment'].filters['get_users'] = get_users

# Ban and Kick functions
async def ban_user(request):
    session = await get_session(request)
    user_id = session.get('user_id')
    if user_id:
        logged_in_user = bot.get_user(int(user_id))

        user_to_ban_id = int(request.match_info['user'])
        user_to_ban = None

        for guild in bot.guilds:
            logged_in_member = guild.get_member(logged_in_user.id)
            if logged_in_member and logged_in_member.guild_permissions.ban_members:
                user_to_ban = guild.get_member(user_to_ban_id)
                if user_to_ban:
                    save_roles(user_to_ban.guild.id, user_to_ban.id, user_to_ban.roles)
                    await guild.ban(user_to_ban)
                    break

        if user_to_ban:
            response_text = f"Banned user {user_to_ban}. Redirecting in 15 seconds...<br><a href='/api/users'>Back</a>"
            response = web.Response(text=response_text, content_type='text/html')
            response.set_cookie('redirect_delay', 15, max_age=15)
            return response
        else:
            return web.Response(text=f"User not found in any guilds, or you don't have permission to ban.")
    else:
        return web.Response(text="You must be logged in to ban users.", status=403)

async def kick_user(request):
    session = await get_session(request)
    user_id = session.get('user_id')
    if user_id:
        logged_in_user = bot.get_user(int(user_id))

        user_to_kick_id = int(request.match_info['user'])
        user_to_kick = None

        for guild in bot.guilds:
            logged_in_member = guild.get_member(logged_in_user.id)
            if logged_in_member and logged_in_member.guild_permissions.kick_members:
                user_to_kick = guild.get_member(user_to_kick_id)
                if user_to_kick:
                    save_roles(user_to_kick.guild.id, user_to_kick.id, user_to_kick.roles)
                    await guild.kick(user_to_kick)
                    break

        if user_to_kick:
            response_text = f"Kicked user {user_to_kick}. Redirecting in 15 seconds...<br><a href='/api/users'>Back</a>"
            response = web.Response(text=response_text, content_type='text/html')
            response.set_cookie('redirect_delay', 15, max_age=15)
            return response
        else:
            return web.Response(text=f"User not found in any guilds, or you don't have permission to kick.")
    else:
        return web.Response(text="You must be logged in to kick users.", status=403)

async def login(request):
    host = request.headers.get('host')
    ip = request.remote  

    
    if ip == "127.0.0.1" or ip.startswith("192.168"):
        redirect_uri = redirect_uris[1]  
    else:
        redirect_uri = redirect_uris[0]  

    base_url = f'http://{host}'
    url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    return web.HTTPFound(location=url)

async def logout(request):
    session = await get_session(request)
    session.invalidate()
    return web.HTTPFound(location='/api/users')

async def callback(request):
    try:
        code = request.query.get('code')
        async with ClientSession() as session:
            s
            ip = request.remote
            if ip == "127.0.0.1" or ip.startswith("192.168"):
                redirect_uri = redirect_uris[1]  
            else:
                redirect_uri = redirect_uris[0]  

            payload = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'scope': 'identify'
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            async with session.post('https://discord.com/api/oauth2/token', data=payload, headers=headers) as resp:
                access_token_data = await resp.json()

            logger.debug(f"access_token_data: {access_token_data}")  

            access_token = access_token_data['access_token']
            headers = {'Authorization': f"Bearer {access_token}"}

            async with session.get('https://discord.com/api/users/@me', headers=headers) as resp:
                user_data = await resp.json()

        user_id = user_data['id']
        avatar_hash = user_data['avatar']

        session = await get_session(request)
        session['user_id'] = user_id
        session['avatar_hash'] = avatar_hash

        return web.HTTPFound(location='/api/users')
    except Exception as e:
        logger.exception("Error in callback function")
        return web.Response(text=f"Internal Server Error: {str(e)}", status=500)

# Add routes to app router
app.router.add_get('/api/user_status/{user_id}', get_user_status)
app.router.add_get('/api/users', get_users)
app.router.add_post('/ban/{user}', ban_user)
app.router.add_post('/kick/{user}', kick_user)
app.router.add_get('/login', login)
app.router.add_get('/logout', logout)
app.router.add_get('/callback', callback)
app.router.add_get('/', index)

# Main function to start bot and web server tasks
async def main():
    bot_task = asyncio.create_task(bot.start(bot_token3))
    web_server_task = asyncio.create_task(web._run_app(app, host='0.0.0.0', port=5000))

    await asyncio.gather(bot_task, web_server_task)

# Run main function
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Gracefully shutting down...")
        for task in asyncio.all_tasks(loop):
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))
        except asyncio.CancelledError:
            pass
        finally:
            loop.run_until_complete(bot.close())
            loop.close()
