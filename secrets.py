#!/usr/bin/python3

# EasyGal - A simple, photo gallery for the web based on Python3.
# Copyright (C) 2015  Andreas Hofmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import random
import os

from getpass import getpass

from passlib.hash import pbkdf2_sha256 as pbkdf2

class SecretsStorage:
    def __init__(self, filename):
        self._file = filename
        self._users = {}
        self._random = ""

        if os.path.exists(filename):
            self._read_secrets()
        else:
            self._init_secrets()

    def _read_secrets(self):
        with open(self._file, "r") as f:
            firstline = True
            for l in f.read().split("\n"):
                if not len(l):
                    break
                if firstline:
                    self._random = l
                    firstline = False
                else:
                    user, pwhash = l.split(" ")
                    self._users[user] = pwhash

    def _init_secrets(self):
        print("Password-file not found - initializing user.")
        print("Enter username:")
        new_user = input()
        new_pw = getpass("New password:")
        self._random = self._generate_random_str()
        self.set_pw(new_user, new_pw)

    def _write_secrets(self):
        with open(self._file, 'w') as f:
            f.write(self._random + "\n")
            for u in self._users.keys():
                f.write(u + " " + self._users[u] + "\n")

    @staticmethod
    def _generate_random_str():
        return ''.join(chr(random.randint(40,126)) for i in range(64))

    def set_pw(self, user, pw):
        pwhash = pbkdf2.encrypt(pw, rounds=50000, salt_size=16)
        self._users[user] = pwhash
        self._write_secrets()

    def check_pw(self, user, pw):
        if user in self._users:
            return pbkdf2.verify(pw, self._users[user])
        return False

    @property
    def secret(self):
        return self._random
