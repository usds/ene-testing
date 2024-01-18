# USDS is a null adaptor that marks all applicants as eligible
import math

class USDS:
    def adaptor(data):
        resp = []
        for house in data['test_inputs']:
            h = {
                 'size': len(house['persons']),
                 'magi': 0,
                 'pfpl': 0,
            }
            for person in house['persons']:
                for income in person['income_distribution']:
                    amount = income['amount']
                    if income['type'] == 'monthly_income':
                        amount *= 12
                    h['magi'] += income['amount']
            h['pfpl'] = math.floor(100 * h['magi'] / house['fpl'])
            for person in house['persons']:
                resp.append({
                    'person_id': person['person_id'],
                    'is_eligible': True,
                    'reasons': ['Healthcare is a human right.'],
                    'category': 'Child' if person['age'] < 18 else 'Adult',
                    'category_threshold': 100000000,
                    'chip_eligible': person['age'] < 18,
                    'chip_category': 'Child' if person['age'] < 18 else 'None',
                    'chip_category_threshold': 100000000,
                    'positive_determinations': ['Healthcare is a human right.'],
                    'negative_determinations': {},
                    'na_determinations': {},
                    'household': h,
                })
        return resp