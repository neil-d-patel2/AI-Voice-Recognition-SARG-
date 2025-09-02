What is Retrieval Augmented Generation and why is it important for this project?

Retrieval Augmented Generation is extremely important, as the majority of date (>80%) of data is private

Also, LLMS are trained ONLY on large scale public data, so a more "internal" use case for llms rose

What we can do is feed private data (specifically "our" private data) to llms for processing and 


The flow of a RAG goes as follows:

Question (some sort of input) --> Indexing --> Retrievment --> Text generation  

"Documents are indexed such that they can be retrieved based upon some heuristics relative to an input like a question"

Those releevant docs can be passed to an llm and the llm can produce answers that are grounded in our "Private Data"

It essentially pairs the processing capacity of a huge llm with huge PRIVATE data stores rather than PUBLIC data stores


The First Aspect of Rag After The Initial Question is **Indexing**:

To go from question to text generation, we need to find the relevant documents in our data
stores to actually provide to our llm. 

We do this by numerical representation, which compresses text documents into numbers so
they can be searched.

ML Embedding Methods: 

Embedding models turn raw data into vectors, which in simple terms, makes finding relavantinformation to the question much easiser.

This makes **Retrieval** so feasible in RAG, and this is how it works.

Because all of our data is now stored numerically, all the numerical data represents some semantic meaning. 

Our question is matched to this relevant data after being indexed, and that data is now in our hands, and text is ready to be generated. 














