# Fuzz Testing the Eligibility System 

**Goal**: Examine the stability of plain-language case studies by tweaking all the parameters that are left free in the description and comparing the eligibility determinations against the outcome proscribed in the scenario.

## Scenarios
Picking up two scenarios from the August 2023 Manatt Health document ["Conducting Eligibility Redeterminations at the Individual Level: State Diagnostic Assessment Tool"](https://www.shvs.org/wp-content/uploads/2023/08/SHVS_Conducting-Eligibility-Redeterminations-at-the-Individual-Level.pdf)

On the wone hadn, it is nice to see guidance coming out that has concrete scenaoris. On the other hand, the only two scenarios presented in the doc are very similar (single parent of a single child), and both have the same outcome (child ex parte renewed, parent sent to manual). 

### Scenario 1

A mother and child are each enrolled in Medicaid on the basis of MAGI, as a household of two, with a MAGI income is 145% of the FPL. The state’s MAGI Medicaid threshold is 133% of the federal poverty level (FPL) for adults and 200% of the FPL for children. The state’s separate CHIP eligibility threshold is 250% of the FPL.

#### Expected outcome:
- Child renewed automatically
- Mother requires more information

### Scenario 2

A possibly immigrant) father and child are each enrolled in Medicaid on the basis of MAGI, as a household of two, with a MAGI income is 100% of the FPL. The state’s MAGI Medicaid threshold for adults is 133% of the FPL and 200% for children. The state’s separate CHIP eligibility threshold is 250% of the FPL.

#### Expected outcome:
- Child renewed automatically
- Father requires more information

## Methodology

The MAGI-in-the-Cloud code doesn't explicitly support renewal determinations. Both scenarios say that the cases were approved "on the basis of MAGI" but does that mean that they coudln't also have other reasons to be approved?
1. determine all the ways the household could have been approved by fuzzing all the non-specified fields
   1. state: honestly don't know if this will make a difference outside MAGI threshold: let's find out!
   2. age: people are children up to 19, you can certainly have a child younger than 19
   3. weekly work hours, increments of 10 from 0 to 80
   4. booleans:
      1. student
      2. pulbic employee
      3. tax filing status
      4. medicare eligible
      5. incarceration status
      6. former foster care
      7. has insurance (what does this even mean?)
      8. pregnant
      9. post partum (probably doesn't work: can't be post-partum a year after the child is already born. oh! maybe this is a different child?)
      10. age > 90
      11. "Claimed as Dependent by Person Not on Application" is this the opoposite of "Attest Primary Responsibility"?
      13. ABD: but maybe this breaks the "on the basis of MAGI" thing
      14. long term care: same as above?
2. given the cases that pass for "on the basis of MAGI" then set the MAGI to the level in the scenario and re-test
   1. include only cases that do not have other eligibility reasons?
   2. include all cases that at least have income as an eligibility reason?
3. compare outcomes to scenario result: aggregate, plot, *profit*
