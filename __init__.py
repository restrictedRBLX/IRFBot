import asyncio
import discord
import json
import urllib.request
import re
from discord.ext import commands

Bot = commands.Bot(command_prefix = ";")
IRF = None
API = "http://verify.eryn.io/api/user/"



Warnings = []
Mutes = []
Roles = json.loads(open("Roles.json").read())

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

def IsModerator(Guild, Member):
    Role = GetRole(Guild, "Server Moderator")
    for HasRoles in Member.roles:
        if Role == HasRoles:
            return true

async def DM(Member, Text):
    try:
        await Bot.send_message(Member, Text)
    except:
        pass

    
async def VerifyMember(Guild, ID):
    Member = Guild.get_member(ID)
    if Member:
        if HasVerified(ID) == "no sir":
            await DM(Member, "Hi there! You are not verified, please verify by going to https://verify.eryn.io")
        else:
            Name, RobloxID = HasVerified(ID)
            await DM(Member, "You have been verified! Please allow up to 1 minute for your roles to be given.")
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
            
            await Bot.change_nickname(Member, Name)


def Mute(From, Victim):
    pass # Not yet implemented
def Warn(From, Victim):
    pass # Not yet implemented
def UpdateWarns():
    pass # Not yet implemented

@Bot.command(pass_context=True)
async def verify(Context):
    Message = Context.message
    Guild = Message.server
    try:
        Member = Guild.get_member(Message.author.id)
        await VerifyMember(Guild, Member.id)
    except:
        pass

@Bot.command(pass_context=True)
async def warn(Context):
    Message = Context.message
    Guild = Message.server
    Member = Guild.get_member(Message.author.id)
    Victim = Message.mentions[0]
    Warn(Member, Victim)

@Bot.command(pass_context=True)
async def mute(Context):
    Message = Context.message
    Guild = Message.server
    Member = Guild.get_member(Message.author.id)
    Victim = Message.mentions[0]
    Mute(Member, Victim)


    

Bot.run('MzUyMDYwNDY0NjMwNDY0NTEz.DPxhFA.6JXjuznETijyQKbWORyAhTPgBoU')
