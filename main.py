import asyncio
import discord
import json
import urllib.request
import re
import threading
import os
from discord.ext import commands

Bot = commands.Bot(command_prefix = ";")
IRF = None
API = "http://verify.eryn.io/api/user/"


Warns = []
Roles = json.loads(open("Roles.json").read())

########## FUNCTIONS V

def SiteContents(url):
    Request = urllib.request.Request(url, headers={"User-Agent":'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'})
    Response = urllib.request.urlopen(Request)
    return Response.read()


def HasVerified(ID):
    JSON = SiteContents(API + str(ID))
    Data = json.loads(JSON)

    Status = Data['status']
    if Status == "ok":
        ROBLOXUsername = Data['robloxUsername']
        ROBLOXID = Data['robloxId']
        return ROBLOXUsername, ROBLOXID
    else:
        return "no sir"

def GroupRank(RobloxID, Group):
    Content = SiteContents("https://roblox.com/Game/LuaWebService/HandleSocialRequest.ashx?method=GetGroupRank&playerid=" + str(RobloxID) + "&groupid=" + str(Group))
    Rank = int(re.findall("\d+", str(Content))[0])
    return Rank

def GetRole(Guild, Name):
    Role = discord.utils.get(Guild.roles, name=Name)
    return Role
def GetChannel(Guild, Name):
    Channel = discord.utils.get(Guild.channels, name=Name)
    return Channel
def IsModerator(Guild, Member):
    Role = GetRole(Guild, "Server Moderator")
    for HasRoles in Member.roles:
        if Role == HasRoles:
            return True

async def DM(Member, Text, Embed):
    try:
        if Embed:
            await Bot.send_message(Member, embed=Text)
        else:
            await Bot.send_message(Member, Text)
    except:
        pass

    
async def VerifyMember(Guild, ID):
    Member = Guild.get_member(ID)
    if Member:
        if HasVerified(ID) == "no sir":
            await DM(Member, "Hi there! You are not verified, please verify by going to https://verify.eryn.io", False)
        else:
            Name, RobloxID = HasVerified(ID)
            await DM(Member, "You have been verified! Please allow up to 1 minute for your roles to be given.", False)
            await Bot.change_nickname(Member, Name)
            for RoleName, RoleInformation in Roles.items():
                print(RoleName)
                Group = RoleInformation['GroupID']
                RequiredRank = int(RoleInformation['Rank'])
                GiveToAbove = RoleInformation['GiveToAbove']
                Role = GetRole(Guild, RoleName)
                if GiveToAbove:
                    if GroupRank(RobloxID, Group) >= RequiredRank:
                        await Bot.add_roles(Member, Role)
                    else:
                        await Bot.remove_roles(Member, Role)
                else:
                    if GroupRank(RobloxID, Group) == RequiredRank:
                        await Bot.add_roles(Member, Role)
                    else:
                        await Bot.remove_roles(Member, Role)
            
            



def LogMessage(Moderator, Victim, Action, Reason):
    Title = Action + " by " + Moderator
    Description = Action + " for\n```" + Reason + "```"
    Embed = discord.Embed(title=Title, description=Description, type="rich")
    Embed.add_field(name="Moderator Name", value = Moderator, inline=False)
    Embed.add_field(name="Victim Name", value = Victim, inline=False)
    Embed.add_field(name="Action", value = Action, inline=False)
    return Embed


async def Mute(From, Victim, Reason):
    for VictimRoles in Victim.roles:
        await Bot.remove_roles(Victim, VictimRoles)
    MutedRole = GetRole(Victim.server, "Muted")
    await Bot.add_roles(Victim, MutedRole)

    Embeded = LogMessage(From.name, Victim.name, "Mute", Reason)    
    await DM(Victim, Embeded, True)
    await Bot.send_message(GetChannel(Victim.server, "joint_logs"), embed=Embeded)
    



async def Warn(From, Victim, Reason):
    Embeded = LogMessage(From.name, Victim.name, "Warn", Reason)
    await DM(Victim, Embeded, True)
    await Bot.send_message(GetChannel(Victim.server, "joint_logs"), embed=Embeded)

