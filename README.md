fec-standardizer
================

An experiment to standardize individual donor names in federal campaign finance data using simple graph theory and machine learning.

## Why?

Most campaign finance analyses in journalism and elsewhere view data at the contribution level, mostly because that's how the data comes out of the box. However, I think there are a lot of new and interesting things we can learn if we start looking at data at the level of individual donors. When does a donor make an unusual contribution? When and why does a donor switch candidates or parties? Which donors act in concert? Might they be doing so illegally? There are a ton of interesting questions to ask, but first we've got to deal with the data.

Almost no campaign contribution data provides standardized, canonical donor IDs. Which is to say there's no explicit marker showing that the "Bob Perry" who gave $1,000 to a Democratic Senate candidate is the same "Bob Perry" who gave to Mitt Romney's presidential run. That said, it's often pretty easy to tell whether two contributions come from the same person. If they share a first, middle and last name; they live in the same ZIP code; and they list the same occupation and employer (all required fields in campaign disclosure data) you can be pretty sure they're the same person.

The Center for Responsive Politics has for years combined automated analysis with human research to attempt to disambiguate the data using these attributes. And they've done a great job. Only problem is, their approach doesn't generalize well to local and sometimes state data. There's only one CRP, after all, and they only have so much time to process data. It stands to reason that they'd focus on federal first.

The purpose of this experiment is to see how well automated techniques can model the intuition of CRP's process, with the hope of creating a workflow that can be quickly adapted to standardize any campaign finance dataset -- local, state or federal.
