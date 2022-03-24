from otree.api import *
import numpy as np
c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'my_garp'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    goods = models.StringField(initial="")
    scenarios = models.StringField(initial="")
    names = models.StringField(initial="")
    descriptions = models.StringField(initial="")
    budgets = models.StringField(initial="")
    prices = models.StringField(initial="")


class Player(BasePlayer):

    numGoods = models.StringField(initial="")
    numScenarios = models.StringField(initial="")
    nameGoods = models.StringField(initial="")
    descGoods = models.StringField(initial="")
    budgetGoods = models.StringField(initial="")
    priceGoods = models.StringField(initial="")

    response = models.StringField()
    value = models.StringField()
    matrix = models.StringField()
    violation = models.StringField()

# FUNCTIONS

# PAGES

class Parameters(Page):
    form_model = 'player'
    form_fields = ['numGoods','nameGoods','numScenarios','priceGoods','budgetGoods','descGoods']

    #parameters page is only displayed when group variable is empty
    def is_displayed(player: Player):
        return player.group.goods == ""

    #pass parameters to group when it is specified
    #get the player who has defined the parameters and assign those parameters to others in group
    def before_next_page(player, timeout_happened):
        sorted_players = sorted(player.group.get_players(), key=lambda x: (x.numGoods))
        for p in player.group.get_players():
            player.group.goods = sorted_players[-1].numGoods
            player.group.scenarios = sorted_players[-1].numScenarios
            player.group.names = sorted_players[-1].nameGoods
            player.group.descriptions = sorted_players[-1].descGoods
            player.group.budgets = sorted_players[-1].budgetGoods
            player.group.prices = sorted_players[-1].priceGoods


class Decision(Page):
    form_model = 'player'
    form_fields = ['response']

    def vars_for_template(player):
        return dict(
            numGoods=player.group.goods,
            numScenarios=player.group.scenarios,
            nameGoods = player.group.names,
            descGoods=player.group.descriptions,
            budgetGoods=player.group.budgets,
            priceGoods=player.group.prices
        )

class Results(Page):

    def vars_for_template(player):

        num_scenarios= int(player.group.scenarios)
        num_goods= int(player.group.goods)
        price_goods = player.group.prices[1:-1]
        responses = player.response[1:-1]


        #make string responses and prices into lists
        rlists = []
        plists = []
        rlisty = responses.split(",")
        plisty = price_goods.split(",")
        for i in range(0, num_scenarios):
            start = i * num_goods
            end = start + num_goods
            rlists.append(rlisty[start:end])
            plists.append(plisty[start:end])

        #make string list into integers
        rlist = np.array(rlists).astype('int')
        plist = np.array(plists).astype('int')

        #create matrix of price x quantity and convert them into list
        px = np.transpose(np.inner(rlist,plist))
        px = px.tolist()
        rlist = rlist.tolist()
        plist = plist.tolist()

        #literal count of violations to GARP following Cox (1997)
        violate = 0
        for j in range(0, num_scenarios):
            for i in range(0, num_scenarios):
                #if Xj R Xi (p1x1 > p1x2)
                if px[j][j] >= px[j][i]:
                    #if Xi notS Xj, pass violation (p2x1 => p2x2)
                    if px[i][j] >= px[i][i]:
                        violate = violate
                    #if Xi S Xj, add to violation (p2x1 < p2x2)
                    elif px[i][j] < px[i][i]:
                        violate = violate+1
                #if Xj notR Xi, pass violation (p1x1 < p1x2)
                if px[j][j] < px[j][i]:
                    violate = violate

        #calculate afriat efficiency index
        eindex = np.zeros(shape=(num_scenarios,num_scenarios))
        for j in range(0, num_scenarios):
            for i in range(0, num_scenarios):
                #if Xj R Xi
                if px[j][j] >= px[j][i]:
                    if px[i][j] >= px[i][i]:
                        # if Xi notS Xj, pass index
                        eindex[i][j] = 1
                        # if Xi S Xj, calculate index that just equates the total budget (largest index value)
                    elif px[i][j] < px[i][i]:
                        eindex[i][j] = px[i][j]/px[i][i]
                #if Xj notR Xi, pass index
                if px[j][j] < px[j][i]:
                    eindex[i][j] = 1

        #find minimum (most restrictive) efficiency score across all choices
        index = eindex.min()

        return dict(
            numGoods=player.group.goods,
            numScenarios=player.group.scenarios,
            nameGoods=player.group.names,
            descGoods=player.group.descriptions,
            budgetGoods=player.group.budgets,
            priceGoods=player.group.prices,
            response = player.response,
            rlist = rlist,
            plist = plist,
            px = px,
            violate = violate,
            eindex = eindex,
            index = index
        )



class ResultsWaitPage(WaitPage):
    pass



page_sequence = [Parameters,Decision,Results]
