# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from core import App, test_step

__authors__ = "Shanming Liu"

app = App('sessions.yaml')


@test_step('commnad')
def test_ssh_session():
    ssh_session = app.ssh_session
    print ssh_session.default_prompt

    telnet_session = app.telnet_session
    print(telnet_session.default_prompt)

if __name__ == '__main__':
    test_ssh_session()
