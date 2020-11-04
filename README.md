# classroom_aia

This application can be used to run an All-in-Water-Auction (AIA) in the classroom. It was converted to oTree for use in [this](https://studiegids.vu.nl/en/2019-2020/courses/AM_468020) course. 

To install the app to your local oTree directory, copy the folder 'classroom_aia' to your oTree Django project and extend the session configurations in your ```settings.py``` at the root of the oTree directory:

```
SESSION_CONFIGS = [
    dict(
        name='classroom_aia',
        display_name="Classroom all-in-auction",
        num_demo_participants=3,
        app_sequence=['classroom_aia'],
        demo=False,
    ),
                  ]
```


## Treatments

To be added.


## Credits

All-in-auction by [David Zetland](https://kysq.org/). 
The paper on which this game is based can be found [here](https://www.kysq.org/pubs/AiA_Final.pdf).
Instructions for the offline version are [here](https://www.kysq.org/pubs/AiA_demo.pdf).