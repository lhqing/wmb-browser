def auto_size(n, scale=3):
    """Auto determine dot size based on ax size and n dots"""
    if n < 500:
        s = 14 - n / 100
    elif n < 1500:
        s = 7
    elif n < 3000:
        s = 5
    elif n < 8000:
        s = 3
    elif n < 15000:
        s = 2
    elif n < 30000:
        s = 1.5
    elif n < 50000:
        s = 1
    elif n < 80000:
        s = 0.8
    elif n < 150000:
        s = 0.6
    elif n < 300000:
        s = 0.5
    elif n < 500000:
        s = 0.4
    elif n < 800000:
        s = 0.3
    elif n < 1000000:
        s = 0.2
    elif n < 2000000:
        s = 0.1
    elif n < 3000000:
        s = 0.07
    elif n < 4000000:
        s = 0.05
    elif n < 5000000:
        s = 0.03
    else:
        s = 0.02

    s = s * scale
    return s
