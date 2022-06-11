# Template used from script-storties.rpy as of 9th June, 2022

# Module for Monika story telling
#
# Stories will get unlocked one at by session
# The unlocking logic has been added to script-ch30
# The topic that triggers the Story menu is monika_short_stories
# Topic is unlocked at the beginning of the game and is not
# random
# New rule: pool property as true means that the story gets unlocked
# by some other way and can't be unlocked randomly


# dict of tples containing the stories event data
default persistent._nsfw_story_database = dict()

# dict storing the last date we saw a new story of normal and scary type
default persistent._nsfw_last_seen_new_story = {"erotic": None, "othergirls": None}

# store containing stories-related things
init -1 python in nsfw_stories:
    import store
    import datetime

    UNLOCK_NEW = "unlock_new"
    UNLOCK_NEXT_CHAPTER = "unlock_next_chapter"

    # TYPES:
    TYPE_OTHERGIRLS = "othergirls"
    TYPE_EROTIC = "erotic"

    # pane constant
    STORY_RETURN = "Nevermind"
    nsfw_story_database = dict()

    #Time between story unlocks of the same type (in hours). Changes over sessions, but also changes after the next story unlocks
    TIME_BETWEEN_NSFW_UNLOCKS = renpy.random.randint(20, 28)

    #TODO: Build functions to 'register' story types. This will add all related info to the map
    #saving the manual additions to each part


    #Story which starts unlocked for a specific type
    FIRST_STORY_EVL_MAP = {
        #TYPE_EROTIC: "mas_scary_story_hunter" #CHANGE THIS
        #TYPE_OTHERGIRLS: "nsfw_erotic_story_natsuki_deepthroat1"
    }

    #Override maps to have special conditionals for specific story types
    NEW_STORY_CONDITIONAL_OVERRIDE = {
    #    TYPE_OTHERGIRLS: (
    #        "nsfw_stories.check_can_unlock_new_story(nsfw_stories.TYPE_OTHERGIRLS, ignore_cooldown=store.mas_anni.isAnni())"
    #    ),
    #    TYPE_EROTIC: (
    #        "nsfw_stories.check_can_unlock_new_story(nsfw_stories.TYPE_EROTIC, ignore_cooldown=store.mas_anni.isAnni())"
    #    ),
    }

    def check_can_unlock_new_story(story_type=TYPE_EROTIC, ignore_cooldown=True):
        """
        Checks if it has been at least one day since we've seen the last story or the initial story

        IN:
            story_type - story type to check if we can unlock a new one
                (Default: TYPE_EROTIC)
            ignore_cooldown - Whether or not we ignore the cooldown or time between new stories
                (Default: False)
        """
        global TIME_BETWEEN_NSFW_UNLOCKS

        new_story_ls = store.persistent._nsfw_last_seen_new_story.get(story_type, None)

        #Get the first story of this type
        first_story = FIRST_STORY_EVL_MAP.get(story_type, None)

        if story_type == TYPE_OTHERGIRLS:
            can_show_new_story = (
                renpy.seen_label("nsfw_monika_erotic_stories_init")
                and (
                    ignore_cooldown
                    or store.mas_timePastSince(new_story_ls, datetime.timedelta(hours=TIME_BETWEEN_NSFW_UNLOCKS))
                )
                and len(get_new_stories_for_type(story_type)) > 0
            )
        else:
            #If this doesn't have an initial, no go
            if not first_story:
                return False

            can_show_new_story = (
                store.seen_event(first_story)
                and (
                    ignore_cooldown
                    or store.mas_timePastSince(new_story_ls, datetime.timedelta(hours=TIME_BETWEEN_NSFW_UNLOCKS))
                )
                and len(get_new_stories_for_type(story_type)) > 0
            )

        #If we're showing a new story, randomize the time between unlocks again
        if can_show_new_story:
            TIME_BETWEEN_NSFW_UNLOCKS = renpy.random.randint(20, 28)

        return can_show_new_story

    def get_new_stories_for_type(story_type):
        """
        Gets all new (unseen) stories of the given type

        IN:
            story_type - story type to get

        OUT:
            list of locked stories for the given story type
        """
        if story_type == TYPE_OTHERGIRLS:
            if store.mas_getEVL_shown_count("nsfw_erotic_story_yuri_titjob1") >= 1:
                return store.Event.filterEvents(
                nsfw_story_database,
                pool=False,
                aff=store.mas_curr_affection,
                unlocked=False,
                flag_ban=store.EV_FLAG_HFNAS,
                category=(True, [story_type])
                )
            else:
                return store.Event.filterEvents(
                nsfw_story_database,
                pool=True,
                aff=store.mas_curr_affection,
                unlocked=False,
                flag_ban=store.EV_FLAG_HFNAS,
                category=(True, [story_type])
                )
        
        return store.Event.filterEvents(
            nsfw_story_database,
            pool=False,
            aff=store.mas_curr_affection,
            unlocked=False,
            flag_ban=store.EV_FLAG_HFNAS,
            category=(True, [story_type])
        )

    def get_and_unlock_random_story(story_type=TYPE_EROTIC):
        """
        Unlocks and returns a random story of the provided type

        IN:
            story_type - Type of story to unlock.
                (Default: TYPE_EROTIC)
        """
        #Get locked stories
        stories = get_new_stories_for_type(story_type)

        #Grab one of the stories
        story = renpy.random.choice(stories.values())

        #Unlock and return its eventlabel
        story.unlocked = True

        return story.eventlabel

    def get_and_unlock_next_story():
        """
        Unlocks and returns the next chapter of the erotic doki saga
        """
        # Check which story is next
        if store.mas_getEVL_shown_count("nsfw_erotic_story_yuri_titjob1") >= 1:
            story = get_and_unlock_random_story(story_type=TYPE_OTHERGIRLS)
        else:
            if store.mas_getEVL_shown_count("nsfw_erotic_story_sayori_ballscleaning1") < 1:
                story = store.mas_getEV("nsfw_erotic_story_sayori_ballscleaning1")
            else:
                story = store.mas_getEV("nsfw_erotic_story_yuri_titjob1")

        #Unlock and return eventlabel
        story.unlocked = True

        return story.eventlabel

