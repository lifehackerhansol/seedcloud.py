#
# Copyright (c) 2020 bruteforcemovable
# Copyright (c) 2023 Nintendo Homebrew
#
# SPDX-License-Identifier: MIT
#

import base64
import hashlib
import struct


# SeedCloud: mostly just database wrappers
class SeedCloud():
    def __init__(self, db):
        self.db = db

    # FC: FriendCode validation
    FC_knownFriendCodes = [
        '113541082053',  # valid            
        '281029350533',  # RANDAL           
        '190853507948',  # ASP              
        '504323700474',  # BLECK            
        '044826694144',  # STHETIX          
        '448554640094',  # HANSOL          
        '242389963248',  # P3NCE            
        '285283849153',  # P3NCE            
        '435668835763',  # P3NCE            
        '345470646642',  # BLAINE LOCKLAIR  
        '139284223032',  # BLAINE LOCKLAIR  
        '392718681180',  # BLAINE LOCKLAIR  
        '332569869337',  # NINTENDOBREW     
        '422783820021',  # KELONIO 3DS      
        '238097183111',  # LOPEZ TUTORIALES 
        '109249029780',  # LOPEZ TUTORIALES 
        '517271779247',  # LOPEZ TUTORIALES 
        '220920415112',  # LOPEZ TUTORIALES 
        '384125672247',  # THEWIZWIKI       
        '143609644804',  # THEWIZWIKI       
        '354064119835',  # THEWIZWIKI       
        '547304741531',  # DARKFELIN         
        '233801992881'  # LINK GAMEPLAY   
    ]

    def FC_isPropablyCopied(self, friendCode):
        return friendCode in self.FC_knownFriendCodes

    def FC_isValid(self, fc_str: str):
        try:
            fc = int(fc_str)
        except ValueError:
            return False
        if fc > 0x7FFFFFFFFF:
            return False
        principal_id = fc & 0xFFFFFFFF
        checksum = (fc & 0xFF00000000) >> 32
        return hashlib.sha1(struct.pack('<L', principal_id)).digest()[0] >> 1 == checksum

    # ID0: ID0 validation
    def ID0_isValid(self, id0):
        try:
            int(id0, 16)
            if len(id0) == 32:
                return True
            else:
                return False
        except:
            return False

    # SQ: SeedQueue operations
    async def SQ_search(self, term: str):
        await self.db.execute(f'select * from seedqueue where id0 like {term} or friendcode like {term}')
        items = self.db.fetchall()
        return items

    # SC: SeedCloud main operations
    async def SC_status(self):
        await self.db.execute('select count(1) as number from seedqueue where state = 3')
        userCount = self.db.fetchall()[0]["number"]
        await self.db.execute('select count(1) as number from seedqueue where state = 4')
        miningCount = self.db.fetchall()[0]["number"]
        await self.db.execute('select count(1) as number from minerstatus where `action` = 0 and TIMESTAMPDIFF(SECOND, last_action_at, now()) < 60 ')
        minersStandby = self.db.fetchall()[0]["number"]

        ret = {
            "userCount": userCount,
            "miningCount": miningCount,
            "minersStandby": minersStandby
        }
        return ret

    async def SC_getMovable(self, taskID):
        if(len(taskID) != 32):
            raise ValueError("Invalid taskID")
        ret = await self.db.execute(f'select * from seedqueue where taskId like "{taskID}" and state = 5')
        if not ret:
            return None
        keyY = self.db.fetchall()[0]["keyY"]
        msed = "{}{}".format('\x00'*(288-16), keyY).encode()
        return msed

    # This is really bad and needs to be fixed
    async def SC_getPart1(self, taskID):
        if(len(taskID) != 32):
            raise ValueError("Invalid taskID")
        ret = await self.db.execute(f'select * from seedqueue where taskId like "{taskID}"')
        if not ret:
            return None
        data = self.db.fetchall()[0]
        part1b64 = base64.b64decode(data["part1b64"]).decode()
        id0 = data["id0"]
        part1 = "{}{}{}{}".format(part1b64, '\x00'*(0x8), id0, '\x00'*(0x1000 - 0x30)).encode()

        return part1
