# Ultimate_Texas_Holdem
Development plan (Phase 1):
- pogoj da se gleda 5 kart (kickerji, barve itd.)
- blind + trips
- comment, comment, comment
- Decisions when to bet (combinations should be considerd for startres only for combinations between hand and flop/river)

Early strategy development (Phase 2):
- Testiranje osnovnih strategij


Strategy development (Phase 3):
- Machine learning (3 stages)
    - later stage gives expected value to check of the previous stage
    - "reverse learning" with koeficient k - one situation in first stage, k
    situations in second stage and k^2 situations in third stage

- Neural network:
    - Igralec ima 4 možnosti (preflop, flop, river, fold)
    - Če izgubi, v tisto smer mali popravek (dou je river -> izgubi -> fold), (dou je river -> zmaga -> flop)