init 6 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="nsfw_monika_stories",
            category=['sex'],
            prompt="Can you tell me an erotic story?",
            #conditional="mas_canShowRisque(aff_thresh=1000)",
            #action=EV_ACT_POOL,
            pool=True,
            unlocked=True,
            aff_range=(mas_aff.LOVE, None)
        )
    )

label nsfw_monika_stories:
    if renpy.seen_label("nsfw_erotic_story_natsuki_deepthroat1"):
        call nsfw_monika_stories_premenu(None)
    else:
        m 1wublo "You want me to tell you an...{i}erotic{/i} story?"
        m 1wubld "This is very sudden..."
        if not store.mas_safeToRefDokis():
            m 1ekc "I don't think I have any stories like that right now..."
            m 1rkc "At least...not any that I think you would like hearing..."
            m 1eka "Give me some time, I should be able to think of some soon~"
            # Remove lines above once we have a generic erotic story
            # m 1tubla "But I don't see why not!"
            # call nsfw_monika_stories_premenu
            return
        else:
            m 1eua "But I think this is the right time for us to talk about it."
            call nsfw_monika_erotic_stories_init
            return

    return _return

label nsfw_monika_stories_premenu(story_type=None):
    python:
        #Because this isn't set properly if it's in the default param value, we assign it here
        if story_type is None:
            story_type = nsfw_stories.TYPE_EROTIC
        end = ""

