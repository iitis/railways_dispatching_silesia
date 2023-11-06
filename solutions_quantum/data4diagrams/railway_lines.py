# source: https://www.atlaskolejowy.net/infra/?id=linia&poz=200
#    and links therein
#  station format:   {'name':'','callsign':'','type':'','km':},

import sys

RAILWAYLINES = {
    '131':({'name':'Chorzów Batory', 'callsign':'CB', 'type':'st', 'km':6.16},
         {'name':'Chorzów Miasto', 'callsign':'CM', 'type':'st', 'km':8.98}),
    '137':({'name':'Katowice', 'callsign':'KO', 'type':'st', 'km':0.39},
         {'name':'Katowice Towarowa KTC', 'callsign':'KTC', 'type':'podg', 'km':2.91},
         {'name':'Chorzów Batory', 'callsign':'CB', 'type':'st', 'km':6.16},
         {'name':'Świętochłowice', 'callsign':'', 'type':'po', 'km':8.41},
         {'name':'Ruda Chebzie', 'callsign':'RC', 'type':'st', 'km':11.74},
         {'name':'Ruda Śląska', 'callsign':'RŚl', 'type':'po', 'km':14.6},
         {'name':'Zabrze', 'callsign':'Zz', 'type':'st', 'km':18.92},
         {'name':'Gliwice', 'callsign':'Gl', 'type':'st', 'km':27.10}),
    '138':({'name':'Katowice Zawodzie', 'callsign':'Kz', 'type':'st', 'km':30.24},
         {'name':'Katowice', 'callsign':'KO', 'type':'st', 'km':32.96}),
    '139':({'name':'Katowice', 'callsign':'KO', 'type':'st', 'km':0.0},
         {'name':'Katowice Brynów', 'callsign':'Bry', 'type':'po', 'km':3.88},
         {'name':'Katowice Ligota', 'callsign':'KL', 'type':'st', 'km':6.08},
         {'name':'Katowice Piotrowice', 'callsign':'KtP', 'type':'po', 'km':7.75},
         {'name':'Katowice Podlesie', 'callsign':'', 'type':'po', 'km':11.35},
         {'name':'Mąkołowiec', 'callsign':'Mc', 'type':'podg', 'km':14.04},
         {'name':'Tychy', 'callsign':'Ty', 'type':'st', 'km':16.97}),
    '140':({'name':'Katowice Ligota', 'callsign':'KL', 'type':'st', 'km':0.00},
         {'name':'Katowice Piotrowice', 'callsign':'KtP', 'type':'po', 'km':1.66},
         {'name':'Mikołów Jamna', 'callsign':'MJ', 'type':'st', 'km':5.86},
         {'name':'Mikołów', 'callsign':'Mi', 'type':'st', 'km':8.75}),
    'depot527':({'name':'Katowice Stacja Manewrowa', 'callsign':'KO(STM)', 'type':'st', 'km':0.0},
                {'name':'Katowice Zawodzie Postojowa', 'callsign':'KO(IC)', 'type':'depot', 'km':0.9}),
    'depot200':({'name':'Katowice', 'callsign':'KO', 'type':'st', 'km':0},
	        {'name':'Katowice Raciborska', 'callsign':'KO(KS)', 'type':'depot', 'km':0.5})}


