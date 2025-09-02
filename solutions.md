Instead of having one human inputting the play and AI storing the data, another possible
way to "store data" is the use of a second human.

This will allow us to have a perfect use case for RAG, as the main issue - having to 
update and reconcile data after it was stored, can be eliminated.

The RAG outputs what happened and why, after the announcer input is translated and 
processsed to text.

Eg. 

Input from announcer- "Batter struckout swinging"

**RAG output** - "Batter #24 on Team Red struckout swinging. Score remains 2-3,No errors."

This format of RAG provides us with multiple different **solutions**:

1. The scorekeeper's vocabulary no longer has to be extremely specific. If the data that 
is being indexed involves the rules of baseball that change often in the Atlantic League, we can put less emphasis on AI storing the data and having to index based upon extremely specific vocabulary. Instead, we can use AI to "fill in the gaps" between the speech of the announcer and that of manual scorekeeping. 

1a. A separate human scorekeeper would be needed on the opposite side of the scorekeeper
in the rag.The flow chart would look something like this with a second human storing data:

Announcer input --> Indexing --> Rules retrieved --> **RAG OUTPUT** --> Data stored by human

2. One incorrect rule will not hinder the rest of the game - In my previous issues 
document, I highlighted a major concern in the opearating workflow, having to go back and 
update incorrect data. Having a second human scorekeeper is a fallback on this issue if itever occurs. 

3.The edge case of needing additional training is now gone, as the data that is being
indexed are mostly the rules of the game.

4.The edge case of players individual stats being stored is also gone, as the human 
scorekeeper at the end of the rag pipeline will be responsible for that. 

**Potential issues that this does not solve**

1. Simulataneous events 

2. Changes post ruling

**New issues that arise**:

1. Having to use another human in this process, when the original goal was to automate it as much as possible. 