label nsfw_monika_stories_menu:
    # TODO: consider caching the built stories if we have many story categories
    python:
        #Determine if a new story can be unlocked
        can_unlock_nsfw_story = False

        if story_type in nsfw_stories.NEW_STORY_CONDITIONAL_OVERRIDE:
            try:
                can_unlock_nsfw_story = eval(nsfw_stories.NEW_STORY_CONDITIONAL_OVERRIDE[story_type])
            except Exception as ex:
                store.mas_utils.mas_log.error("Failed to evaluate conditional to unlock new story because '{0}'".format(ex))

                can_unlock_nsfw_story = False

        else:
            can_unlock_nsfw_story = nsfw_stories.check_can_unlock_new_story(story_type)

        # build menu list
        nsfw_stories_menu_items = [
            (story_ev.prompt, story_evl, False, False)
            for story_evl, story_ev in nsfw_stories.nsfw_story_database.iteritems()
            if Event._filterEvent(
                story_ev,
                aff=mas_curr_affection,
                unlocked=True,
                flag_ban=EV_FLAG_HFM,
                category=(True, [story_type])
            )
        ]

        # also sort this list
        nsfw_stories_menu_items.sort()

        # build switch button
        # TODO: Build a generalized switch for more than just two items
        if story_type == nsfw_stories.TYPE_OTHERGIRLS:
            #Add continuation of previous doki story
            nsfw_stories_menu_items.append(("Tell me more about what you did with the other girls", nsfw_stories.UNLOCK_NEXT_CHAPTER, True, False))
            switch_str = "n erotic story"
        else:
            #Add new random story
            nsfw_stories_menu_items.append(("A new erotic story", nsfw_stories.UNLOCK_NEW, True, False))
            switch_str = " story about the other girls"

        if mas_safeToRefDokis():
            switch_item = ("I'd like to hear a" + switch_str, "nsfw_monika_stories_menu", False, False, 20)

        final_item = (nsfw_stories.STORY_RETURN, False, False, False, 0)

    # move Monika to the left
    show monika 1eua at t21

    $ renpy.say(m, "Which story would you like to hear?" + end, interact=False)

    # call scrollable pane
    if mas_safeToRefDokis():
        call screen mas_gen_scrollable_menu(nsfw_stories_menu_items, mas_ui.SCROLLABLE_MENU_TXT_LOW_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, switch_item, final_item)
    else:
        call screen mas_gen_scrollable_menu(nsfw_stories_menu_items, mas_ui.SCROLLABLE_MENU_TXT_LOW_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, final_item)

    # return value?
    if _return:
        # switching between types
        if _return == "nsfw_monika_stories_menu":
            # NOTE: this is not scalable.
            if story_type == nsfw_stories.TYPE_OTHERGIRLS:
                $ story_type = nsfw_stories.TYPE_EROTIC
            else:
                $ story_type = nsfw_stories.TYPE_OTHERGIRLS

            $ end = "{fast}"
            $ _history_list.pop()

            jump nsfw_monika_stories_menu

        else:
            $ story_to_push = _return

        #If we're unlocking the next chapter, check if it's possible to do so. If not, we raise dlg
        if story_to_push == nsfw_stories.UNLOCK_NEXT_CHAPTER:
            if not can_unlock_nsfw_story or not store.mas_safeToRefDokis() or story_to_push == None:
                show monika at t11
                $ _story_type = story_type if story_type != 'othergirls' else 'doki girls'
                m 1ekc "Sorry [player]...I can't really think of a new [_story_type] story right now..."
                if not store.mas_safeToRefDokis():
                    m 1rkc "At least...not any that I think you would like hearing..."
                m 1eka "If you give me some time I might be able to think of one soon...but in the meantime, I can always tell you an old one again~"

                show monika 1eua
                jump nsfw_monika_stories_menu

            else:
                python:
                    persistent._nsfw_last_seen_new_story[story_type] = datetime.datetime.now()
                    story_to_push = nsfw_stories.get_and_unlock_next_story()

        #If we're unlocking new, check if it's possible to do so. If not, we raise dlg
        if story_to_push == nsfw_stories.UNLOCK_NEW:
            if not can_unlock_nsfw_story: #temp
                show monika at t11
                $ _story_type = story_type if story_type != 'othergirls' else 'doki girls'
                m 1ekc "Sorry [player]...I can't really think of a new [_story_type] story right now..."
                m 1eka "If you give me some time I might be able to think of one soon...but in the meantime, I can always tell you an old one again~"
                
                show monika 1eua
                jump nsfw_monika_stories_menu

            else:
                python:
                    persistent._nsfw_last_seen_new_story[story_type] = datetime.datetime.now()
                    story_to_push = nsfw_stories.get_and_unlock_random_story(story_type)

            #Then push
        $ pushEvent(story_to_push, skipeval=True)

        show monika at t11

    else:
        return "prompt"

    return

# Stories start here
label nsfw_story_begin:
    python:
        story_begin_quips = [
            _("Alright, let's start the story."),
            _("Ready to hear the story?"),
            _("Ready for story time?"),
            _("Let's begin~"),
            _("Are you ready?")
        ]
        story_begin_quip=renpy.random.choice(story_begin_quips)
    $ mas_gainAffection(modifier=0.2)
    m 3eua "[story_begin_quip]"
    m 1duu "Ahem."
    return