async def Kick(From, Victim, Reason):

    await Bot.kick(Victim)
    Embeded = LogMessage(From.name, Victim.name, "Kick", Reason)
    await DM(Victim, Embeded, True)
    await Bot.send_message(GetChannel(Victim.server, "joint_logs"), embed=Embeded)
    
async def Unmute(Member):
    for MemberRoles in Member.roles:
        await Bot.remove_roles(MemberRoles)
    await VerifyMember(Member.server, Member.id)


######## Commands V

@Bot.command(pass_context=True)
async def verify(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        await Bot.delete_message(Message)
        await VerifyMember(Guild, Message.author.id)
    except:
        pass



@Bot.command(pass_context=True)
async def warn(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        if Member and IsModerator(Guild, Member):
            Victim = Message.mentions[0]
            Reason = Message.content[9+len(Message.raw_mentions[0]): len(Message.content)]
            await Warn(Member, Victim, Reason)
            await Bot.delete_message(Message)
    except:
        pass
        
@Bot.command(pass_context=True)
async def mute(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        if Member and IsModerator(Guild, Member):
            Victim = Message.mentions[0]
            Reason = Message.content[9+len(Message.raw_mentions[0]): len(Message.content)]
            await Mute(Member, Victim, Reason)
            await Bot.delete_message(Message)
    except:
        pass


@Bot.command(pass_context=True)
async def kick(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        if Member and IsModerator(Guild, Member):
            Victim = Message.mentions[0]
            Reason = Message.content[9+len(Message.raw_mentions[0]): len(Message.content)]
            await Kick(Member, Victim, Reason)
            await Bot.delete_message(Message)
    except:
        pass


@Bot.command(pass_context=True)
async def clearwarns(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        if Member and IsModerator(Guild, Member):
            Victim = Message.mentions[0]
            for Occurence in Warns:
                if Occurence == Victim.id:
                    Warns.remove(Victim.id)
            await Bot.send_message(Message.channel, "Warnings cleared for " + Victim.name)
    except:
        pass


@Bot.command(pass_context=True)
async def clear(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        if Member and IsModerator(Guild, Member):
            MessagesToDelete = int(Message.content[7:len(Message.content)])
            await Bot.delete_message(Message)
            await Bot.purge_from(Message.channel, limit=MessagesToDelete)
    except:
        pass



@Bot.command(pass_context=True)
async def talk(Context):
    Message = Context.message
    Author = Message.author
    if Author.id == "212552746879025154":
        Content = Message.content
        Channel = Message.channel
        ToSay = Content[5:len(Content)]
        await Bot.delete_message(Message)
        await Bot.send_message(Channel, ToSay)

@Bot.command(pass_context=True)
async def exec(Context):
    Message = Context.message
    Author = Message.author
    if Author.id == "212552746879025154":
        Guild = Message.server
        Member = Guild.get_member(Author.id)
        Content = Message.content
        Channel = Message.channel
        ToExec = Content[5:len(Content)]
        eval(ToExec)
        
@Bot.command(pass_context=True)
async def checkwarns(Context):
    Message = Context.message
    Guild = Message.server
    Channel = Message.channel
    WarningsGiven = Warns.count(Message.author.id)
    await Bot.send_message(Channel, "<@" + Message.author.id + "> you have " + str(WarningsGiven) + " warnings!")

######### Reaction warn and mute system

@Bot.event
async def on_reaction_add(Reaction, Member):
    Message = Reaction.message
    Guild = Message.server
    Channel = Message.channel
    Victim = Guild.get_member(Message.author.id)
    try:
        if IsModerator(Guild, Member):
            if Reaction.emoji.name == "mute":
                await Mute(Member, Victim, "Player said: " + Message.clean_content)
                await Bot.delete_message(Message)
            elif Reaction.emoji.name == "warn":
                await Warn(Member, Victim, "Player said: " + Message.clean_content)
                await Bot.delete_message(Message)
            elif Reaction.emoji.name == "kick":
                await Kick(Member, Victim, "Player said: " + Message.clean_content)
                await Bot.delete_message(Message)
    except:
        pass
        
token = os.environ.get("token")
print("oof")
Bot.run(token)
