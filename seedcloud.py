#
# Copyright (c) 2020 bruteforcemovable
# Copyright (c) 2023 Nintendo Homebrew
#
# SPDX-License-Identifier: MIT
#

import aiomysql


class SeedCloud():
    def __init__(self, db):
        self.db = db

    async def search_seedqueue(self, term: str):
        await self.db.execute(f'select * from seedqueue where id0 like {term} or friendcode like {term}')
        items = self.db.fetchall()
        return items