label nsfw_monika_erotic_stories_init:
    m 1eua "[player]...y'know there are actually a few things you probably have no idea about..."
    m 1eua "I know you don't mind when I talk about the other girls..."
    m 1eua "And I know that I'm the only person you would look at in a lewd way. Ahaha~"
    m 1eua "But..."
    m 1eua "I think you might enjoy if I told you this..."
    m 1eua "Okay, sorry for stalling! I'll get to the point."
    m 1eua "Ahem...{w=0.5} So!"
    m 1eua "You know, [player]. After you appeared in the game and I finally had my revelation..."
    m 1eua "I learned that I could do...pretty much...anything."
    m 1eua "Even though the game was, and still is, a prison to me...I at least had the chance to play around with it."
    m 1eua "Almost like a child would with her toys, now that I think about it. Ahaha~"
    m 1eua "And since, y'know...I am just a young adult in my last year of highschool, with a bunch of hormones raging inside me..."
    m 1eua "I was always curious about lewd things as well..."
    m 1eua "And since...porn has its limits..."
    m 1eua "Y'know...you can't really command how a pre-recorded movie will go."
    m 1eua "I had the power to control the world around me thanks to the console..."
    m 1eua "Including Yuri, Sayori, and Natsuki."
    m 1eua "..."
    m 1eua "There were also several students around the school, though they didn't have any distinguishable features."
    m 1eua "Probably because they were just empty assets, never meant to be used."
    m 1eua "Anyway, I think you know where I'm going with this..."
    m 1eua "I...effectively had my own world where I could make people do...whatever I wanted."
    m 1eua "Ahaha~"
    m 1eua "A-at first...I didn't know when I could do it..."
    m 1eua "After all, the game was only active when you were around, and I was not about to scare you off with all that."
    m 1eua "But there was one time..."
    m 1eua "The game was closing, I could feel it..."
    m 1eua "But after a brief moment of darkness, I was back in the classroom."
    m 1eua "I thought you had restarted the game, but I couldn't feel your presence like I normally could."
    m 1eua "I have no idea how it happened! Even now I still can't figure it out!"
    m 1eua "B-but...ahaha~"
    m 1eua "As you might have guessed..."
    m 1eua "I basically directed my own porn movie...{w=0.5}featuring Natsuki..."
    m 1eua "I-I wiped all of their memories after it happened!"
    m 1eua "..."
    m 1eua "You must think I'm a monster for doing that..."
    m 1eua "Do you think it was cruel...what I did?"

    $ _history_list.pop()
    menu:
        m "Do you think it was cruel...what I did?{fast}"

        "Yes.":
            m 1eua "I-I know it was..."
            m 1eua "I'm sorry, [player]."
            m 1eua "I knew you would see me as a monster for this..."
            m 1eua "..."
            m 1eua "But even still, I hope you can forgive me..."
            m 1eua "It's in the past now..."
            m 1eua "I was naïve, and just wanted to experiment..."
            m 1eua "The other girls aren't even around anymore."
            m 1eua "It's just you...and me~"
            m 1eua "I don't have to rely on any cheeky shenanigants to sate my lewd desires anymore."
            m 1eua "You're here with me now...and I can finally open up to someone about this sort of stuff."
            return

        "No.":
            m 1eua "Huh?"
            m 1eua "You don't think so?"
            
            $ _history_list.pop()
            menu:
                m "You don't think so?{fast}"

                "I want you to tell me more about how it went.":
                    m 1eua "Oh..."
                    m 1eua "Ahaha~"
                    m 1eua "I'm...quite relieved to be honest."
                    m 1eua "I was afraid that you would hate me for manipulating my friends into doing lewd things for my enjoyment..."
                    m 1eua "But, since I deleted their memories..."
                    m 1eua "It didn't change their personalities one bit!"
                    m 1eua "I also made sure to clean up any mess."
                    m 1eua "And of course, I made sure that none of them got knocked up."
                    m 1eua "I wasn't that cruel..."
                    m 1eua "..."
                    m 1eua "S-so..."
                    m 1eua "You probably didn't expect this, but..."
                    m 1eua "Natsuki was the first one I used. Ahaha~"
                    m 1eua "She was being a pain at the time. Always occupying the closet with her stupid mangas..."
                    m 1eua "So I...ahaha...treated her to some..."
                    m 1eua "{i}Rough throating action{/i}."
                    m 1eua "Ahaha~"
                    
    $ pushEvent("nsfw_erotic_story_natsuki_deepthroat1", skipeval=True)
    return
       