RAILWAYSEGMENTS={
    '137139GLYTy':({'name': 'Gliwice', 'callsign': 'GLC', 'type': 'st', 'km': 0.0},
                  {'name': 'Zabrze', 'callsign': 'ZZ', 'type': 'st', 'km': 8.18},
                  {'name': 'Ruda Śląska', 'callsign': 'RŚl', 'type': 'po', 'km': 12.5},
                  {'name': 'Ruda Chebzie', 'callsign': 'RCB', 'type': 'st', 'km': 15.36},
                  {'name': 'Świętochłowice', 'callsign': '', 'type': 'po', 'km': 18.69},
                  {'name': 'Chorzów Batory', 'callsign': 'CB', 'type': 'st', 'km': 20.94},
                  {'name': 'Katowice Towarowa KTC', 'callsign': 'KTC', 'type': 'podg', 'km': 24.19},
                  {'name': 'Katowice', 'callsign': 'KO', 'type': 'st', 'km': 26.71},
                  {'name': 'Katowice Brynów', 'callsign': 'Bry', 'type': 'po', 'km': 30.59},
                  {'name': 'Katowice Ligota', 'callsign': 'KL', 'type': 'st', 'km': 36.67},
                  {'name': 'Katowice Piotrowice', 'callsign': 'KtP', 'type': 'po', 'km': 44.42},
                  {'name': 'Katowice Podlesie', 'callsign': '', 'type': 'po', 'km': 55.77},
                  {'name': 'Mąkołowiec', 'callsign': 'Mc', 'type': 'podg', 'km': 69.81},
                  {'name': 'Tychy', 'callsign': 'Ty', 'type': 'st', 'km': 86.78}),
    '137138GLYKZ': ({'name': 'Gliwice', 'callsign': 'GLC', 'type': 'st', 'km': 0.0},
                    {'name': 'Zabrze', 'callsign': 'ZZ', 'type': 'st', 'km': 8.18},
                    {'name': 'Ruda Śląska', 'callsign': 'RSl', 'type': 'po', 'km': 12.5},
                    {'name': 'Ruda Chebzie', 'callsign': 'RCB', 'type': 'st', 'km': 15.36},
                    {'name': 'Świętochłowice', 'callsign': '', 'type': 'po', 'km': 18.69},
                    {'name': 'Chorzów Batory', 'callsign': 'CB', 'type': 'st', 'km': 20.94},
                    {'name': 'Katowice Towarowa KTC', 'callsign': 'KTC', 'type': 'podg', 'km': 24.19},
                    {'name': 'Katowice', 'callsign': 'KO', 'type': 'st', 'km': 26.71},
                    {'name':'Katowice Stacja Manewrowa', 'callsign':'KO(STM)', 'type':'st', 'km':27.21},
                    {'name':'Katowice Zawodzie', 'callsign':'KZ', 'type':'st', 'km':29.43}),
    '138139KZTY': ({'name':'Katowice Zawodzie', 'callsign':'KZ', 'type':'st', 'km':0.0},
                   {'name':'Katowice Stacja Manewrowa', 'callsign':'KO(STM)', 'type':'st', 'km':2.21},
                   {'name': 'Katowice', 'callsign': 'KO', 'type': 'st', 'km': 2.71},
                   {'name': 'Katowice Brynów', 'callsign': 'Bry', 'type': 'po', 'km': 6.6},
                   {'name': 'Katowice Ligota', 'callsign': 'KL', 'type': 'st', 'km': 8.8},
                   {'name': 'Katowice Piotrowice', 'callsign': 'KtP', 'type': 'po', 'km': 10.47},
                   {'name': 'Katowice Podlesie', 'callsign': '', 'type': 'po', 'km': 14.07},
                   {'name': 'Mąkołowiec', 'callsign': 'Mc', 'type': 'podg', 'km': 16.76},
                   {'name': 'Tychy', 'callsign': 'Ty', 'type': 'st', 'km': 19.69})
}


def station_on_lines(station):
    """Gives lines on which the station is located, along with the ordnal number"""
    result = []
    for line in RAILWAYLINES.keys():
        for station_found in list(
                filter(lambda x: x['callsign'] == station or x['name'] == station,
                       RAILWAYLINES[line])):
            result.append((line, RAILWAYLINES[line].index(station_found)))
    return result

def route_on_lines(route, lines):
    """The route is a sequence (list) of stations (names or call signs), 
    the line is a set of line identifiers.
    It will return a list with station ordinal numbers on lines."""
    result = []
    for station in route:
        result.append(tuple(filter(lambda x: x[0] in lines, station_on_line(station))))
    return [s for s in result if s!=()]

def station2km(station, segment):
    try:
        return list(filter(
            lambda x: x['callsign'].upper() == station.upper() or x['name'].upper() == station.upper(),
            RAILWAYSEGMENTS[segment]))[0]['km']
    except:
        raise ValueError

def station_on_segment(station, segment, exceptions=set([])):
    return len(list(filter(
        lambda x: ((x['callsign'].upper() == station.upper() or x['name'].upper() == station.upper())\
                    and station.upper() not in set([s.upper() for s in list(exceptions)])),
                    RAILWAYSEGMENTS[segment]))) > 0
            
def train_on_segment(train, segment, exceptions=set([])):
    return len(list(filter(lambda s: station_on_segment(s, segment, exceptions=exceptions), train.route)))

