""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.
Version: 4.1
"""

import yaml
from datetime import date, datetime
from dateutil.parser import parse

import disnake
from disnake import ApplicationCommandInteraction, Option, OptionType
from disnake.ext import commands, tasks

from helpers import checks

class General(commands.Cog, name="commands"):
    def __init__(self, bot):
        self.bot = bot
        self.desired_time = str
        self.channel = None
        self.file_string = None

        try:
            for guild in self.bot.guilds:
                self.check_config(guild)
        except Exception as e:
            return print(f"could not perform check_config().\n{e}")

    def check_config(self, guild):

        file_string = "configs/" + str(guild.id)
        
        if self.post_q.is_running():
            self.post_q.cancel()
            print(f"{self.post_q.is_running()} OR {self.post_q.is_being_cancelled()} -> task is being cancelled...")
    
        print(f"loading configuration for {guild.name} (ID: {guild.id})...")

        try:
          with open(f"{file_string}-config.yaml",'r') as f:
                config_yaml = yaml.safe_load(f)
        except Exception as e:
            return print(f"setting up configurations didn't quite work.\n\nthis is what happened: {str(e)}")

        if config_yaml['channel'] == None:
            return print(f"no previous configurations for {guild.name} (ID: {guild.id}) was found: {config_yaml['channel']}")

        else:
            print(f"previous configurations were found for {guild.name} (ID: {guild.id}...): {config_yaml['channel']}")
            self.channel = config_yaml['channel']
            self.file_string = file_string

            try:
                submitted_time = parse(config_yaml['desired_time'],fuzzy=True)
                submitted_time = submitted_time.time()
            except Exception as e: 
                embed = disnake.Embed(
                    title="nimi nasa!?",
                    description=f"couldn't parse the time value you gave... \n\nexception: {str(e)}",
                    color=disnake.Color.yellow(),
                )
                send_chan = self.bot.get_channel(self.channel)
                if send_chan == None: return print(f"{e}")
                else: send_chan.send(embed=embed)

            self.post_q.change_interval(time=submitted_time)
            self.post_q.start()
            print(f"next post will occur at {self.post_q.next_iteration}")
            print(f"this loop runs are time {self.post_q.time}")
            print(f"this is loop number {self.post_q.current_loop}")
            print(f"next post will occur at {self.post_q.next_iteration}")


    @commands.slash_command(
        name="fetch_question",
        description="fetch a question by index",
        options=[
            Option(
                name="index",
                description="position of question in list (0 -> -1)",
                type=OptionType.integer,
                required=True,
            )
        ]
    )
    @checks.not_blacklisted()
    async def fetch_question(self, interactions: ApplicationCommandInteraction, index: int) -> None:
        """
        fetches a specific question by index
        """

        file_string = "configs/" + str(interactions.guild_id)

        # load in questions
        with open(f'{file_string}-new-q.yaml','r') as f:
            q_data = yaml.safe_load(f)

        # build response from index
        try:
            embed = disnake.Embed(
                title="o pana seme",
                description=q_data[index],
            )
        except:
            embed = disnake.Embed(
                title="ala!",
                description="that wasn't a valid index :(",
                color=disnake.Color.yellow(),
            )
            return await interactions.send(embed=embed, ephemeral=True)
                    
        # send successful response
        await interactions.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="remove_question",
        description="remove a question by index (permanent)",
        options=[
            Option(
                name="index",
                description="position of question in list (0 -> -1)",
                type=OptionType.integer,
                required=True,
            )
        ]
    )
    @checks.not_blacklisted()
    async def remove_question(self, interactions: ApplicationCommandInteraction, index: int) -> None:
        """
        will remove a question by index and will not save it to old-q.yaml
        """

        file_string = "configs/" + str(interactions.guild_id)
        
        # load in questions
        with open(f'{file_string}-new-q.yaml','r') as f:
            q_data = yaml.safe_load(f)

        # remove a given question
        try:
            question = q_data.pop(index)
        except:
            embed = disnake.Embed(
                title="ala!",
                description="you need to add more questions to do that!",
                color=disnake.Color.yellow(),
            )
            return await interactions.send(embed=embed, ephemeral=True)

        # write updated list without removed q
        with open(f'{file_string}-new-q.yaml','w') as f:
            yaml.safe_dump(q_data,f)

        # send confirmation back to user
        embed = disnake.Embed(
            title="o weka!",
            description=f"your question was: \n\n```\n{question}\n``` \n\nbut it's gone now!",
            color=disnake.Color.green()
        )

        await interactions.send(embed=embed, ephemeral=True)


    @commands.slash_command(
        name="restore_old_questions",
        description="this command will add all old questions to the end of current questions list",
        options=[ 
            Option(
                name="confirmation",
                description="are you sure? this cannot be undone.",
                type=OptionType.boolean,
                required=True,
            )
        ]
    )    
    @checks.not_blacklisted()
    async def restore_old_questions(self, interactions:ApplicationCommandInteraction, confirmation: bool) -> None:
        if confirmation == False:
            return
        else:
            pass

        file_string = "configs/" + str(interactions.guild_id)

        with open(f'{file_string}-new-q.yaml','r') as f:
            q_data_new = yaml.safe_load(f)
            new_quantity = len(q_data_new)
        with open(f'{file_string}-old-q.yaml','r') as f:
            q_data_old = yaml.safe_load(f)
            old_quantity = len(q_data_old)
        try:
            [ q_data_new.append(i) for i in q_data_old ]
        except Exception as e:
            embed = disnake.Embed(
                title="ala!",
                description=f"something went wrong...\n\n```\n{str(e)}\n```",
                color=disnake.Color.red(),
            )
            return await interactions.send(embed=embed, ephemeral=True)

        with open(f'{file_string}-new-q.yaml','w') as f:
            yaml.safe_dump(q_data_new,f)
        with open(f'{file_string}-old-q.yaml','w') as f:
            yaml.safe_dump(list(),f)

        embed = disnake.Embed(
            title="o weka!",
            description=f"added {old_quantity} questions to the {new_quantity} already in your list. \n\n \
                that's {old_quantity+new_quantity} questions total!",
            color=disnake.Color.green(),
        )

        await interactions.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="add_question",
        description="add a new question to the list",
        options=[
            Option(
                name="question",
                description="enter your question",
                type=OptionType.string,
                required=True
            )
        ]
    )
    @checks.not_blacklisted()
    async def add_question(self, interactions: ApplicationCommandInteraction, question: str) -> None:
        """
        adds a new question to the new-q list
        """

        file_string = "configs/" + str(interactions.guild_id)

        # load in questions
        with open(f'{file_string}-new-q.yaml','r') as f:
            q_data = yaml.safe_load(f)
        if q_data == None: q_data = list()
        
        q_data.append(question)
        quantity = len(q_data)
        
        with open(f'{file_string}-new-q.yaml','w') as f:
            yaml.safe_dump(q_data,f)

        embed = disnake.Embed(
            title="pona!",
            description=f"your question is number **{quantity}** in the queue!",
        )

        await interactions.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="get_num_questions",
        description="get how many questions are waiting",
    )
    @checks.not_blacklisted()
    async def get_num_questions(self, interactions: ApplicationCommandInteraction) -> None:
        """
        gets number of questions in queue
        """

        file_string = "configs/" + str(interactions.guild_id)

        # load in questions
        with open(f'{file_string}-new-q.yaml','r') as f:
            q_data = yaml.safe_load(f)

        quantity = len(q_data)

        # try to build response embed
        try:
            desc_string = f"there are {quantity} questions in queue. \n\nthe next question is:\n{q_data[0]}\n\nthe newest question is:\n{q_data[-1]}"
        except Exception as e:
            print(f"{interactions.guild_id} has {quantity} questions available.\nexception: {str(e)}")
            embed = disnake.Embed(
                title="o pana!",
                description=f"you're all out of questions!\n\nexception: {str(e)}",
                color=disnake.Color.yellow(),
            )
            return await interactions.send(embed=embed, ephemeral=True)
            
        # send response embed
        embed = disnake.Embed(
            title="nanpa seme",
            description=desc_string,
        )

        await interactions.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="post_now",
        description="post a question to a specified channel now",
        options=[
            Option(
                name="channel",
                description="which channel you want the question in",
                type=OptionType.channel,
                required=True,
            ),
            Option(
                name="question",
                description="optionally include index of a specific question",
                type=OptionType.integer,
                required=False,
            )
        ]
    )
    @checks.not_blacklisted()
    async def post_now(self, interactions: ApplicationCommandInteraction, channel, question) -> None:
        """
        post immediately to a specified channel
        """
        embed = disnake.Embed(
            title="o pana!",
            description="you're all out of questions!",
            color=disnake.Color.yellow(),
        )
        file_string = "configs/" + str(interactions.guild_id)

        # get the next question
        with open(f'{file_string}-new-q.yaml','r') as f:
            q_data = yaml.safe_load(f)

        if q_data is None: q_data = list()
        if question is None: question = 0

        try:
            active_q = str(q_data.pop(question))          
        except:
            return await interactions.send(embed=embed, ephemeral=True)

        # create the thread for the question
        new_thread = await channel.create_thread(
            name=date.today().strftime("%A, %B %-d"),
            type=disnake.ChannelType.public_thread
        )

        # transfer the active question to old-q.yaml
        # write new new-q.yaml with active-q removed
        try:
            with open(f'{file_string}-old-q.yaml','r') as f:
                old_q = yaml.safe_load(f)
            with open(f'{file_string}-old-q.yaml','w') as f:
                old_q.append(active_q)
                yaml.safe_dump(old_q, f)
            with open(f'{file_string}-new-q.yaml', 'w') as f:
                yaml.safe_dump(q_data, f)
        except Exception as e:
            print(f"{interactions.guild_id} couldn't move the posted question to old-q.yaml\n\nexception: {str(e)}")

        # post the active question
        await new_thread.send(active_q)

        # send confirmation
        embed.title, embed.description = "pona a!", f"posted successfully in **#{str(channel.name)}**"
        embed.color = disnake.Color.green()
        return await interactions.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="configure",
        description="set daily question rotation",
        options=[ 
            Option(
                name="time",
                description="time each day to post a question",
                type=OptionType.string,
                required=True,
            ),
            Option(
                name="channel",
                description="which channel you want the question in",
                type=OptionType.channel,
                required=True,
            ),
        ]   
    )
    @checks.not_blacklisted()
    async def configure(self, interactions: ApplicationCommandInteraction, time: str, channel) -> None:

        file_string = "configs/" + str(interactions.guild_id)
        self.file_string = file_string
        self.channel = str(channel.id)
        self.desired_time = time

        config_yaml = dict()
        config_yaml['channel'] = self.channel
        config_yaml['desired_time'] = str(self.desired_time)

        # write the configuration file
        try:
          with open(f"{file_string}-config.yaml",'w') as f:
                config_yaml = yaml.safe_dump(config_yaml,f)
        except Exception as e:
            embed = disnake.Embed(
                title="o pakala...",
                description=f"writing your configuration file didn't work out.\n\nthis is what happened: {str(e)}",
                color=disnake.Color.red(),
            )
            return await interactions.send(embed=embed, ephemeral=True)
        
        # initialize with checks
        self.check_config(interactions.guild)

    # this is a daily question posting loop
    @tasks.loop(hours=24)
    async def post_q(self):

        # make channel id into channel object
        try:
            channel = self.bot.get_channel(self.channel)
            print(f"channel is {str(channel)} and {channel.id}")
        except Exception as e:
            return print(f"couldn't resolve given channel_id into channel object in post_q()\nexception: {e}")

        # if we're out of questions, we'll post an embed about it.
        with open(f'{self.file_string}-new-q.yaml','r') as f:
            q_data = yaml.safe_load(f)

        list(q_data)

        try: active_q = str(q_data.pop(0))          
        except:
            embed = disnake.Embed(
                title="mi ken ala alasa e seme!",
                description="no questions left to post! :'<",
                color=disnake.Color.yellow(),
            )
            return await channel.send(embed=embed)

        # if everything is good, we will create a new public thread with a timestamp
        new_thread = await channel.create_thread(
            name=date.today().strftime("%A, %B %-d"),
            type=disnake.ChannelType.public_thread
        )

        # this embed contains the question
        embed = disnake.Embed(
            title=" ♥ ijo seme sin! ♥",
            description=active_q,
        )

        # we will post the question inside the thread we just made
        await new_thread.send(embed=embed)

        # the active question is appended to the old-q list for reuse
        with open(f'{self.file_string}-new-q.yaml','w') as f:
            yaml.safe_dump(q_data, f)
        with open(f'{self.file_string}-old-q.yaml','a') as f:
            f.write(active_q + "\n")

        print(f"next post will occur at {self.post_q.next_iteration}")

def setup(bot):
    bot.add_cog(General(bot))
