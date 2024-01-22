# MITC format is the JSON used by https://github.com/HHSIDEAlab/medicaid_eligibility

class MITC:
    def produce(usds):
        mitc = {'Name': 'Frontend Application'}
        # WARNING: MITC requires all households to be in the same state
        mitc['State'] = usds['test_inputs'][0]['locality']
        # WARNING: MITC assumes applications happen in the same year
        mitc['Application Year'] = usds['test_inputs'][0]['application_year']
        # TODO: Tax Returns
        mitc['Tax Returns'] = [
            {
                'Dependents': [],
                'Filers': [],
            },
        ]

        # MITC puts all people in one array, with a sibling household object
        mitc['Physical Households'] = []
        mitc['People'] = []
        for usds_house in usds['test_inputs']:
            mitc_house = {
                'Household ID': usds_house['household_id'],
                'People': [],
            }
            for usds_person in usds_house['persons']:
                # WARNING: MITC has unique person IDs across households: remap?
                mitc_house['People'].append({'Person ID': usds_person['person_id']})
                mitc['People'].append(produce_person(usds_person))

            mitc['Physical Households'].append(mitc_house)
        return mitc
        
    def consume(mitc):
        usds = []
        for person in mitc['Applicants']:
            p = {
                'person_id': person['Person ID'],
                'household': {
                    'size': len(person['Medicaid Household']['People']),
                    'magi': person['Medicaid Household']["MAGI"],
                    'pfpl': person['Medicaid Household']["MAGI as Percentage of FPL"],
                },
                'is_eligible': is_eligibile(person),
                'category': person["Category"],
                'category_threshold': person["Category Threshold"],
                'medicaid_eligible': mitc2bool(person["Medicaid Eligible"]),
                'ineligibility_reasons': person["Ineligibility Reason"]
                    if "Ineligibility Reason" in person else None,
                'chip_eligible': mitc2bool(person["CHIP Eligible"]),
                'chip_category': person["CHIP Category"],
                'chip_category_threshold': person["CHIP Category Threshold"],
                'chip_ineligibility_reasons': person["CHIP Ineligibility Reason"] 
                    if "CHIP Ineligibility Reason" in person else None,
                'positive_determinations': [
                    name for (name, d) in person["Determinations"].items()
                    if d["Indicator"] == 'Y'
                ],
                'negative_determinations': {
                    name: d["Ineligibility Reason"] for (name, d) in person["Determinations"].items()
                    if d["Indicator"] == 'N'
                },
                'na_determinations': [
                    name for (name, d) in person["Determinations"].items()
                    if d["Indicator"] == 'X'
                ],
            }
            if p['is_eligible']:
                p['reasons'] = p['positive_determinations']
            else:
                p['reasons'] = p['negative_determinations'].keys()
            usds.append(p)
        return usds

def is_eligibile(person):
    return (
        mitc2bool(person['Medicaid Eligible']) or
        mitc2bool(person['CHIP Eligible'])
    )
    
def mitc2bool(yn):
    return yn == 'Y'

def bool2mitc(tf):
    return 'Y' if tf else 'N'

def produce_person(usds):
    mitc = {}
    mitc['Applicant Age'] = usds['age']
    mitc['Applicant Age >= 90'] = bool2mitc(usds['age'] > 90)
    mitc['Applicant Attest Blind or Disabled'] = bool2mitc(usds['has_abd_status'])
    mitc['Applicant Attest Long Term Care'] = bool2mitc(usds['long_term_care'])
    mitc['Applicant Post Partum Period Indicator'] = bool2mitc(usds['is_post_partum'])
    mitc['Applicant Pregnant Indicator'] = bool2mitc(usds['is_pregnant'])
    mitc['Claimed as Dependent by Person Not on Application'] = bool2mitc(usds['claimed_dependent'])
    mitc['Former Foster Care'] = bool2mitc(usds['former_foster_care'])
    mitc['Has Insurance'] = bool2mitc(usds['has_insurance'])
    mitc['Hours Worked Per Week'] = usds['weekly_work_hours']
    mitc['Incarceration Status'] = bool2mitc(usds['is_incarcerated'])
    mitc['Income'] = produce_income(usds['income_distribution'])
    mitc['Is Applicant'] = bool2mitc(usds['is_applicant'])
    mitc['Lives In State'] = bool2mitc(usds['lives_in_state'])
    mitc['Medicare Entitlement Indicator'] = bool2mitc(usds['is_medicare_eligible'])
    mitc['Person ID'] = usds['person_id']
    mitc['Prior Insurance'] = bool2mitc(usds['prior_insurance'])
    mitc['Relationships'] = produce_relations(usds['relationships'])
    mitc['Required to File Taxes'] = bool2mitc(usds['must_file_taxes'])
    mitc['State Health Benefits Through Public Employee'] = bool2mitc(usds['state_health_benefits'])
    mitc['Student Indicator'] = bool2mitc(usds['is_student'])
    mitc[ 'US Citizen Indicator'] = bool2mitc(usds['is_citizen'])
    return mitc

IMCOME_TYPES = {
    'alimony': 'Alimony',
    'capital_gain_or_loss': 'Capital Gain or Loss',
    'farm_income_or_loss': 'Farm Income or Loss',
    'magi_deductions': 'MAGI Deductions',
    'monthly_income': 'Monthly Income',
    'other_income': 'Other Income',
    'pensions_annuities': 'Pensions and Annuities Taxable Amount',
    'tax_exempt_interest': 'Tax-Exempt Interest',
    'taxable_interest': 'Taxable Interest',
    'tax_refunds_credits_offsets': 'Taxable Refunds, Credits, or Offsets of State and Local Income Taxes',
    'unemployment_compensation': 'Unemployment Compensation',
    'wages_salary_tips': 'Wages, Salaries, Tips',
}

def produce_income(usds):
    mitc = {}
    for source in usds:
        mitc[IMCOME_TYPES[source['type']]] = source['amount']
    return mitc

def produce_relations(usds):
    mitc = []
    for link in usds:
        mitc.append(
            {
                'Attest Primary Responsibility': bool2mitc(link['attests_responsibility']),
                'Other ID': link['person_id'],
                'Relationship Code': link['relationship_code'],
            }
        )
    return mitc