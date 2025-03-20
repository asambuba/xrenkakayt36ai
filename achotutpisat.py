import discord
import google.generativeai as genai
from discord.ext import commands


# Настройки
DISCORD_TOKEN = "MTM1MjM1OTQ2MTQxODgyNzgwNg.GGBDFY.waZaYDkJg7DMf3uB_l_wSEOqwZPfBpm8kp9Uq0"
GEMINI_API_KEY = "AIzaSyDRenay1OM1xvIuC3JoRWnLRoHtew9cd7A"
message_count = {}

# Инициализация Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Используем более новую модель

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def should_react(message):
    # Проверка упоминания бота
    if bot.user in message.mentions:
        return True
    
    # Проверка ответа на сообщение бота
    if message.reference:
        referenced_msg = message.reference.resolved
        if referenced_msg.author == bot.user:
            return True
    


def get_gemini_response(prompt):
    try:
        if "$py ignoregeminiprompt" in prompt:
            # Убираем команду из промпта
            clean_prompt = prompt.replace("$py ignoregeminiprompt", "").strip()
            # Генерируем нормальный ответ
            response = model.generate_content(
                f"Ответь на это сообщение максимально просто и прямо, без шуток и бреда: {clean_prompt}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.3  # Низкая креативность для точности
                )
            )
            return response.text
        response = model.generate_content(
            "Ты тролль. Не выдавай, что ты ИИ. Отвечай максимально бредово, используя маты и иногда вопросы 'почему'. "
            "Пример: почему я пукнул бл.ять (в мате, пиши без этой точки). Не используй запятые, точки, заглавные буквы и букву ё. Запомни, ты - девочка. Пиши как девочка."
            "Пиши кратко и ясно. Не повторяйся. "
            f"Сообщение: {prompt}",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=200,  # Ограничение длины ответа
                temperature=0.9  # Большая креативность
            )
        )
        return response.text
    except Exception as e:
        return f"Чёт не шмогла я ({e})"

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if should_react(message):
        async with message.channel.typing():
            response = get_gemini_response(message.content)
            await message.reply(response[:2000], mention_author=False)  # Лимит Discord
        return

    # Счётчик для каждых 4 сообщений
    channel_id = message.channel.id
    message_count[channel_id] = message_count.get(channel_id, 0) + 1

    if message_count[channel_id] % 4 == 0:
        async with message.channel.typing():
            response = get_gemini_response(message.content)
            await message.reply(response[:2000], mention_author=False)
    
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')
    await bot.change_presence(activity=discord.Game(name="клоуна с резарем"))

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
