# -*- coding: utf-8 -*-
import string

import irc3


import db
import sitebot_config
import yolo_utils
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
                if sitebot_config.FIELDS[field]['type'] is list:
                    field_value = site_info.get(
                        sitebot_config.FIELDS[field]['column_name'],
                        []
                    )
                    if len(field_value) > 0:
                        field_value.sort()
                        field_value = ' '.join(field_value)
                    else:
                        field_value = ''
                else:
                    field_value = site_info.get(
                        sitebot_config.FIELDS[field]['column_name'],
                        ''
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
        '!add',
        '!addsite',
        '!delsite',
        '!help',
        '!rm',
        '!search',
        '!set',
        '!site',
        '!sites',
    )

    # max length of a message we will send at once before breaking into chunks
    MAX_MSG_LENGTH = 490

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

    @staticmethod
    def validate_always_uppercase():
        for field in sitebot_config.ALWAYS_UPPERCASE:
            if field not in sitebot_config.COLUMN_MAPPING:
                raise Exception('Invalid field: {} found in ALWAYS_UPPERCASE')
            if sitebot_config.COLUMN_MAPPING[field] != str:
                raise Exception(
                    "Hey retard, don't put non str fields in ALWAYS_UPPERCASE"
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
                data = data.strip()
                _, msg = data.split(' ', 1)
                msg = self.fish.decrypt(msg)
                msg = ''.join(_ for _ in msg if _ in string.printable)
                parts = msg.split()

                if parts[0] == '!reload':
                    self.bot.reload()
                    return self.send_msg(
                        target,
                        'Reloaded!'
                    )

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

    def add(self, target, args):
        if self.usage(args, target, 4, '!add <site> <field> <value(s)>'):
            return

        site_name, field, values = args[1], args[2], args[3:]

        values = yolo_utils.uppercase_if_needed(field, values)

        if not sitebot_config.COLUMN_MAPPING.get(field) == list:
            return self.send_msg(
                target,
                'Field {} only allows 1 value! Perhaps you want to !set '
                'instead?'.format(args[2])
            )

        result = self.db.add_value(site_name, field, values)
        self.send_msg(
            target,
            '{}: set {} to: {}'.format(
                Formatter.bold(site_name),
                Formatter.bold(field),
                ' '.join(result)
            )
        )

    def addsite(self, target, args):
        """Attempts to add a site to the database"""
        if self.usage(args, target, 2, '!addsite <site>'):
            return

        try:
            self.db.add_site(args[1].upper())
        except self.db.AlreadyExistsError:
            return self.send_msg(
                target,
                '{} is already added!'.format(Formatter.bold(args[1]))
            )

        self.send_msg(
            target,
            'Site {} has been added!'.format(Formatter.bold(args[1]))
        )

    def rm(self, target, args):
        """Removes a value from a field"""
        if self.usage(args, target, 4, '!rm <site> <field> <value>'):
            return

        site_name, field, values = args[1], args[2], args[3:]
        values = yolo_utils.uppercase_if_needed(field, values)

        try:
            result = self.db.remove_value(site_name, field, values)
        except self.db.InvalidField:
            return self.send_msg(
                target,
                '{} is an invalid field! Use !set to see a list of valid '
                'fields'.format(field)
            )

        if result['skipped'] > 0:
            return self.send_msg(
                target,
                'Site {} does not exist!'.format(Formatter.bold(site_name))
            )

        self.send_msg(
            target,
            '{}: done!'.format(Formatter.bold(site_name))
        )

    def delsite(self, target, args):
        """Deletes a site from the database"""
        if self.usage(args, target, 2, '!delsite <site>'):
            return

        response = self.db.delete_site(args[1])
        if response['deleted'] != 1:
            return self.send_msg(
                target,
                'Site {} does not exist!'.format(args[1])
            )

        self.send_msg(
            target,
            '{} has been wiped from the database!'.format(
                Formatter.bold(args[1])
            )
        )

    def help(self, target, _):
        self.send_msg(
            target,
            'Available commands: {}'.format(' '.join(self.COMMANDS))
        )

    def search(self, target, args):
        if self.usage(args, target, 3, '!search <field> <value>'):
            return

        field, values = args[1], args[2]
        values = yolo_utils.uppercase_if_needed(field, values)

        if args[1] not in sitebot_config.VALID_FIELDS:
            return self.send_msg(
                target,
                '{} is not a valid field!'.format(field)
            )

        results = self.db.search(field, values)

        if len(results) == 0:
            return self.send_msg(
                target,
                '{} was not found on any site!'.format(values)
            )

        sorted_results = [each['name'] for each in results]
        self.send_msg(
            target,
            '{}: {} found on: {}'.format(
                Formatter.bold(field),
                values,
                Formatter.bold(' '.join(sorted_results))
            )
        )

    def send_msg(self, target, msg):
        encrypted_msg = self.fish.encrypt(msg)
        if isinstance(encrypted_msg, list):
            for msg in encrypted_msg:
                self.bot.privmsg(
                    target,
                    msg
                )
        else:
            self.bot.privmsg(
                target,
                encrypted_msg
            )

    def set(self, target, args):
        """Sets a value for a site"""
        usage_string = '!set <site> <field> <value(s)>'
        if self.usage(args, target, 4, usage_string):
            valid_fields = sitebot_config.VALID_FIELDS
            valid_fields.sort()
            return self.send_msg(
                target,
                'Allowed fields: {}'.format(' '.join(valid_fields))
            )

        site_name, field, values = args[1], args[2], args[3:]
        values = yolo_utils.uppercase_if_needed(field, values)

        try:
            result = self.db.set_value(site_name, field, values)
        except self.db.InvalidField:
            return self.send_msg(
                target,
                '{} is an invalid field! Use !set to see a list of valid '
                'fields'.format(field)
            )
        except self.db.InvalidType as exc:
            return self.send_msg(
                target,
                'Field {} must be of type: {}'.format(field, exc.message)
            )

        if result['skipped'] > 0:
            return self.send_msg(
                target,
                'Site {} does not exist!'.format(site_name)
            )

        self.send_msg(
            target,
            '{}: set {} to: {}'.format(
                Formatter.bold(site_name),
                Formatter.bold(field),
                ' '.join(values)
            )
        )

    def site(self, target, args):
        """Returns site info for the given site"""
        if self.usage(args, target, 2, '!site <site_name>'):
            return

        site_info = self.db.get_site(args[1])

        if not site_info:
            return self.send_msg(
                target,
                'Site {} does not exist!'.format(args[1])
            )

        for line in Formatter.format_site(site_info):
            self.send_msg(
                target,
                line
            )

    def sites(self, target, _):
        """Returns a list of all sites in the database"""
        results = self.db.list_sites()
        if len(results) == 0:
            return self.send_msg(
                target,
                'No sites added yet! Add a site with !addsite.'
            )

        self.send_msg(
            target,
            ' '.join([site['name'] for site in results])
        )

    @classmethod
    def reload(cls, old):
        print 'reloading!'
        reload(yolofish)
        reload(db)
        return cls(old.bot)
