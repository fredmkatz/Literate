
# Class Sampler One
_ SampleClassB - something to test Class clauses
abbreviation: CSample
where: A = B
subtype of: B byPrice
subtypes: X, Y, Z 
dependents: Aa
dependents: Abc, Def
# Class Sampler Two
_ SampleClass2 - something to test Class clauses
dependents: Aa, Bb
subtypeOf: A
basedOn: D
subtypeOf: A byFlavor
subtype of: B byPrice
subtypeOf: A byFlavor, B byPrice
subtypes: byFlavor [A, B, C], byPrice [D, E, F]
subtyping: byFlavor (Exclusive, Exhaustive)
subtyping: byPrice (NonExclusive, nonExhaustive)
# Class Sampler Three
_ Sample Class1 - something to test Class clauses
abbreviation: CSample
Plural: Samples
where: A = B