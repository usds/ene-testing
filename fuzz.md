# Fuzz Testing the Eligibility System 

**Goal**: Examine the stability of plain-language case studies by tweaking all the parameters that are left free in the description and comparing the eligibility determinations against the outcome proscribed in the scenario.

## Scenarios
Picking up two scenarios from the August 2023 Manatt Health document ["Conducting Eligibility Redeterminations at the Individual Level: State Diagnostic Assessment Tool"](https://www.shvs.org/wp-content/uploads/2023/08/SHVS_Conducting-Eligibility-Redeterminations-at-the-Individual-Level.pdf)

On the one hand, it is nice to see guidance coming out that has concrete scenarios. On the other hand, the only two scenarios presented in that doc are very similar (single parent of a single child), and both have the same outcome (child ex parte renewed, parent sent to manual).

### Scenario 1

A mother and child are each enrolled in Medicaid on the basis of MAGI, as a household of two, with a MAGI income is 145% of the FPL. The state’s MAGI Medicaid threshold is 133% of the federal poverty level (FPL) for adults and 200% of the FPL for children. The state’s separate CHIP eligibility threshold is 250% of the FPL.

#### Expected outcome:
- Child renewed automatically
- Mother sent for manual renewal

### Scenario 2

An immigrant father and child are each enrolled in Medicaid on the basis of MAGI, as a household of two, with a MAGI income is 100% of the FPL. The state’s MAGI Medicaid threshold for adults is 133% of the FPL and 200% for children. The state’s separate CHIP eligibility threshold is 250% of the FPL.

#### Expected outcome:
- Child renewed automatically
- Father sent for manual renewal

## Methodology

The MAGI-in-the-Cloud code doesn't explicitly support renewal determinations. Both scenarios say that the cases were approved "on the basis of MAGI" but does that mean that they couldn't also have other reasons to be approved?
1. determine all the ways the household could have been approved by fuzzing all the non-specified fields
   1. state: honestly don't know if this will make a difference outside MAGI threshold: let's find out!
   2. age: both scenarios indicate that the parent is an adult
   3. weekly work hours, increments of 20 from 0 to 60
   4. booleans:
      1. student
      2. public employee
      3. tax filing status
      4. medicare eligible
      5. incarceration status
      6. former foster care
      7. has insurance (what does this even mean?)
      8. pregnant
      9. post partum (maybe this is a different child from last year?)
      10. age > 90
      11. "Claimed as Dependent by Person Not on Application" is this the opposite of "Attest Primary Responsibility"?
      12. ABD: but maybe this breaks the "on the basis of MAGI" thing
      13. long term care: same as above?
      14. citizenship
      15. child previously in foster care
   5. this is *a lot* of possibilities, find a way to prune: implemented random sampling
2. given the cases that pass for "on the basis of MAGI" then set the MAGI to the level in the scenario and re-test
   1. include only cases that do not have other eligibility reasons?
   2. include all cases that at least have income as an eligibility reason?
3. compare outcomes to scenario result: aggregate, plot, *profit*

Execute a fuzz test:
```
./mitc/mitc.sh start
poetry run python ./fuzz.py -t fuzz_templates/00001.yml -n 1000
./mitc/mitc.sh stop
```

## Results

### Computational Performance

The python fuzzer implementation is able to evaluate 112 cases per second on a virtual machine where `lscpu` reports "Intel(R) Xeon(R) Gold 6348 CPU @ 2.60GHz" while making http requests to the ruby MITC E&E service running on the same machine in a container. The `top` command reported the MITC engine using 87% of the CPU while the fuzzer was using the other 13%. It's unclear why they were competing for one core: possibly the VM only had access to a single core despite `lscpu` reporting 24 cores being available.

112 cases per second translates to one million cases in 2.5 hours.

### Stability

Fuzzing every parameter that is not explicitly mentioned in the scenario quickly leads to hundreds of millions or even billions of possibilities. In this case, even random sampling doesn't work since the vast majority are not valid (meaning that the pre-condition does not even yield the result in the scenario). Since the child is eligible in both the pre- and post-condition of both scenarios, it was decided to hold the child's properties mostly static. This reduces the possibility space to only hundreds of thousands. With this narrower field, random sampling is informative even for runs small enough to complete in seconds: enabling iterative exploration.

#### Scenario 1

Holding the child description static, using NJ as a test state, the scenario admits 196,608 possible household situations. Performing 10,000 sample runs indicates that around 40% of those match the pre-condition, and only about 10% of those match the post-condition.

The parameters that cause a situation to be invalid are things like immigration status and access to other insurance programs.

Most of the correctness failures (the situation matches the pre-condition but does not match the post-condition) arise from the system marking the parent eligible, despite the scenario sending them for manual renewal. The main driver of these situations is the parent being either pregnant or post-partum.

Interestingly, `is_pregnant` and `is_post_partum` and both boolean values, which implies that the correctness rate should be 25% if those are the only factors involved. Indeed, if we fix them both to be `false` the rate of both valid and correct situations goes to 100%. The fact that we only see 10% correctness from valid situations when considering pregnancy implies that there is a second-order interaction between pregnancy and some other parameter, probably income, that is affecting the results.

#### Scenario 2

It was not possible to test scenario 2 because the MITC engine does not explicitly support renewals, only applications. As a result there is no way to indicate (as far as I know) that the father has an acceptable immigration status that is valid in the pre-condition. As a result, all possible household situations fail the citizenship test during validation phase, and are rejected.

Possible work-around would be to use the fuzzer's pre/post condition mechanism to also set the citizenship status to `true` during validation. I should also dive into the MITC code to see if there's a way to specify immigration status directly that I don't know about.

## Discussion

I was able to develop a deeper understanding of scenario 1 by turning parameter fuzzing on and off for various dimensions of the household descriptions. It was fairly easy to narrow scenario 1 to see the effect of pregnancy on the determinations. It is very easy to imagine a junior engineer at a vendor receiving the scenario as a requirement and writing code that ends up sending a lot of pregnant and post-partum beneficiaries, who should have been *ex parte* renewed, to manual renewal instead.

Scenario 1 was small enough that it was possible to run all the 196,000 situations in less than an hour. The results of that run were that 56% of the situations were valid, and of those, 5.5% had correct outcomes. These results seem close enough to the 40%/10% result from the small samples to give some confidence that sampling is a valid approach.

It would be interesting to try and automate my manual exploration to surface which parameters effect the outcomes. One could fuzz one parameter at a time, holding the others constant, however that might miss interactions between parameters. Also it's hard to know which option for a given parameter it is safe to use as the control. For example in Scenario 2 the parameter `is_citizen` is set to the constant constant `false` and that prevents the system from exploring the effect of the other parameters.
