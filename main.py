import asyncio
import disnake
import datetime
from disnake.ext import commands, tasks
#импортируем нужные библиотеки

bot = commands.Bot(
    command_prefix='!', #задаём префикс
    intents=disnake.Intents.all(), #подключаем интенты
    activity=disnake.Game('ХПК 5'), #статус: играет в 'ХПК 5'
    test_guilds=[int] # текст сервер нужен для того, что бы слэш-команды моментально загружались
)
bot.remove_command('help') #удаляем кринжовую дефолт команду help


#В коде я заменял уникальные id и тд. Вместо них я подставлял int!!!


chat_id = [int] #айди чата ивентов



class CloseTicket(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @disnake.ui.button(label='Закрыть тикет', style=disnake.ButtonStyle.red)
    async def close_ticket(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_message('Тикет был закрыт', ephemeral=True)
        await interaction.channel.delete()



@bot.slash_command(name='тикет', description='Создать тикет для ивента')
async def ticket1(interaction):
    overwrites = {
        interaction.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
        interaction.guild.me: disnake.PermissionOverwrite(read_messages=True),               #<-- настройка прав доступа к текстовому каналу
        interaction.user: disnake.PermissionOverwrite(read_messages=True)
    }
    channel = await interaction.guild.create_text_channel(f'{interaction.user.name} - тикет', overwrites=overwrites)   #создаём текст.канал(тикет)
    await interaction.response.send_message(f'тикет создан - {channel.mention}', ephemeral=True)

    embed = disnake.Embed(
        title='Тикет создан', 
        description=f'{interaction.user.mention} создал тикет\nНажми на кнопку ниже, что бы закрыть тикет',
        colour=0x00a3ff
    )

    embed2 = disnake.Embed(
        title='Как создать ивент?',
        description='Пропишите следующее и дождитесь сообщение бота:\n!ивент (дд.мм) (час:минута)(по МСК) (название) (текст) (url-ссылка на фото, загруженное на сайте imgur)\nПример:\n!ивент 23.01 21:00 Скачки приходите на мои скачки коней, тут весело;) https://i.imgur.com/NAtU27J.jpg\n\nСайт imgur прикреплён выше',
        colour=0x00a3ff
    )

    embed2.set_image('https://i.imgur.com/4smOteH.png')
    embed2.set_author(
        name='imgur',
        url='https://imgur.com/'
    )

    await channel.send(embed=embed, view=CloseTicket()) #отправляем сообщение с кнопкой, отвечающей за удаление тикета
    await channel.send(embed=embed2)   #отправляем сообщение с инструкцией
    


@bot.command(name='ивент')
async def event(ctx):
    '''
    команда !ивент определяет ключевое сообщение об ивенте
    '''
    gosha = ctx.guild.get_member(int) #определяем айди админа
    global message_event, zxc, name
    message = ctx.message.content

    if ctx.channel.id not in chat_id:
        message_event = ' '.join(message.split()[1:])
        time = f"Время: {' '.join(list(message_event.split())[:2])}"
        name = f"Название: {' '.join(list(message_event.split())[2:3])}"   #определяем время, название и текст ивента
        text = ' '.join(list(message_event.split())[3:])
        zxc = f'**{time}**\n**{name}**\n{text}'
        await ctx.send(zxc, view=SandEvent())    #отправляем сообщение в красивом формате с кнопкой для админа
        await ctx.send(gosha.mention)   #пингуем админа



class SandEvent(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='принимаю ивент', style=disnake.ButtonStyle.green)
    async def accept(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        global channel_event, x

        if interaction.user.id == int or interaction.user.id == int:   #кнопка будет реагировать на взаимодействия с конкретными юзерами(админами)
            channel_event = interaction.guild.get_channel(int)
            x = await channel_event.send(f'@everyone\n{zxc}', view=SandEventbutton())     #пересылаем сообщение в чат ивенты
            await interaction.channel.delete()      #удаляем тикет, он нам больше не нужен



class SandEventbutton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label='я приду', style=disnake.ButtonStyle.green)
    async def iillcomming(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        global role
        role = interaction.guild.get_role(int)   #определяем роль
        await interaction.user.add_roles(role)   #при нажатии кнопки юзером, еду даётся роль
        await interaction.send('вы подтвердили участие в ивенте!', ephemeral=True)
        day = list((' '.join(message_event.split())).split()[0].split('.'))[0]
        month = list((' '.join(message_event.split())).split()[0].split('.'))[1]      #<-- более точно определяем дату, месяц и время
        hour = list((' '.join(message_event.split())).split()[1].split(':'))[0]
        minute = list((' '.join(message_event.split())).split()[1].split(':'))[1]
        zxc = f'{day}/{month}/{hour}/{minute}/{23}'
        self.future = datetime.datetime.strptime(zxc, '%d/%m/%H/%M/%y')     #определяем время начала ивента
        self.zxcursed.start(interaction.guild.members)      #запускаем task

    @disnake.ext.tasks.loop(seconds=1)
    async def zxcursed(self, members):
        '''
        Каждую секунду обновляем текущее время. 
        Сравниваем текущее время и время начала ивента. 
        Eсли до начала ивента 10минут, то в чат присылаем сообщение с пингом, затем через 2 минуты удаляем это сообщение, по причине не актуальности
        Если время совпадает с временем начала ивента, то оповещаем в чате об этом с пингом. Через 2 минуты удаляем это оповещение и так же первое сообщение об ивенте

        '''
        global dota2
        now = datetime.datetime.now()
        raznica = self.future - now
        nujno1 = datetime.timedelta(minutes= 10)
        nujno2 = datetime.timedelta(minutes=9, seconds=59)
        nujno3 = datetime.timedelta(seconds=2)
        if nujno2 < raznica < nujno1:
            print('До ивента 10мин')
            dota2 = await channel_event.send('<@&1066806596824473702>\nДо ивента осталось ровно 10 минут!Смотри не опоздай!')
            await asyncio.sleep(120)
            await dota2.delete()
        elif raznica < nujno3:
            print('ивент начался')
            qwe = await channel_event.send(f'<@&1066806596824473702>\nИвент {list(name.split())[1]} начался!')
            await asyncio.sleep(120)
            await x.delete()
            await qwe.delete()
            for i in members:
                if role in i.roles:
                    await i.remove_roles(role)

            self.zxcursed.stop()
            #стопаем task

@bot.event
async def on_ready():
    print(f'полетели {bot.user}')
#при готовности бота, в консольку будет это писаться

bot.run('тссс, тут был токен') #запуск :)