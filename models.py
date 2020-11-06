from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from operator import itemgetter
from django.db import models as djmodels
import random

doc = """
Classroom all-in-auction from David Zetland: https://www.kysq.org/pubs/AiA_demo.pdf
"""


class Constants(BaseConstants):
    name_in_url = 'classroom_aia'
    players_per_group = 3
    num_sessions = 4
    num_rounds_per_session = 3
    num_rounds = num_sessions * num_rounds_per_session
    instructions_template = 'classroom_aia/instructions.html'
    endowments = [0, 1, 2, 3, 4]
    types = ['A', 'B', 'C']
    land = [[6, 4, 3, 2, 1], [8, 5, 3, 2], [10, 9, 7]]


class Subsession(BaseSubsession):
    def vars_for_admin_report(self):
        pass

    def creating_session(self):
        if self.round_number == 1:
            self.session.vars["players_stopped"] = 0
            self.session.vars["total_num_endowments"] = 0
            for p in self.get_players():
                p.participant.vars["payoff"] = 0
                p.participant.vars["type"] = random.choice(Constants.types)
                p.participant.vars["endowment"] = random.choice(Constants.endowments)
                p.participant.vars["accepted_bids"] = 0
                if p.participant.vars["type"] == "A":
                    p.participant.vars["land"] = Constants.land[0]
                elif p.participant.vars["type"] == "B":
                    p.participant.vars["land"] = Constants.land[1]
                else:  # must be C
                    p.participant.vars["land"] = Constants.land[2]
                self.session.vars["total_num_endowments"] += p.participant.vars["endowment"]

            self.session.vars["bids"] = []
            self.session.vars["accepted_bids"] = []
            self.session.vars["other_bids"] = []
            self.session.vars["accepted_bidders"] = []
            self.session.vars["price"] = c(0)


class Group(BaseGroup):
    total_nr_bids = models.IntegerField()

    def order_bids(self):
        for p in self.get_players():
            if p.stop:
                self.session.vars["players_stopped"] += 1
            else:
                if p.bid > 0:
                    self.session.vars["bids"].append([p.bid, p.id_in_group])

        self.session.vars["bids"] = sorted(self.session.vars["bids"], key=itemgetter(0), reverse=True)
        # reverse=True to sort from high to low
        self.session.vars["accepted_bids"] = [item[0] for item in self.session.vars["bids"][:self.session.vars["total_num_endowments"]]]
        self.session.vars["other_bids"] = [item[0] for item in self.session.vars["bids"][self.session.vars["total_num_endowments"]:]]
        self.session.vars["accepted_bidders"] = [item[1] for item in self.session.vars["bids"][:self.session.vars["total_num_endowments"]]]
        if len(self.session.vars["bids"]) <= self.session.vars["total_num_endowments"]:
            self.session.vars["price"] = c(0)
        else:
            self.session.vars["price"] = self.session.vars["bids"][self.session.vars["total_num_endowments"]][0]
            # take value of bid n + 1

        for p in self.get_players():
            p.accepted_bids = self.session.vars["accepted_bidders"].count(p.id_in_group)
            # to store for results page:
            p.participant.vars["accepted_bids"] = self.session.vars["accepted_bidders"].count(p.id_in_group)
        
    def reset_session(self):
        print("now resetting session")
        self.session.vars["players_stopped"] = 0
        self.session.vars["bids"] = []
        self.session.vars["accepted_bids"] = []
        self.session.vars["other_bids"] = []
        self.session.vars["accepted_bidders"] = []
        self.session.vars["price"] = c(0)
        self.session.vars["total_num_endowments"] = 0
        
        for p in self.get_players():
            p.participant.vars["type"] = random.choice(Constants.types)
            p.participant.vars["endowment"] = random.choice(Constants.endowments)
            p.participant.vars["accepted_bids"] = 0
            if p.participant.vars["type"] == "A":
                p.participant.vars["land"] = Constants.land[0]
            elif p.participant.vars["type"] == "B":
                p.participant.vars["land"] = Constants.land[1]
            else:  # must be C
                p.participant.vars["land"] = Constants.land[2]
            self.session.vars["total_num_endowments"] += p.participant.vars["endowment"]


class Player(BasePlayer):
    endowment = models.IntegerField()
    bid = models.CurrencyField(min=0, max=20, initial=0, blank=True)  # min will be set in Bid template to current price
    type = models.StringField()
    stop = models.BooleanField()
    accepted_bids = models.IntegerField()

    def vars_for_template(self):
        if self.subsession.round_number % Constants.num_rounds_per_session == 0:
            round_in_session = 3  # else it would return 0
        else:
            round_in_session = self.subsession.round_number % Constants.num_rounds_per_session
        return dict(endowment=self.participant.vars["endowment"],
                    type=self.participant.vars["type"],
                    land=self.participant.vars["land"],
                    num_land=len(self.participant.vars["land"]),
                    player_accepted_bids=self.participant.vars["accepted_bids"],
                    price=self.session.vars["price"],
                    num_stopped=self.session.vars["players_stopped"],
                    round_in_session=round_in_session,
                    total_endowments=self.session.vars["total_num_endowments"],
                    payoff = self.participant.vars["payoff"])

    def calculate_payoffs(self):
        net_units = self.participant.vars["endowment"] - self.participant.vars["accepted_bids"]
        cash_change = self.session.vars["price"] * net_units
        profit_irrigated = sum(self.participant.vars["land"][:self.participant.vars["accepted_bids"]])
        profit_dry = len(self.participant.vars["land"]) - self.participant.vars["accepted_bids"]
        profit_land = profit_irrigated + profit_dry
        profit = profit_land + cash_change
        self.participant.vars["payoff"] += profit
