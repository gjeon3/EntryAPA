from otree.api import *

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'Risk'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gamble = models.IntegerField(initial=None,
                                 choices=[[1],
                                          [2],
                                          [3],
                                          [4],
                                          [5]])

# PAGES
class Selection(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Prediction(Page):
    pass


page_sequence = [Selection, Prediction]