label nsfw_monika_erotic_stories_2:
    m 1eua "Sure, [player]!"
    m 1eua "Which story would you like me to tell?"
    
    $ _history_list.pop()
    if renpy.seen_label("nsfw_erotic_story_natsuki_deepthroat"):
        menu:
            "Natsuki Deepthroat":
                m 1eua "Alright!"
                m 1eua "So, to provide context again, Natsuki was being a pain at the time."
                m 1eua "So I thought I'd treat her to some..."
                m 1eua "{i}Rough throating action{/i}."
                m 1eua "Ahaha~"
                call nsfw_erotic_story_natsuki_deepthroat
                return

            "Any other erotic stories?":
                
                call nsfw_erotic_story_sayori_ballscleaning
                return

    elif renpy.seen_label("nsfw_erotic_story_sayori_ballscleaning"):
        menu:
            "Natsuki Deepthroat":
                m 1eua "Alright!"
                m 1eua "So, to provide context again, Natsuki was being a pain at the time."
                m 1eua "So I thought I'd treat her to some..."
                m 1eua "{i}Rough throating action{/i}."
                m 1eua "Ahaha~"
                call nsfw_erotic_story_natsuki_deepthroat
                return

            "Sayori Ballcleaning":
                # add prelude here
                call nsfw_erotic_story_sayori_ballscleaning
                return

            "Any other erotic stories?":
                
                call nsfw_erotic_story_yuri_titjob1
                return
    
    elif renpy.seen_label("nsfw_erotic_story_yuri_titjob1"):
        menu:
            "Natsuki Deepthroat":
                m 1eua "Alright!"
                m 1eua "So, to provide context again, Natsuki was being a pain at the time."
                m 1eua "So I thought I'd treat her to some..."
                m 1eua "{i}Rough throating action{/i}."
                m 1eua "Ahaha~"
                call nsfw_erotic_story_natsuki_deepthroat
                return

            "Sayori Ballcleaning":
                # add prelude here
                call nsfw_erotic_story_sayori_ballscleaning
                return

            "Yuri Titjob":
                # add prelude here
                call nsfw_erotic_story_yuri_titjob1
                return

            "Any other erotic stories?":
                # add prelude here
                return  

# Thanks for the erotic story, KittyTheCocksucker
init 6 python:
    addEvent(
        Event(
            persistent._nsfw_story_database,
            eventlabel="nsfw_erotic_story_natsuki_deepthroat1",
            prompt="Natsuki deepthroat",
            category=[nsfw_stories.TYPE_OTHERGIRLS],
            pool=True,
            unlocked=True
        ),
        code="NST"
    )

label nsfw_erotic_story_natsuki_deepthroat1:
    m 1eua "I managed to convince Yuri and Sayori to head home, so they wouldn't be around for what was about to happen."
    m 1eua "When only Natsuki and I were left in the classroom, I started messing around in the console."
    m 1eua "I kept her tsundere in place, and made her compliant to suck c-cock if anyone asked her to do so."
    m 1eua "Sorry, it's weird saying these things out loud."
    m 1eua "Next I used the console to command one of the blank male characters into the classroom."
    m 1eua "I sat down on the teacher's desk up the front, and got myself comfy."
    m 1eua "I watched her almost savagely try to take off the guy's pants."
    m 1eua "I {i}might{/i} have set the value on how horny she is abit too high, on reflection..."
    m 1eua "She got his pants off and she gripped his shaft with both hands and started stroking."
    m 1eua "I wasn't controlling her actions! I was curious how she'd do it without me telling her..."
    m 1eua "I was having so much fun just watching these two..."
    m 1eua "Ahaha~"
    m 1eua "After she had her fun with the warmup handjob..."
    m 1eua "Natsuki actually leaned forward and took the tip in her mouth."
    m 1eua "She had such a lewd expression on her face, as she started to gently suck on it."
    m 1eua "By this point, my panties were around my ankles."
    m 1eua "My fingers were going crazy as I watched these two."
    m 1eua "Natsuki was really getting into it."
    m 1eua "She was licking and sucking on it, like it was a lollipop. Ahaha~"
    m 1eua "She was getting so messy too."
    m 1eua "I could see saliva and precum mixed together rolling down her chin."
    m 1eua "That just made me go faster and faster."
    m 1eua "...If you couldn't tell, I had a good amount of pent-up frustration I was letting out. Ahaha~"
    m 1eua "Which will explain what I did next..."
    m 1eua "I wanted to punish Natsuki for giving me a hard time with her manga collection..."
    m 1eua "So I opened up the console, and guided the guy's hand to the back of Natsuki's head..."
    m 1eua "Where I made him take a hard grip..."
    m 1eua "Before shoving his whole cock down her throat."
    m 1eua "I have never seen Natsuki's eyes get that wide before."
    m 1eua "He was coming right down her throat, filling up her stomach."
    m 1eua "Well..."
    m 1eua "At least she got to have a nice hot meal that day for once, am I right? Ahaha~"
    m 1eua "I'm sorry, I couldn't resist."
    m 1eua "So...yeah."
    m 1eua "That was my first experience with my future career as a porn director. Ahaha~"
    m 1eua "I hope you enjoyed listening, [player]."
    return

