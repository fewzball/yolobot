# -*- coding: utf-8 -*-
import irc3

import yolofish


@irc3.plugin
class Plugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.fish = yolofish.YoloFish(bot.config['fish_key'])

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_message(self, mask, event, target, data):
        # We only care about messages from channels
        if target.startswith('#'):
            if data.startswith('+OK ') or data.startswith('mcps '):
                _, msg = data.split(' ', 1)
                msg = self.fish.decrypt(msg)

    @classmethod
    def reload(cls, old):
        print('reloading!')
        return cls(old.bot)
