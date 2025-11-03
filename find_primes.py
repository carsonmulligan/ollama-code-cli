def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def find_primes_up_to(limit):
    primes = []
    for number in range(2, limit + 1):
        if is_prime(number):
            primes.append(number)
    return primes

limit = 100
primes = find_primes_up_to(limit)
print("Prime numbers up to", limit, ":", primes)

if __name__ == "__main__":
    print("Running the script...")