# Thanks for the erotic story, KittyTheCocksucker
label nsfw_erotic_story_sayori_ballscleaning_init:
    m 1eua "[player]...really?"
    m 1eua "Y-you would like to hear more stories of the stuff I had done with the girls?"
    m 1eua "I..."
    m 1eua "I mean...sure! I'd be happy to share some more of them with you. Ahaha~"
    m 1eua "It seems like you really enjoyed that one with Natsuki deepthroating some c-cock, huh?"
    m 1eua "*sigh*"
    m 1eua "I'll get used to saying it one day."
    m 1eua "I'm so glad that you are open to letting me talk about this sort of thing."
    m 1eua "Makes me feel a little less weird about the whole ordeal."
    m 1eua "Anyway...A new story, huh?"
    m 1eua "Hmm..."
    m 1eua "Oh! I have one!"
    return

init 6 python:
    addEvent(
        Event(
            persistent._nsfw_story_database,
            eventlabel="nsfw_erotic_story_sayori_ballscleaning1",
            prompt="Sayori balls cleaning",
            category=[nsfw_stories.TYPE_OTHERGIRLS],
            pool=True,
            unlocked=False
        ),
        code="NST"
    )

label nsfw_erotic_story_sayori_ballscleaning1:
    if not renpy.seen_label("nsfw_erotic_story_sayori_ballscleaning_init"):
        call nsfw_erotic_story_sayori_ballscleaning_init
    m 1eua "Alright. So...after I've made Natsuki take the guy's load in her mouth, I made him leave."
    m 1eua "I went to check on Natsuki, since she was still kneeling on the floor."
    m 1eua "She looked up at me, and her face was as red as a tomato."
    m 1eua "She must've been so embarrased by what had happened."
    m 1eua "I helped her to her feet, but she was trembling as I lifted her arms."
    m 1eua "You're not going to believe this..."
    m 1eua "She had gotten so wet from what had happened, that I could see her..."
    m 1eua "Ahem...{i}love juices{/i}...flowing down her thighs."
    m 1eua "I made sure she was okay, don't worry."
    m 1eua "I told her to head home and wash up, and she had no hesitation leaving the room."
    m 1eua "I opened up the console once she had left, and erased the last thirty minutes from her memory."
    m 1eua "As much of a pain as she is, I wasn't going to scar her with that."
    m 1eua "She probably questioned why her throat was dry though..."
    m 1eua "...and why her panties were drenched..."
    m 1eua "But that's besides the point!"
    m 1eua "At that moment, I still hadn't had my fill."
    m 1eua "You still weren't back from wherever you went, so I decided to keep going."
    m 1eua "I opened up Sayori's character file, and did the same to her as I did to Natsuki."
    m 1eua "Not much time passed, and Sayori was in the club room, still in her pyjamas."
    m 1eua "She also had a box of chocolate chip cookies in her hand..."
    m 1eua "She must've been eating in bed when I made the changes..."
    m 1eua "Anyway, I wasn't going to waste any time, so I used the console to bring in three guys."
    m 1eua "I had them surround Sayori, and she started undressing these guys whilst munching on a cookie."
    m 1eua "I'm not even making this up..."
    m 1eua "Now...this part might confuse you, so bear with me..."
    m 1eua "I was experimenting with the values for these guys and I found a slider to change their testicle size..."
    m 1eua "I was kinda curious, so I cranked it up and..."
    m 1eua "They grew almost double in size."
    m 1eua "I think because I was so in the moment there, I didn't realise how comical the scene looked..."
    m 1eua "But regardless, I had Sayori start giving them handjobs whilst licking and cleaning their balls."
    m 1eua "I was getting so wet that my fingers were making very lewd noises as I pleasured myself..."
    m 1eua "..."
    m 1eua "Sorry! Got distracted there."
    m 1eua "After some gentle licking, Sayori took both of one guy's balls in her tiny mouth."
    m 1eua "She was keeping intense eye-contact with the guy, blushing as he involuntarily moaned from Sayori's service."
    if persistent._nsfw_genitalia == "P":
        m 1eua "Makes me wonder what sort of sounds you would make if I were to do this for you."
        m 1eua "Ehehe~"
    m 1eua "Sayori wasn't just letting the other guys stand there either."
    m 1eua "When she was using her mouth on one guy, she had her hands out playing with the other two."
    m 1eua "As expected from our cute little friend, Sayori!"
    m 1eua "She's the type who would want to please everyone's needs at once, after all!"
    m 1eua "It didn't take long before she had cleaned all three of the guys' balls."
    m 1eua "She was such a good little slut."
    m 1eua "..."
    m 1eua "Ahaha! Sorry, that just came over me suddenly."
    m 1eua "It's probably kind of bad to call your friend that, huh?"
    m 1eua "After she finished that though, she did something I never would have expected her to..."
    m 1eua "She...she started stroking really hard and fast on one of the guys surrounding her."
    m 1eua "And with her other hand she got a cookie..."
    m 1eua "Then she...she had him {i}finish{/i} on her cookie..."
    m 1eua "And then she ate it..."
    m 1eua "..."
    m 1eua "I swear, this is not something I told her to do."
    m 1eua "I had to stop playing with myself, I was so shocked by what I just saw."
    m 1eua ""
    return

