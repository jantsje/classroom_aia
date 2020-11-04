from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from django.db import models as djmodels

doc = """
Classroom all-in-auction from David Zetland: https://www.kysq.org/pubs/AiA_demo.pdf
"""


class Constants(BaseConstants):
    name_in_url = 'classroom_aia'
    players_per_group = 3
    num_rounds = 10
    instructions_template = 'classroom_aia/instructions.html'
    endowments = [0, 1, 2, 3, 4]
    types = ['A', 'B', 'C']
    nr_winning_bids = 4  # sum(endowments)*len(types)


class Subsession(BaseSubsession):
    def vars_for_admin_report(self):
        pass

    def creating_session(self):
        import itertools
        types = itertools.cycle(Constants.types)
        endowments = itertools.cycle(Constants.endowments)
        for p in self.get_players():
            p.type = next(types)
            p.endowment = next(endowments)
            if self.round_number == 1:
                p.participant.vars["stopped"] = False

        if self.round_number == 1:
            self.session.vars["bids"] = []
            self.session.vars["accepted_bids"] = []
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
                    self.session.vars["bids"].append(p.bid)  # p.id_in_group
        self.session.vars["bids"] = sorted(self.session.vars["bids"], reverse=True)  # to sort from high to low
        self.session.vars["accepted_bids"] = self.session.vars["bids"][:Constants.nr_winning_bids]
        if len(self.session.vars["bids"]) <= Constants.nr_winning_bids:
            self.session.vars["price"] = 0
        else:
            self.session.vars["price"] = self.session.vars["bids"][Constants.nr_winning_bids]
            # take value of bid n + 1


class Player(BasePlayer):
    endowment = models.IntegerField()
    bid = models.CurrencyField(min=0, max=20, initial=0, blank=True)  # min will be set in Bid template to current price
    type = models.StringField()
    stop = models.BooleanField()

    # def set_payoff(self):
    #     self.payoff = self.endowment - self.bid1 - self.bid2 - self.bid3 - self.bid4 - self.bid5
