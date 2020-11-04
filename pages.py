from . import models
from .models import Constants
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from otree.constants import timeout_happened


class Introduction(Page):
    """Description of the game: How to play and returns expected"""
    pass

    def is_displayed(self):
        return self.subsession.round_number == 1


class Bid(Page):
    """Player: Choose how much to contribute"""

    form_model = 'player'

    timeout_seconds = 20

    def before_next_page(self):
        if self.timeout_happened:
            if self.round_number == 1:
                self.player.bid = 0
            else:
                self.player.stop = True

    def get_form_fields(self):
        fields = ['bid']
        if self.round_number > 1:
            fields.append('stop')
        return fields

    def is_displayed(self):
        return self.session.vars["num_stopped_players"] < Constants.players_per_group and \
               self.subsession.round_number <= Constants.num_rounds

    def vars_for_template(self):
        return{'round_number': self.round_number,
               'stopped': self.participant.vars["stopped"],
               'price': self.session.vars["price"]}


class AfterBidWP(WaitPage):
    after_all_players_arrive = 'order_bids'

    def is_displayed(self):
        return self.session.vars["num_stopped_players"] < Constants.players_per_group and \
               self.subsession.round_number <= Constants.num_rounds

        # body_text = "Waiting for other participants to contribute."


class Results(Page):
    """Players payoff: How much each has earned"""

    timeout_seconds = 5

    def is_displayed(self):
        return self.session.vars["num_stopped_players"] < Constants.players_per_group and \
               self.subsession.round_number <= Constants.num_rounds

    def vars_for_template(self):
        return {"accepted_bids": self.session.vars["accepted_bids"],
                "num_accepted_bids": len(self.session.vars["accepted_bids"]),
                "price": self.session.vars["price"],
                "num_stopped_players": self.session.vars["num_stopped_players"]}


class Calculate(Page):
    """Students are asked to calculate payoff"""

    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        return {"price": self.session.vars["price"]}  # add later: player.num_accepted_bids


class FinalResults(Page):
    """Final payoff"""

    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        return {"other_bids": self.session.vars["bids"][len(self.session.vars["accepted_bids"]):],
                "accepted_bids": self.session.vars["accepted_bids"],
                "all_bids": self.session.vars["bids"],
                "num_accepted_bids": len(self.session.vars["accepted_bids"]),
                "price": self.session.vars["price"],
                "num_stopped_players": self.session.vars["num_stopped_players"]}


page_sequence = [
    Introduction,
    Bid,
    AfterBidWP,
    Results,
    Calculate,
    FinalResults
]
