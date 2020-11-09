# classroom_aia

This application can be used to run an All-in-Water-Auction (AIA) in the classroom. It was converted to oTree for use in [this](https://studiegids.vu.nl/en/2020-2021/courses/AM_468020) course. 

To install the app to your local oTree directory, copy the folder 'classroom_aia' to your oTree Django project and extend the session configurations in your ```settings.py``` at the root of the oTree directory:

```
SESSION_CONFIGS = [
    dict(
        name='classroom_aia',
        display_name="Classroom all-in-auction",
        num_demo_participants=3,
        app_sequence=['classroom_aia'],
        timeout_seconds=15,
        endowments=[0, 1, 2, 3, 4],
        land=[[6, 4, 3, 2, 1], [8, 5, 3, 2], [10, 9, 7]],
        num_sessions=4,
        rounds_per_session=3,
        players_per_group=3,
        doc="""Make sure to set players_per_group equal to the number of participants."""
    ),
```


## Configurations
When you start a session, you can use the config file to change the following parameters:
* ```timeout_seconds``` Time in seconds after which the <strong>Bid</strong> page will auto-submit (with a bid of 0 ECU). Probably 15 seconds is fine. 
* ```num_sessions``` The number of sessions you want to play. A new session will reset the endowments and the productivity of the land of each player.
* ```rounds_per_session``` The number of rounds per session. Note that the total number of rounds equals <i>num_sessions</i> * <i>rounds_per_session</i>. This should not be more than 100 (or you should increase <i>Constants.num_rounds</i>). 
* ```players_per_group``` The number of players. Note that this should be equal to the number of participants you enter in oTree. 


## Game-play
Players start at the <strong>Getting started</strong> page, which will explain their endowments and their land. For each plot of land the payoffs are explained. There is no next button on this page. Experimenter should advance all students to the next page (oTree > Monitor > Advance slowest users). 

The next page is the <strong>Bid</strong> page. Students can enter one bid at once. Bidding is mandatory in the first round. In later rounds, students can opt to <i>skip bidding for this round</i>.
After bidding, a <strong>Results</strong> page shows how many bids were accepted, how many units are in the auction and the current auction price. The experimenter has to advance students to the next round of bidding.
The process of bidding ends either after a certain number of ```rounds_per_session``` or after a round in which all players have decided to skip bidding.

After the bidding process, students are asked to calculate their own payoff at the <strong>Calculate</strong> page. Advancing students to the next page will show the payoffs at the <strong>Calculated</strong> page.
The final page of each session gives an overview of all bids, sorted from high to low. Accepted bids are indicated in green, an unaccepted bids are indicated in grey.

The <strong>NewSession</strong> page shows a yellow warning to indicate the start of a new session. This page also shows students their cumulative payoff over the sessions.  

The <strong>SessionTotals</strong> page is only displayed at the end of the session. This page repeats the number of rounds per session and the number of sessions. It also gives the final payoff to each player, and a button to close the screen.

## Data
The game stores the bids of each player in each round in the Player class, as well as the <i>total_payoff</i> at the end of each session.
At the end of each session, the Group class also stores all bids, all accepted bids and the auction price of that particular session.


## Credits

All-in-auction by [David Zetland](https://kysq.org/). 
The paper on which this game is based can be found [here](https://www.kysq.org/pubs/AiA_Final.pdf).
Instructions for the offline version are [here](https://www.kysq.org/pubs/AiA_demo.pdf).