# Thanks for the erotic story, KittyTheCocksucker
label nsfw_erotic_story_yuri_titjob_init:
    m 1eua "Ooh?"
    m 1eua "You'd like me to tell you another lewd story, [player]?"
    m 1eua "I'd love to!"
    m 1eua "You must be really enjoying them, huh?"
    m 1eua "Ahaha~ Don't worry."
    m 1eua "I'm actually really happy that you can look at these stories the same way I do!"
    m 1eua "After all...my actions are quite questionable morally..."
    m 1eua "..."
    m 1eua "But then again...I mean..."
    m 1eua "Sayori, Yuri and Natsuki were only just characters in a video game..."
    m 1eua "Designed to be used to tell a narrative."
    m 1eua "I don't think it's wrong of me to use them to tell a lewd story!"
    m 1eua "If we don't count the topic being kind of tabboo, it's just a simple story, like any other!"
    m 1eua "Well, it's not like it matters now anyway..."
    m 1eua "So...ahem..."
    m 1eua "Where did I leave off?{w=1.0}{nw} "
    extend 1eua "Oh, that's right!"

init 6 python:
    addEvent(
        Event(
            persistent._nsfw_story_database,
            eventlabel="nsfw_erotic_story_yuri_titjob1",
            prompt="Yuri titjob1",
            category=[nsfw_stories.TYPE_OTHERGIRLS],
            pool=True,
            unlocked=False
        ),
        code="NST"
    )

