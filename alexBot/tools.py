import math
import posixpath
import time
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator, Iterable, TypeVar
from urllib.parse import urlparse

if TYPE_CHECKING:
    from bot import Bot

import re
from logging import getLogger

import aiohttp
import discord
import xmltodict
from discord.ext import commands

log = getLogger(__name__)

_T = TypeVar("_T")


class Cog(commands.Cog):
    """The Cog base class that all cogs should inherit from."""

    def __init__(self, bot: "Bot"):
        self.bot: "Bot" = bot


async def get_text(session: aiohttp.ClientSession, url: str) -> str:
    log.debug(f"fetched url: {url}")
    async with session.get(url) as content:
        return await content.text()


async def get_json(session: aiohttp.ClientSession, url: str, **kwargs) -> dict:
    log.debug(f"fetched json: {url}")
    async with session.get(url, **kwargs) as content:
        return await content.json()


async def get_xml(session: aiohttp.ClientSession, url: str) -> dict:
    log.debug(f"fetched xml: {url}")
    async with session.get(url) as content:
        return xmltodict.parse(await content.text())


def is_in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id

    return commands.check(predicate)


def is_in_channel(channel_id):
    async def predicate(ctx):
        return ctx.channel and ctx.channel.id == channel_id

    return commands.check(predicate)


def timing(log=None):
    """
    a decorator to log how long a function takes to execute.
    """
    if log is None:
        prt = print
    else:
        prt = log.debug

    def inner_function(function: Callable):
        """
        a decorator to log how long a function takes to execute.
        """

        @wraps(function)
        def wrapper(*args, **kwargs):
            prt(f"starting {function.__name__}..")
            ts = time.time()
            result = function(*args, **kwargs)
            te = time.time()
            prt(f"{function.__name__} completed, took {te - ts} seconds")
            return result

        return wrapper

    return inner_function


def grouper(iterable: Iterable[_T], n: int) -> Generator[Iterable[_T], None, None]:
    """
    given a iterable, yield that iterable back in chunks of size n. last item will be any size.
    """
    for i in range(math.ceil(len(iterable) / n)):
        yield iterable[i * n : i * n + n]


def transform_neosdb(url: str) -> str:
    url = urlparse(url)
    return f"https://cloudxstorage.blob.core.windows.net/assets{posixpath.splitext(url.path)[0]}"

