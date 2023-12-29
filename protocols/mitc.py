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
        usds = mitc
        usds

def mitc_bool(tf):
    return 'Y' if tf else 'N'

def produce_person(usds):
    mitc = {}
    mitc['Applicant Age'] = usds['age']
    mitc['Applicant Age >= 90'] = mitc_bool(usds['age'] > 90)
    mitc['Applicant Attest Blind or Disabled'] = mitc_bool(usds['has_abd_status'])
    mitc['Applicant Attest Long Term Care'] = mitc_bool(usds['long_term_care'])
    mitc['Applicant Post Partum Period Indicator'] = mitc_bool(usds['is_post_partum'])
    mitc['Applicant Pregnant Indicator'] = mitc_bool(usds['is_pregnant'])
    mitc['Claimed as Dependent by Person Not on Application'] = mitc_bool(usds['claimed_dependent'])
    mitc['Former Foster Care'] = mitc_bool(usds['former_foster_care'])
    mitc['Has Insurance'] = mitc_bool(usds['has_insurance'])
    mitc['Hours Worked Per Week'] = usds['weekly_work_hours']
    mitc['Incarceration Status'] = mitc_bool(usds['is_incarcerated'])
    mitc['Income'] = produce_income(usds['income_distribution'])
    mitc['Is Applicant'] = mitc_bool(usds['is_applicant'])
    mitc['Lives In State'] = mitc_bool(usds['lives_in_state'])
    mitc['Medicare Entitlement Indicator'] = mitc_bool(usds['is_medicare_eligible'])
    mitc['Person ID'] = usds['person_id']
    mitc['Prior Insurance'] = mitc_bool(usds['prior_insurance'])
    mitc['Relationships'] = produce_relations(usds['relationships'])
    mitc['Required to File Taxes'] = mitc_bool(usds['must_file_taxes'])
    mitc['State Health Benefits Through Public Employee'] = mitc_bool(usds['state_health_benefits'])
    mitc['Student Indicator'] = mitc_bool(usds['is_student'])
    mitc[ 'US Citizen Indicator'] = mitc_bool(usds['is_citizen'])
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
                'Attest Primary Responsibility': mitc_bool(link['attests_responsibility']),
                'Other ID': link['person_id'],
                'Relationship Code': link['relationship_code'],
            }
        )
    return mitc