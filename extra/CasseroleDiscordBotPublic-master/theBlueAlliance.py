import os,sys
sys.path.append("..")
import APIKeys

import tbapy

class TBAInfo():

    def __init__(self):
        print("Attemting to log into TheBlueAlliance.com...")
        self.tba = tbapy.TBA(APIKeys.TBA_KEY)
        print("Login Complete!")

    def lookupTeamName(self, number):
        teamData = self.tba.team(number)
        teamName = teamData.nickname
        response = teamName

        return response

