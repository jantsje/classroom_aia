from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from operator import itemgetter
from django.db import models as djmodels

doc = """
Classroom all-in-auction from David Zetland: https://www.kysq.org/pubs/AiA_demo.pdf
"""


class Constants(BaseConstants):
    name_in_url = 'classroom_aia'
    players_per_group = 30
    num_rounds = 10
    instructions_template = 'classroom_aia/instructions.html'
    endowments = [0, 1, 2, 3, 4]
    types = ['A', 'B', 'C']
    land = [[6, 4, 3, 2, 1], [8, 5, 3, 2], [10, 9, 7]]
    nr_winning_bids = sum(endowments)*6


class Subsession(BaseSubsession):
    def vars_for_admin_report(self):
        pass

    def creating_session(self):
        import itertools
        types = itertools.cycle(Constants.types)
        endowments = itertools.cycle(Constants.endowments)
        if self.round_number == 1:
            for p in self.get_players():
                p.participant.vars["type"] = next(types)
                p.participant.vars["endowment"] = next(endowments)
                p.participant.vars["stopped"] = False
                p.participant.vars["accepted_bids"] = 0
                if p.participant.vars["type"] == "A":
                    p.participant.vars["land"] = Constants.land[0]
                elif p.participant.vars["type"] == "B":
                    p.participant.vars["land"] = Constants.land[1]
                else:  # must be C
                    p.participant.vars["land"] = Constants.land[2]

            self.session.vars["bids"] = []
            self.session.vars["accepted_bids"] = []
            self.session.vars["other_bids"] = []
            self.session.vars["accepted_bidders"] = []
            self.session.vars["price"] = 0
            self.session.vars["num_stopped_players"] = 0
            self.session.vars["end_bidding"] = False


class Group(BaseGroup):
    total_nr_bids = models.IntegerField()

    def order_bids(self):
        for p in self.get_players():
            if p.stop:
                p.participant.vars["stopped"] = True
                self.session.vars["num_stopped_players"] += 1
            else:
                if p.bid > 0:
                    self.session.vars["bids"].append([p.bid, p.id_in_group])

        self.session.vars["bids"] = sorted(self.session.vars["bids"], key=itemgetter(0), reverse=True)
        # reverse=True to sort from high to low
        self.session.vars["accepted_bids"] = [item[0] for item in self.session.vars["bids"][:Constants.nr_winning_bids]]
        self.session.vars["other_bids"] = [item[0] for item in self.session.vars["bids"][Constants.nr_winning_bids:]]
        self.session.vars["accepted_bidders"] = [item[1] for item in self.session.vars["bids"][:Constants.nr_winning_bids]]
        print(self.session.vars["accepted_bidders"], 'accepted bidders')
        if len(self.session.vars["bids"]) <= Constants.nr_winning_bids:
            self.session.vars["price"] = 0
        else:
            self.session.vars["price"] = self.session.vars["bids"][Constants.nr_winning_bids][0]
            # take value of bid n + 1

        for p in self.get_players():
            p.accepted_bids = self.session.vars["accepted_bidders"].count(p.id_in_group)
            # to store for results page:
            p.participant.vars["accepted_bids"] = self.session.vars["accepted_bidders"].count(p.id_in_group)


class Player(BasePlayer):
    endowment = models.IntegerField()
    bid = models.CurrencyField(min=0, max=20, initial=0, blank=True)  # min will be set in Bid template to current price
    type = models.StringField()
    stop = models.BooleanField()
    accepted_bids = models.IntegerField()

    def vars_for_template(self):
        return dict(endowment=self.participant.vars["endowment"],
                    type=self.participant.vars["type"],
                    land=self.participant.vars["land"],
                    num_land=len(self.participant.vars["land"]),
                    player_accepted_bids=self.participant.vars["accepted_bids"],
                    price=self.session.vars["price"],)

