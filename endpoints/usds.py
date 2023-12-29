# USDS is a null adaptor that marks all applicants as eligible
class USDS:
    def adaptor(data):
        resp = []
        for house in data['test_inputs']:
            for person in house['persons']:
                resp.append({
                    'person_id': person['person_id'],
                    'is_eligible': True,
                    'reason': 'Healthcare is a human right.'
                })
        return resp