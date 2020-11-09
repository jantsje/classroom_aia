from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from operator import itemgetter
import random

doc = """
Classroom all-in-auction from David Zetland: https://www.kysq.org/pubs/AiA_demo.pdf
"""


class Constants(BaseConstants):
    name_in_url = 'classroom_aia'
    num_rounds = 100  # large number, real number comes from settings in config
    instructions_template = 'classroom_aia/instructions.html'
    players_per_group = None  # got to enter something


class Subsession(BaseSubsession):

    def creating_session(self):
        group_matrix = []
        players = self.get_players()
        ppg = self.session.config['players_per_group']
        for i in range(0, len(players), ppg):
            group_matrix.append(players[i:i + ppg])
        self.set_group_matrix(group_matrix)

        s = self.session.config
        if self.round_number == 1:
            self.session.vars["num_rounds"] = s["num_sessions"] * s["rounds_per_session"]
            self.session.vars["players_stopped"] = 0
            self.session.vars["total_num_endowments"] = 0
            endowments = self.session.config["endowments"]
            land = self.session.config["land"]
            for p in self.get_players():
                p.participant.vars["payoff"] = 0
                p.participant.vars["endowment"] = random.choice(endowments)
                p.participant.vars["accepted_bids"] = 0
                p.participant.vars["land"] = random.choice(land)
                self.session.vars["total_num_endowments"] += p.participant.vars["endowment"]

            self.session.vars["bids"] = []
            self.session.vars["accepted_bids"] = []
            self.session.vars["other_bids"] = []
            self.session.vars["accepted_bidders"] = []
            self.session.vars["price"] = c(0)


class Group(BaseGroup):
    endowments = models.IntegerField()
    all_bids = models.StringField(null=True)
    accepted_bids = models.StringField(null=True)
    auction_price = models.CurrencyField()
    stopped = models.IntegerField()

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
        endowments = self.session.config["endowments"]
        land = self.session.config["land"]
        for p in self.get_players():
            if p.id_in_group == 1:  # to make sure only to reset once per group
                self.session.vars["players_stopped"] = 0
                self.session.vars["bids"] = []
                self.session.vars["accepted_bids"] = []
                self.session.vars["other_bids"] = []
                self.session.vars["accepted_bidders"] = []
                self.session.vars["price"] = c(0)
                self.session.vars["total_num_endowments"] = 0
            else:
                pass
            p.participant.vars["endowment"] = random.choice(endowments)
            p.participant.vars["accepted_bids"] = 0
            p.participant.vars["land"] = random.choice(land)
            self.session.vars["total_num_endowments"] += p.participant.vars["endowment"]

    def store_bids(self):
        self.accepted_bids = str(self.session.vars["bids"])  # idea to improve: unpack Currency() here
        self.all_bids = str(self.session.vars["accepted_bids"])
        self.auction_price = self.session.vars["price"]
        self.stopped = self.session.vars["players_stopped"]
        self.endowments = self.session.vars["total_num_endowments"]


class Player(BasePlayer):
    endowment = models.IntegerField()
    bid = models.CurrencyField(min=0, max=20, initial=0, blank=True)  # min will be set in Bid template to current price
    stop = models.BooleanField()
    accepted_bids = models.IntegerField()
    total_payoff = models.CurrencyField()

    def vars_for_template(self):
        if self.subsession.round_number % self.session.config["rounds_per_session"] == 0:
            round_in_session = 3  # else it would return 0
        else:
            round_in_session = self.subsession.round_number % self.session.config["rounds_per_session"]
        return dict(endowment=self.participant.vars["endowment"],
                    land=self.participant.vars["land"],
                    num_land=len(self.participant.vars["land"]),
                    player_accepted_bids=self.participant.vars["accepted_bids"],
                    price=self.session.vars["price"],
                    num_stopped=self.session.vars["players_stopped"],
                    round_in_session=round_in_session,
                    total_endowments=self.session.vars["total_num_endowments"],
                    payoff=self.participant.vars["payoff"],
                    rounds_per_session=self.session.config["rounds_per_session"])

    def calculate_payoffs(self):
        net_units = self.participant.vars["endowment"] - self.participant.vars["accepted_bids"]
        cash_change = self.session.vars["price"] * net_units
        profit_irrigated = sum(self.participant.vars["land"][:self.participant.vars["accepted_bids"]])
        profit_dry = len(self.participant.vars["land"]) - self.participant.vars["accepted_bids"]
        profit_land = profit_irrigated + profit_dry
        profit = profit_land + cash_change
        self.participant.vars["payoff"] += profit

    def store_payoffs(self):
        self.total_payoff = self.participant.vars["payoff"]
