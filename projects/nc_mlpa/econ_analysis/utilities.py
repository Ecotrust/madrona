'''
Returns a pseudo-random integer between low and high. Defaults to
between 1 and 1 trillion.
'''
def getRandInt(low=1, high=1000000000):
    import random
    return random.randint(low, high) 

'''
A better rounding operation.  Chops off remainder as Python can leave 
repeating decimal places.
'''
def trueRound(num, places=4):
    num = round(num,places)
    format_str = '%.'+str(places)+'f'
    result = format_str % num
    return result

def percentage(one, two):
    return (one/two)*100    