from .models import Constants
from ._builtin import Page, WaitPage


class Introduction(Page):
    """Description of the game: How to play and returns expected"""

    def is_displayed(self):
        return self.subsession.round_number == 1

    def vars_for_template(self):
        return self.player.vars_for_template()


class Bid(Page):
    """Player: Choose how much to bid"""

    form_model = 'player'

    # timeout_seconds = 15

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
        return self.session.vars["players_stopped"] < Constants.players_per_group and \
               self.subsession.round_number < Constants.num_rounds

    def vars_for_template(self):
        return self.player.vars_for_template()


class AfterBidWP(WaitPage):
    after_all_players_arrive = 'order_bids'

    def is_displayed(self):
        return self.session.vars["players_stopped"] < Constants.players_per_group and \
               self.subsession.round_number < Constants.num_rounds

        # body_text = "Waiting for other participants to contribute."


class Results(Page):
    """Players payoff: How much each has earned"""

    def is_displayed(self):
        return self.session.vars["players_stopped"] < Constants.players_per_group and \
               self.subsession.round_number < Constants.num_rounds

    def vars_for_template(self):
        return dict(self.player.vars_for_template(),
                    accepted_bids=self.session.vars["accepted_bids"],
                    num_accepted_bids=len(self.session.vars["accepted_bids"]))


class Calculate(Page):
    """Students are asked to calculate payoff"""

    def is_displayed(self):
        return self.subsession.round_number % Constants.num_rounds_per_session == 0

    def vars_for_template(self):
        return self.player.vars_for_template()


class Calculated(Page):
    """Students shown their payoffs"""

    def is_displayed(self):
        return self.subsession.round_number % Constants.num_rounds_per_session == 0

    def vars_for_template(self):
        net_units = self.player.participant.vars["endowment"] - self.player.participant.vars["accepted_bids"]
        cash_change = self.session.vars["price"] * net_units
        profit_irrigated = sum(self.participant.vars["land"][:self.player.participant.vars["accepted_bids"]])
        profit_dry = len(self.player.participant.vars["land"]) - self.player.participant.vars["accepted_bids"]
        profit_land = profit_irrigated + profit_dry
        profit = profit_land + cash_change
        return dict(self.player.vars_for_template(),
                    net_units=net_units,
                    cash_change=cash_change,
                    profit_land=profit_land,
                    profit=profit)


class FinalResults(Page):
    """Final payoff"""

    def is_displayed(self):
        return self.subsession.round_number % Constants.num_rounds_per_session == 0

    def vars_for_template(self):
        return {"other_bids": self.session.vars["other_bids"],
                "accepted_bids": self.session.vars["accepted_bids"],
                "all_bids": self.session.vars["bids"],
                "num_accepted_bids": len(self.session.vars["accepted_bids"]),
                "price": self.session.vars["price"],
                "num_stopped_players": self.session.vars["players_stopped"],
                "session_num": int(self.subsession.round_number / Constants.num_rounds_per_session)}


class NewSession(Page):
    """Warning page that a new session will start"""

    def is_displayed(self):
        return self.subsession.round_number % Constants.num_rounds_per_session == 0

    def before_next_page(self):
        self.player.reset_session()


page_sequence = [
    Introduction,
    Bid,
    AfterBidWP,
    Results,
    Calculate,
    Calculated,
    FinalResults,
    NewSession
]
