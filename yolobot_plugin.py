# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3

import yolofish


@irc3.plugin
class Plugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.fish = yolofish.YoloFish(bot.config['fish_key'])

    @irc3.event(irc3.rfc.JOIN)
    def say_hi(self, mask, channel):
        """Say hi when someone join a channel"""
        if mask.nick != self.bot.nick:
            self.bot.privmsg(channel, 'Hi %s!' % mask.nick)
        else:
            self.bot.privmsg(channel, 'Hi %s!')

    @command(permission='view')
    def echo(self, mask, target, args):
        """Echo

            %%echo <message>...
        """
        yield ' '.join(args['<message>'])

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_message(self, mask, event, target, data):
        if target.startswith('#'):
            # We only care about messages from channels
            if data.startswith('+OK ') or data.startswith('mcps '):
                _, msg = data.split(' ', 1)
                msg = self.fish.decrypt(msg)

    @classmethod
    def reload(cls, old):
        print('reloading!')
        return cls(old.bot)