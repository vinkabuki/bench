const isHappyNumber = (n: number): boolean => {
    const seen = new Set<number>();
    while (n !== 1 && !seen.has(n)) {
        seen.add(n);
        n = n.toString().split('').reduce((acc, digit) => acc + Math.pow(parseInt(digit), 2), 0);
    }
    return n === 1;
}

isHappyNumber(19);