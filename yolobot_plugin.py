# -*- coding: utf-8 -*-
import db
import irc3
import sitebot_config
import yolofish

BOLD = '\x02'


class Formatter(object):
    @classmethod
    def bold(cls, text):
        return '{}{}{}'.format(BOLD, text, BOLD)

    @classmethod
    def format_site(cls, site_info):
        """Formats the site info into the format specified in the
        sitebot_config"""
        output = []
        for row in sitebot_config.LAYOUT:
            line_output = []
            for field in row:
                if isinstance(sitebot_config.FIELDS[field]['type'], list):
                    field_value = site_info.get(
                        ' '.join(sitebot_config.FIELDS[field]['column_name']),
                        ' '
                    )
                else:
                    field_value = site_info.get(
                        sitebot_config.FIELDS[field]['column_name'],
                        ' '
                    )

                line_output.append(
                    '{}: {}'.format(
                        cls.bold(field),
                        field_value
                    )
                )
            output.append(' '.join(line_output))
        return output


@irc3.plugin
class Plugin(object):
    COMMANDS = (
        '!addsite',
        '!site',
        '!set',
    )

    def __init__(self, bot):
        self.validate_layout()

        self.bot = bot
        self.fish = yolofish.YoloFish(bot.config['fish_key'])

        self.db = db.YoloDB(bot.config['db_host'], bot.config['db_name'])

    @staticmethod
    def validate_layout():
        valid_field_names = sitebot_config.FIELDS.keys()
        for output_row in sitebot_config.LAYOUT:
            for field in output_row:
                if field not in valid_field_names:
                    raise Exception(
                        'Error: sitebot_config.py: field {} in LAYOUT does not '
                        'exist in FIELDS.'.format(field)
                    )

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_message(self, mask, event, target, data):
        """This event gets triggered whenever the bot receives a message

        :param mask: The users hostmask
        :type mask: str
        :param event: The event type (will always be PRIVMSG)
        :type event: str
        :param target: The username or channel the message came from
        :type target: str
        :param data: The message
        :type data: str

        """
        # We only care about messages from channels
        if target.startswith('#'):
            if data.startswith('+OK ') or data.startswith('mcps '):
                _, msg = data.split(' ', 1)
                msg = self.fish.decrypt(msg)
                parts = msg.split()
                if parts[0] in self.COMMANDS:
                    getattr(self, parts[0].lstrip('!'))(target, parts)

    def usage(self, args, target, num_args, usage_message):
        """Checks to see if the required number of arguments are provided. If
        they are not, then print out the usage for the command, and return
        True. Otherwise return False.

        :param args: The args that were passed to the bot
        :param target: The channel the message came from
        :param num_args: The number of required args for the command
        :param usage_message: The usage message to print out
        :return: bool
        """
        if len(args) < num_args:
            self.send_msg(
                target,
                '{} {}'.format(
                    Formatter.bold('Usage:'),
                    usage_message
                )
            )
            return True
        return False

    def addsite(self, target, args):
        """Attempts to add a site to the database"""
        if self.usage(args, target, 2, '!addsite <site>'):
            return

        try:
            self.db.add_site(args[1].lower())
        except self.db.AlreadyExistsError:
            return self.send_msg(
                target,
                '{} is already added!'.format(Formatter.bold(args[1]))
            )

        self.send_msg(
            target,
            'Site {} has been added!'.format(Formatter.bold(args[1]))
        )

    def send_msg(self, target, msg):
        self.bot.privmsg(
            target,
            self.fish.encrypt(msg)
        )

    def set(self, target, args):
        valid_fields = sitebot_config.VALID_FIELDS
        valid_fields.sort()
        usage_string = '!set <site> <field> <value(s)>'
        if self.usage(args, target, 4, usage_string):
            self.send_msg(
                target,
                'Allowed fields: {}'.format(' '.join(valid_fields))
            )

    def site(self, target, args):
        if self.usage(args, target, 2, '!site <site_name>'):
            return
        site_info = self.db.get_site(args[1])

        for line in Formatter.format_site(site_info):
            self.send_msg(
                target,
                line
            )

    @classmethod
    def reload(cls, old):
        print 'reloading!'
        return cls(old.bot)
