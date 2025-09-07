Potential Issues - 


1. Noise impacting speech recognition (Solved) - Instead of complete automation, having a human scorekeeper with noise
   cancelling headphones, provides basis for the rest of the issues.

1a. Broadcasting environment - Some stadiums may not have an environment where the entire game can can be captured, and 
    quiet enough for one human to correctly keep score. 

2. Variability in scorekeeping language - The knowledge base and or dataset used in the RAG pipelines needs to account for 
   separate versions of the same event being equivalent unless:

2a. Having each scorekeeper learn the "language" of our AI is a possible solution, however, quick turnaround times for some 
    scorekeepers may exemplify the most dangerous error - having to reconsile and edit any data that was already stored.

3. Order of information given / Potential errors made by human scorekeeper - Eg, saying strike two rather than strike one,
   AI needs to be able to to undo and fix its own records, in this situation - ("Error on previous, strike one, not strike two.)

4. Simultaneous events - In scenerios where multiple things happen at once, a runner stealing a base while batter swings,
   if human scorekeeper misses or doesnt report part of the play, the data will not be stored properly leading to incorrect scoring, and possible hallucinations throughout the rest of the game. 

5. Changes post ruling - If a play is scored and stored, going back and changing the score will be difficult, this  
   proved to be difficult in issue two, three, and four as well, and because one wrong score could break the scoring of the entire game, a system that allows for constant reconciliation and updates is extremely necessary.

Possible Edge Cases: 

- May need additional training on games that have extra innings (different rules in such games?)

- Atlantic league is a partner of the MLB, and rule changes are done quite often. AI needs to account for these changes
  and again, be able to reconcile and update properly. (Will only be necessary if rules change scorekeeping)

- Players going in and out of the Atlantic League, will *individual* stats be stored in data alongside scorekeeping? If not, can be stored in multiple different ways, such as team, number, position.   

SM: 

The main issues that consistenly pop up are ambiguity, changes within the Atlantic League, and reconciliation and updating. 