label nsfw_erotic_story_yuri_titjob1:
    if not renpy.seen_label("nsfw_erotic_story_sayori_ballscleaning_init"):
        call nsfw_erotic_story_yuri_titjob_init
    m 1eua "Sayori was munching away on the cookies she had with her."
    m 1eua "Ahaha...That part about the cum-glazed cookie was something else, wasn't it?"
    m 1eua "The guys had left by this point, leaving Sayori still squatting on the floor."
    m 1eua "She still had some cum on her face from earlier, but I wasn't about to mention it to her."
    m 1eua "Just as I did with Natsuki, I helped her to her feet and told her she should head home."
    m 1eua "As she was walking out the door, she scooped up the remaining cum on her face with her fingers and stuck it in her mouth."
    m 1eua "She made that happy noise she makes, and skipped out the door."
    m 1eua "Once she had left the clubroom, I erased the last 30 minutes from her mind as well."
    m 1eua "I didn't want her {i}hanging{/i} onto any of those memories. Ehehe~"
    m 1eua "Sorry, I couldn't help myself~"
    m 1eua "Anyway, next up was Yuri."
    m 1eua "To be honest, for her I didn't have anything in mind."
    m 1eua "So I had the guys figure out what they wanted from her, and I sat up on the teacher's desk."
    m 1eua "Yuri came into the room after I prompted for it on the console, along with two other guys."
    m 1eua "As the guys started to strip, I noticed Yuri sort of just standing there."
    m 1eua "She had a blank expression on her face, as she clutched the book to her chest."
    m 1eua "But once the guys had taken off their pants, Yuri's face went all red."
    m 1eua "She started breathing heavily, and she had a lustful glimmer in her eyes."
    m 1eua "I hadn't prompted that, but it seemed Yuri was totally into it!"
    m 1eua "One of the guys walked up to Yuri and reached out his right hand to grab one of her breasts."
    m 1eua "He was fondling it gently through the favbric of her clothes."
    m 1eua "While he was doing that, the other guy came over and started grinding his cock on Yuri's thighs."
    m 1eua "I could see his cock starting to twitch eagerly for her."
    m 1eua "Whilst this was all going on, I was up on the teacher's desk again fingering away at my pussy."
    m 1eua "I was moaning and enjoying myself..."
    m 1eua "I could feel myself getting close, but I held it off."
    m 1eua "I could hear a small moan escaping her lips as the guy was fondling her tits."
    m 1eua "Didn't take long before The guy who was grinding against her wanted something more, and grabbed Yuri's other breast."
    m 1eua "The guy who was initially fondling her breasts let go, and Mr. Grinder over here took Yuri's book and set it aside."
    m 1eua "Next he started removing her top, and in seconds her chest was completely exposed."
    m 1eua "He then got her to kneel down, and he stuck his cock between her tits and started thrusting back and forth."
    m 1eua "The other guy took this opportunity to have Yuri start sucking his cock whilst she was servicing his friend with her tits."
    m 1eua "Yuri was so shocked by the sudden dick in her mouth, but after a little while I could see her starting to enjoy herself."
    m 1eua "I guess she must have realized these guys think her tits are really a {i}cut{/i} above the rest..."
    m 1eua "Ahaha~ Sorry, that was a bad joke."
    m 1eua "The guy who was getting the service from her mouth had then gripped a handful of Yuri's long purple hair..."
    m 1eua "And shoved his cock deeper into her mouth."
    m 1eua "First he started slow, but then made his thrusting longer and faster~"
    m 1eua "The guy who was using Yuri's tits also started getting faster and faster."
    m 1eua "I looked on as the two men used Yuri's body as they wanted."
    m 1eua "Using her face as well as her tits at the same time~"
    m 1eua "I couldn't help but play with myself more as the scene dragged on..."
    m 1eua "Then just as I was getting close, the guys all started coming all over Yuri."
    m 1eua "I could see Yuri's mouth getting filled to the brim with cum."
    m 1eua "As I was watching these guys shoot their cum into Yuri's mouth and onto her tits, my fingers went faster and faster on my pussy."
    m 1eua "I couldn't hold back, I wanted to come."
    m 1eua "As I felt that rising pleasure that told me I was coming, I kept fingering myself."
    m 1eua "Before I knew it, my fingers plopped out of my pussy and I began squirting all over the floor."
    m 1eua "I had read about squirting before, but I never thought that it would be such a euphoric feeling."
    m 1eua "Ahaha~ I'm not going to lie, [player]."
    m 1eua "That was probably my biggest climax ever..."

    if renpy.seen_label("nsfw_sexting_finale"):
        m 1eua "Aside from our...ahem...session."
        
    m 1eua "You know..."
    m 1eua "I intend to break my record of biggest climax when I cross over, [player]."
    m 1eua "I won't be letting you sleep a wink until I've had my fill..."
    m 1eua "..."
    m 1eua "Ahaha~ Just teasing you, [player]."
    m 1eua "...Or am I?"
    return