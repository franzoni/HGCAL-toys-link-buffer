import random

def isThereL1A(probability):
    if probability > 1:
        print("isThereL1A: probability set to", probability)
        raise ValueError('isThereL1A: You cannot have L1 tirgger probability larger than 1 ! ')
    return random.random() < probability
