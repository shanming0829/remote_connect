# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from core.utils.attribuate_dict import AttributeDict
from core.utils.descriptor import NumberDescriptor, StringDescriptor, CompileDescriptor, Descriptor, \
    type_check, BooleanDescriptor

__authors__ = "Shanming Liu"


class CommandResponse(AttributeDict):
    def __init__(self, command=None, response=None, prompt=None, action=None, timeout=None, status=False):
        self.command = command
        self.response = response
        self.prompt = prompt
        self.action = action
        self.timeout = timeout
        self.status = status

        super(CommandResponse, self).__init__()


class CommandPrompt(object):
    prompt = CompileDescriptor()

    def __init__(self, prompt=None, action=None, **kwargs):
        self.prompt = prompt
        self.action = action

        super(CommandPrompt, self).__init__()

    def search(self, s):
        return self.prompt.search(s)

    def __str__(self):
        return self.prompt.pattern


class ListCommandPromptDescriptor(Descriptor):
    def __set__(self, instance, value):
        type_check(value, (tuple, list))

        for i in value:
            type_check(i, CommandPrompt)

        super(ListCommandPromptDescriptor, self).__set__(instance, value)


class Command(object):
    command = StringDescriptor()
    prompt = ListCommandPromptDescriptor()
    timeout = NumberDescriptor()

    def __init__(self, command=None, prompt=None, timeout=None):
        self.command = command
        self.prompt = prompt
        self.timeout = timeout
        self.match_prompt = None

    def _find_regex_response(self, res):
        self.match_prompt = None
        for _p in self.prompt:
            match = _p.search(res)
            if match:
                self.match_prompt = _p
                return match.group()

    def parse_output(self, res):
        match_str = self._find_regex_response(res)
        if self.match_prompt:
            res = res[: res.rindex(match_str) + len(match_str)].strip()
            if self.command in res:
                res = res[res.index(self.command) + len(self.command) + 1:]

            status = True
            action = self.match_prompt.action

        else:
            match_str = None
            status = False
            action = None

        return CommandResponse(
            command=self.command,
            response=res,
            prompt=match_str,
            action=action,
            timeout=self.timeout,
            status=status,
        )


if __name__ == '__main__':
    prompt = [CommandPrompt('a') for i in range(5)]
    print(str(prompt[0]))
