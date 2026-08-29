import asyncio
import json
import time
import httpx

API_URL = "http://localhost:3000/api/submit"
STATUS_URL = "http://localhost:3000/api/submission"
PROBLEM_ID = "top-k-frequent"
TOTAL_SUBMISSIONS = 100
POLL_INTERVAL = 1.0
# Worker concurrency is 5 (src/worker.ts). 100 jobs => 20 waves.
# Each job can take up to CONTAINER_TIMEOUT_SECONDS (30s) plus overhead.
# 60s is shorter than worst-case queue wait (~20 * 35s).
WORKER_CONCURRENCY = 5
MAX_JOB_SECONDS = 35.0
POLL_TIMEOUT = (TOTAL_SUBMISSIONS / WORKER_CONCURRENCY) * MAX_JOB_SECONDS + 60.0

# httpx.DEFAULT_LIMITS is max_connections=100, max_keepalive_connections=20.
# 100 concurrent polls sit exactly on that cap; raise it so requests are not
# queued behind keepalive reuse.
HTTP_LIMITS = httpx.Limits(
    max_connections=200,
    max_keepalive_connections=100,
)

# ============================================================
# 100 realistic contestant submissions
#
# Problem:
#   LeetCode 347 - Top K Frequent Elements
#
# Expected function:
#
#   def topKFrequent(nums, k):
#       ...
#
# Some submissions are:
#   - Correct
#   - Correct but inefficient
#   - Wrong
#   - Runtime errors
#   - Deliberately slow
# ============================================================

SOLUTIONS = [

# ============================================================
# 1-10: Correct solutions
# ============================================================

"""def topKFrequent(nums, k):
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    pairs = list(freq.items())
    pairs.sort(key=lambda x: x[1], reverse=True)

    return [x[0] for x in pairs[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq

    freq = defaultdict(int)

    for num in nums:
        freq[num] += 1

    heap = []

    for num, count in freq.items():
        heapq.heappush(heap, (count, num))

        if len(heap) > k:
            heapq.heappop(heap)

    return [num for count, num in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    buckets = [[] for _ in range(len(nums) + 1)]

    for num, count in counter.items():
        buckets[count].append(num)

    result = []

    for count in range(len(buckets) - 1, 0, -1):
        for num in buckets[count]:
            result.append(num)

            if len(result) == k:
                return result

    return result
""",

"""def topKFrequent(nums, k):
    freq = {}

    for x in nums:
        if x not in freq:
            freq[x] = 0
        freq[x] += 1

    ordered = sorted(
        freq.keys(),
        key=lambda x: freq[x],
        reverse=True
    )

    return ordered[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counts = Counter()

    for value in nums:
        counts[value] += 1

    result = []

    for value, count in counts.most_common(k):
        result.append(value)

    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    frequency = Counter(nums)

    values = list(frequency.keys())

    values.sort(
        key=lambda value: frequency[value],
        reverse=True
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    result = []

    while len(result) < k:
        best = None
        best_count = -1

        for num in freq:
            if num not in result and freq[num] > best_count:
                best = num
                best_count = freq[num]

        result.append(best)

    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq

    counts = Counter(nums)

    return heapq.nlargest(
        k,
        counts.keys(),
        key=counts.get
    )
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counts = Counter(nums)

    return sorted(
        counts,
        key=counts.get,
        reverse=True
    )[:k]
""",


# ============================================================
# 11-20: Correct but different styles
# ============================================================

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.setdefault(num, 0) + 1

    result = list(freq)

    result.sort(
        key=freq.__getitem__,
        reverse=True
    )

    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    c = Counter(nums)

    return [
        item[0]
        for item in sorted(
            c.items(),
            key=lambda pair: pair[1],
            reverse=True
        )[:k]
    ]
""",

"""def topKFrequent(nums, k):
    frequency = {}

    for number in nums:
        frequency[number] = frequency.get(number, 0) + 1

    result = sorted(
        frequency,
        key=lambda number: (-frequency[number], number)
    )

    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    ranked = []

    for number in counter:
        ranked.append(
            (counter[number], number)
        )

    ranked.sort(reverse=True)

    return [
        number
        for _, number in ranked[:k]
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    items = list(counter.items())

    items.sort(
        key=lambda pair: pair[1],
        reverse=True
    )

    answer = []

    for number, _ in items[:k]:
        answer.append(number)

    return answer
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict

    counts = defaultdict(int)

    for number in nums:
        counts[number] += 1

    candidates = list(counts)

    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            if counts[candidates[j]] > counts[candidates[i]]:
                candidates[i], candidates[j] = (
                    candidates[j],
                    candidates[i]
                )

    return candidates[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    frequency = Counter(nums)

    result = []

    for _ in range(k):
        value = max(
            frequency,
            key=frequency.get
        )

        result.append(value)
        del frequency[value]

    return result
""",

"""def topKFrequent(nums, k):
    counts = {}

    for num in nums:
        counts[num] = counts.get(num, 0) + 1

    ordered = list(counts.items())

    ordered.sort(
        key=lambda item: item[1],
        reverse=True
    )

    answer = []

    for item in ordered:
        if len(answer) >= k:
            break

        answer.append(item[0])

    return answer
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter()

    for n in nums:
        freq.update([n])

    return [
        n
        for n, count
        in freq.most_common(k)
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    pairs = counter.most_common()

    result = []

    for i in range(k):
        result.append(pairs[i][0])

    return result
""",


# ============================================================
# 21-40: Inefficient but mostly correct
# ============================================================

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    answer = []

    for _ in range(k):
        best = None

        for num in freq:
            if best is None or freq[num] > freq[best]:
                best = num

        answer.append(best)
        del freq[best]

    return answer
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        if num in freq:
            freq[num] += 1
        else:
            freq[num] = 1

    result = []

    while len(result) < k:
        current = sorted(
            freq.items(),
            key=lambda x: x[1],
            reverse=True
        )

        result.append(current[0][0])
        del freq[current[0][0]]

    return result
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        count = 0

        for other in nums:
            if other == num:
                count += 1

        freq[num] = count

    ordered = sorted(
        freq,
        key=lambda x: freq[x],
        reverse=True
    )

    return ordered[:k]
""",

"""def topKFrequent(nums, k):
    unique = []

    for num in nums:
        if num not in unique:
            unique.append(num)

    frequencies = []

    for num in unique:
        count = nums.count(num)
        frequencies.append((num, count))

    frequencies.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [x[0] for x in frequencies[:k]]
""",

"""def topKFrequent(nums, k):
    counts = {}

    for num in nums:
        counts[num] = nums.count(num)

    values = list(counts.keys())

    values.sort(
        key=lambda x: counts[x],
        reverse=True
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counts = Counter(nums)

    values = list(counts.keys())

    # Repeated sorting
    for _ in range(min(k, len(values))):
        values.sort(
            key=lambda x: counts[x],
            reverse=True
        )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for number in nums:
        freq[number] = freq.get(number, 0) + 1

    values = list(freq.keys())

    result = []

    while values and len(result) < k:
        best = values[0]

        for value in values:
            if freq[value] > freq[best]:
                best = value

        result.append(best)
        values.remove(best)

    return result
""",

"""def topKFrequent(nums, k):
    frequency = {}

    for number in nums:
        if number not in frequency:
            frequency[number] = 0

        frequency[number] += 1

    result = []

    while len(result) < k:
        maximum = -1
        candidate = None

        for number, count in frequency.items():
            if count > maximum:
                maximum = count
                candidate = number

        result.append(candidate)
        frequency.pop(candidate)

    return result
""",

"""def topKFrequent(nums, k):
    counts = {}

    for x in nums:
        counts[x] = counts.get(x, 0) + 1

    items = list(counts.items())

    # Selection sort
    for i in range(min(k, len(items))):
        best = i

        for j in range(i + 1, len(items)):
            if items[j][1] > items[best][1]:
                best = j

        items[i], items[best] = items[best], items[i]

    return [x[0] for x in items[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = []

    while len(result) < k:
        maximum = max(freq.values())

        for number in freq:
            if freq[number] == maximum:
                result.append(number)
                del freq[number]
                break

    return result
""",

"""def topKFrequent(nums, k):
    frequency = {}

    for x in nums:
        frequency[x] = frequency.get(x, 0) + 1

    buckets = {}

    for value, count in frequency.items():
        if count not in buckets:
            buckets[count] = []

        buckets[count].append(value)

    result = []

    for count in sorted(buckets, reverse=True):
        for value in buckets[count]:
            result.append(value)

            if len(result) == k:
                return result

    return result
""",

"""def topKFrequent(nums, k):
    freq = {}

    for x in nums:
        freq[x] = freq.get(x, 0) + 1

    sorted_items = sorted(
        freq.items(),
        key=lambda x: x[1]
    )

    sorted_items.reverse()

    return [
        item[0]
        for item in sorted_items[:k]
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = list(freq.keys())

    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            if freq[result[j]] > freq[result[i]]:
                result[i], result[j] = (
                    result[j],
                    result[i]
                )

    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for n in nums:
        freq[n] = freq.get(n, 0) + 1

    values = list(freq)

    # Bubble sort
    for i in range(len(values)):
        swapped = False

        for j in range(len(values) - 1 - i):
            if freq[values[j]] < freq[values[j + 1]]:
                values[j], values[j + 1] = (
                    values[j + 1],
                    values[j]
                )
                swapped = True

        if not swapped:
            break

    return values[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    values = []

    for number in freq:
        values.append(number)

    values.sort(
        key=lambda number: freq[number],
        reverse=True
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}

    for n in nums:
        frequency[n] = frequency.get(n, 0) + 1

    pairs = []

    for number in frequency:
        pairs.append(
            [number, frequency[number]]
        )

    pairs.sort(
        key=lambda pair: pair[1],
        reverse=True
    )

    return [
        pair[0]
        for pair in pairs[:k]
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    answer = []

    for number in freq:
        inserted = False

        for i in range(len(answer)):
            if freq[number] > freq[answer[i]]:
                answer.insert(i, number)
                inserted = True
                break

        if not inserted:
            answer.append(number)

        if len(answer) > k:
            answer.pop()

    return answer
""",

"""def topKFrequent(nums, k):
    freq = {}

    for number in nums:
        freq[number] = freq.get(number, 0) + 1

    result = list(freq)

    for i in range(len(result)):
        best = i

        for j in range(i + 1, len(result)):
            if freq[result[j]] > freq[result[best]]:
                best = j

        result[i], result[best] = (
            result[best],
            result[i]
        )

    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    pairs = list(counter.items())

    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            if pairs[j][1] > pairs[i][1]:
                pairs[i], pairs[j] = pairs[j], pairs[i]

    return [x[0] for x in pairs[:k]]
""",

"""def topKFrequent(nums, k):
    frequency = {}

    for n in nums:
        frequency[n] = frequency.get(n, 0) + 1

    result = []

    for _ in range(k):
        candidate = None

        for n in frequency:
            if candidate is None:
                candidate = n
            elif frequency[n] > frequency[candidate]:
                candidate = n

        result.append(candidate)
        del frequency[candidate]

    return result
""",


# ============================================================
# 41-60: Buggy submissions
# ============================================================

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    # BUG: ascending instead of descending
    return sorted(freq.keys(), key=freq.get)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    # BUG: returns least frequent
    return sorted(
        freq,
        key=lambda x: freq[x]
    )[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    # BUG: off by one
    values = sorted(
        freq,
        key=lambda x: freq[x],
        reverse=True
    )

    return values[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    # BUG: returns k+1 elements
    return [
        x for x, _
        in freq.most_common(k + 1)
    ]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    # BUG: forgot reverse=True
    values = sorted(
        freq,
        key=lambda x: freq[x]
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    values = list(freq)

    # BUG: sorts by value instead of frequency
    values.sort()

    return values[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    # BUG: most_common returns tuples
    return freq.most_common(k)
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = []

    # BUG: indexes frequency rather than keys
    for i in range(k):
        result.append(freq[i])

    return result
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    result = []

    for num in nums:
        if num not in result:
            result.append(num)

        if len(result) == k:
            break

    # BUG: just returns first k unique values
    return result
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    result = list(freq.keys())

    # BUG: wrong sort direction
    result.sort(
        key=lambda x: -freq[x]
    )

    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = []

    for number in freq:
        if freq[number] >= k:
            result.append(number)

    # BUG: misunderstands k as frequency threshold
    return result[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}

    for number in nums:
        frequency[number] = frequency.get(number, 0) + 1

    # BUG: dictionary insertion order isn't frequency order
    return list(frequency.keys())[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for x in nums:
        freq[x] = freq.get(x, 0) + 1

    result = sorted(
        freq.items(),
        key=lambda x: x[0],
        reverse=True
    )

    # BUG: sorted by number
    return [x[0] for x in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = []

    for number, count in freq.items():
        if count > 1:
            result.append(number)

    # BUG: ignores elements occurring once
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for n in nums:
        freq[n] = freq.get(n, 0) + 1

    values = list(freq)

    values.sort(
        key=lambda x: freq[x]
    )

    # BUG
    return values[-k-1:-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = [
        x for x in freq
        if freq[x] == max(freq.values())
    ]

    # BUG: only returns maximum-frequency elements
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = []

    for number in sorted(freq):
        result.append(number)

    # BUG
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for n in nums:
        freq[n] = freq.get(n, 0) + 1

    values = sorted(
        freq,
        key=lambda x: freq[x],
        reverse=True
    )

    # BUG: k interpreted as zero-based index
    return values[:k+1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    # BUG: returns frequencies instead of values
    return [
        count
        for _, count in freq.most_common(k)
    ]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for x in nums:
        freq[x] = freq.get(x, 0) + 1

    result = sorted(
        freq.items(),
        key=lambda pair: pair[1],
        reverse=True
    )

    # BUG: returns (number, frequency)
    return result[:k]
""",


# ============================================================
# 61-75: Runtime errors
# ============================================================

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] += 1

    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    result = []

    for i in range(k):
        result.append(freq.most_common()[i][0])

    return result
""",

"""def topKFrequent(nums, k):
    freq = Counter(nums)

    return freq.most_common(k)
""",

"""def topKFrequent(nums, k):
    result = []
    for i in range(k):
        result.append(nums[i])

    return result
""",

"""def topKFrequent(nums, k):
    freq = {}

    for n in nums:
        freq[n] = freq[n] + 1

    return list(freq)[:k]
""",

"""def topKFrequent(nums, k):
    numbers = None

    for x in nums:
        numbers.append(x)

    return numbers[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for x in nums:
        freq[x] = freq.get(x, 0) + 1

    return sorted(
        freq,
        key=lambda x: frequency[x],
        reverse=True
    )[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for x in nums:
        freq[x] = freq.get(x, 0) + 1

    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    c = Counter(nums)

    return c.most_common(k)
    
    print(undefined_variable)
""",

"""def topKFrequent(nums, k):
    for i in range(len(nums) + 1):
        print(nums[i])

    return []
""",

"""def topKFrequent(nums, k):
    freq = {}

    for n in nums:
        freq[n] += 1

    values = list(freq.keys())

    values.sort(
        key=lambda x: freq[x],
        reverse=True
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    c = Counter(nums)

    result = c.most_common(k)

    return [x[0] for x in result]

    raise RuntimeError("unexpected failure")
""",

"""def topKFrequent(nums, k):
    import nonexistent_module

    return []
""",

"""def topKFrequent(nums, k):
    x = 10 / 0

    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("Contestant bug")
""",


# ============================================================
# 76-85: Deliberately slow
# ============================================================

"""def topKFrequent(nums, k):
    import time

    time.sleep(4)

    from collections import Counter
    return [
        x for x, _
        in Counter(nums).most_common(k)
    ]
""",

"""def topKFrequent(nums, k):
    import time

    time.sleep(5)

    freq = {}

    for n in nums:
        freq[n] = freq.get(n, 0) + 1

    return sorted(
        freq,
        key=freq.get,
        reverse=True
    )[:k]
""",

"""def topKFrequent(nums, k):
    import time

    time.sleep(10)

    return []
""",

"""def topKFrequent(nums, k):
    import time

    while True:
        time.sleep(0.1)
""",

"""def topKFrequent(nums, k):
    while True:
        pass
""",

"""def topKFrequent(nums, k):
    total = 0

    # Huge CPU loop
    for i in range(10**9):
        total += i

    from collections import Counter

    return [
        x for x, _
        in Counter(nums).most_common(k)
    ]
""",

"""def topKFrequent(nums, k):
    result = []

    for x in nums:
        for y in nums:
            if x == y and x not in result:
                result.append(x)

    result.sort()

    return result[:k]
""",

"""def topKFrequent(nums, k):
    import time

    for _ in range(50):
        time.sleep(0.1)

    from collections import Counter

    return [
        x for x, _
        in Counter(nums).most_common(k)
    ]
""",

"""def topKFrequent(nums, k):
    result = []

    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] == nums[j]:
                pass

    from collections import Counter

    return [
        x for x, _
        in Counter(nums).most_common(k)
    ]
""",

"""def topKFrequent(nums, k):
    import time

    time.sleep(3.5)

    from collections import Counter

    return [
        x for x, _
        in Counter(nums).most_common(k)
    ]
""",


# ============================================================
# 86-100: More realistic mixed submissions
# ============================================================

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq

    freq = Counter(nums)

    heap = []

    for num, count in freq.items():
        heapq.heappush(heap, (-count, num))

    return [
        heapq.heappop(heap)[1]
        for _ in range(k)
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    buckets = [[] for _ in range(len(nums) + 1)]

    for num, count in freq.items():
        buckets[count].append(num)

    answer = []

    for bucket in reversed(buckets):
        answer.extend(bucket)

        if len(answer) >= k:
            break

    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    return sorted(
        freq.keys(),
        key=lambda x: (-freq[x], x)
    )[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    answer = []

    for number, count in freq.items():
        answer.append((count, number))

    answer.sort(reverse=True)

    return [number for _, number in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict

    freq = defaultdict(int)

    for value in nums:
        freq[value] += 1

    ordered = list(freq.keys())

    ordered.sort(
        key=lambda value: freq[value],
        reverse=True
    )

    return ordered[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq

    counter = Counter(nums)

    return [
        item[1]
        for item in heapq.nlargest(
            k,
            counter.items(),
            key=lambda x: x[1]
        )
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    result = counter.most_common(k)

    return [number for number, frequency in result]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for value in nums:
        if value in freq:
            freq[value] += 1
        else:
            freq[value] = 1

    values = list(freq.keys())

    values.sort(
        key=lambda value: freq[value],
        reverse=True
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counter = Counter(nums)

    result = list(counter)

    result.sort(
        key=counter.get,
        reverse=True
    )

    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counts = Counter()

    for number in nums:
        counts[number] += 1

    pairs = list(counts.items())

    pairs.sort(
        key=lambda p: p[1],
        reverse=True
    )

    answer = []

    for i in range(k):
        answer.append(pairs[i][0])

    return answer
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    counts = Counter(nums)

    sorted_values = sorted(
        counts,
        key=lambda value: counts[value],
        reverse=True
    )

    return sorted_values[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    answer = []

    for value, count in freq.items():
        answer.append((count, value))

    answer.sort(reverse=True)

    return [
        value
        for count, value in answer[:k]
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    values = list(freq)

    values.sort(
        reverse=True,
        key=lambda x: freq[x]
    )

    return values[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    result = sorted(
        freq.items(),
        reverse=True,
        key=lambda item: item[1]
    )

    return [
        number
        for number, count in result[:k]
    ]
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    freq = Counter(nums)

    values = freq.keys()

    values = sorted(
        values,
        key=lambda x: freq[x],
        reverse=True
    )

    return list(values[:k])
""",

"""def topKFrequent(nums, k):
    from collections import Counter

    frequency = Counter(nums)

    result = []

    for value in frequency:
        result.append(value)

    result.sort(
        key=lambda x: frequency[x],
        reverse=True
    )

    return result[:k]
""",

]


# ============================================================
# Make sure we have exactly 100
# ============================================================
SOLUTIONS = SOLUTIONS[:100]
assert len(SOLUTIONS) == 100, (
    f"Expected 100 solutions, got {len(SOLUTIONS)}"
)


# ============================================================
# Submit one solution
# ============================================================

async def send_submission(client, index, code):
    payload = {
        "language": "python",
        "code": code,
        "problemId": PROBLEM_ID,
    }

    try:
        response = await client.post(
            API_URL,
            json=payload,
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()
        submission_id = data.get("submissionId")

        print(
            f"[Job {index + 1:03d}] "
            f"Queued -> {submission_id}"
        )

        return submission_id, time.time()

    except Exception as e:
        print(
            f"[Job {index + 1:03d}] "
            f"Failed to queue -> {e}"
        )

        return None, time.time()


def _result_payload(data):
    result = data.get("result")
    return result if isinstance(result, dict) else {}


# ============================================================
# Poll one submission until it reaches a terminal state
# ============================================================

async def poll_submission(client, index, submission_id, queued_at):
    history = []

    if submission_id is None:
        return {
            "index": index,
            "id": None,
            "state": "queue_failed",
            "status": None,
            "score": None,
            "error": None,
            "poll_history": history,
        }

    deadline = time.time() + POLL_TIMEOUT
    last_data = None
    last_error = None

    while time.time() < deadline:
        elapsed = time.time() - queued_at
        try:
            response = await client.get(
                f"{STATUS_URL}/{submission_id}",
                timeout=10.0,
            )
            # Snapshot the body before parsing so we never depend on a
            # connection-pool Response object remaining valid.
            status_code = response.status_code
            raw_text = response.text
        except Exception as e:
            last_error = str(e)
            entry = {
                "elapsed_s": round(elapsed, 3),
                "http_status": None,
                "raw": None,
                "error": last_error,
            }
            history.append(entry)
            print(
                f"[poll] id={submission_id} elapsed={elapsed:.1f}s "
                f"http=ERR {last_error}"
            )
            await asyncio.sleep(POLL_INTERVAL)
            continue

        print(
            f"[poll] id={submission_id} elapsed={elapsed:.1f}s "
            f"http={status_code} body={raw_text}"
        )
        history.append({
            "elapsed_s": round(elapsed, 3),
            "http_status": status_code,
            "raw": raw_text,
            "error": None,
        })

        if status_code >= 400:
            last_error = f"HTTP {status_code}: {raw_text}"
            await asyncio.sleep(POLL_INTERVAL)
            continue

        try:
            data = json.loads(raw_text) if raw_text else {}
        except json.JSONDecodeError as e:
            last_error = f"invalid json: {e}"
            await asyncio.sleep(POLL_INTERVAL)
            continue

        last_data = data
        state = data.get("state")
        result = _result_payload(data)

        # BullMQ (and this API) can report state=completed a moment before
        # returnvalue is persisted. Treating that as terminal produced the
        # "-" / "completed" rows: status fell back to r["state"], score was
        # None. Keep polling until the result payload is actually present.
        if state == "completed" and not result:
            await asyncio.sleep(POLL_INTERVAL)
            continue

        if state in ("completed", "failed"):
            return {
                "index": index,
                "id": submission_id,
                "state": state,
                "status": result.get("status"),
                "score": result.get("score"),
                "error": result.get("error") or data.get("failedReason"),
                "poll_history": history,
            }

        await asyncio.sleep(POLL_INTERVAL)

    result = _result_payload(last_data or {})
    last_state = (last_data or {}).get("state")
    return {
        "index": index,
        "id": submission_id,
        "state": "poll_timeout",
        "status": result.get("status"),
        "score": result.get("score"),
        "error": (
            f"No terminal result after {POLL_TIMEOUT:.0f}s "
            f"(last state={last_state!r})"
            + (f"; last_error={last_error}" if last_error else "")
        ),
        "poll_history": history,
    }


# ============================================================
# Main load test
# ============================================================

async def main():

    print(
        f"🚀 Sending {TOTAL_SUBMISSIONS} submissions "
        f"to {API_URL}\n"
    )

    start_time = time.time()

    async with httpx.AsyncClient(limits=HTTP_LIMITS) as client:

        submit_tasks = [
            send_submission(client, i, SOLUTIONS[i])
            for i in range(TOTAL_SUBMISSIONS)
        ]

        queued = await asyncio.gather(*submit_tasks)
        submission_ids = [item[0] for item in queued]
        queued_at = [item[1] for item in queued]

        queue_time = time.time() - start_time

        successful = sum(1 for s in submission_ids if s is not None)
        failed = TOTAL_SUBMISSIONS - successful

        print("\n" + "=" * 50)
        print("📊 API QUEUING METRICS")
        print("=" * 50)
        print(f"Total Sent          : {TOTAL_SUBMISSIONS}")
        print(f"Successfully Queued : {successful}")
        print(f"Failed              : {failed}")
        print(f"Time Taken          : {queue_time:.2f}s")
        if queue_time > 0:
            print(f"API Throughput      : {TOTAL_SUBMISSIONS / queue_time:.2f} req/sec")
        print("=" * 50)

        print(
            f"\n⏳ Polling {successful} jobs for results "
            f"(timeout {POLL_TIMEOUT:.0f}s each)...\n"
        )

        poll_start = time.time()

        poll_tasks = [
            poll_submission(client, i, submission_ids[i], queued_at[i])
            for i in range(TOTAL_SUBMISSIONS)
        ]

        results = await asyncio.gather(*poll_tasks)

        poll_time = time.time() - poll_start

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    status_counts = {}
    for r in results:
        key = r["status"] or r["state"]
        status_counts[key] = status_counts.get(key, 0) + 1

    print("\n" + "=" * 90)
    print("📊 JUDGE RESULT SUMMARY")
    print("=" * 90)
    print(f"Polling Time         : {poll_time:.2f}s\n")

    for key, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"{key:25s} : {count}")

    print("\n" + "-" * 90)
    print(f"{'Idx':>4} {'Submission ID':24} {'Status':18} {'Score':>7} {'Error'}")
    print("-" * 90)

    missing_score = []
    for r in sorted(results, key=lambda x: x["index"]):
        idx = r["index"] + 1
        status = r["status"] or r["state"]
        score = r["score"] if r["score"] is not None else "-"
        error = (r["error"] or "")[:50]
        sid = r["id"] or "-"
        print(f"{idx:>4} {sid!s:24} {status:18} {score!s:>7} {error}")
        if r["score"] is None and r["state"] not in ("queue_failed",):
            missing_score.append(r)

    print("=" * 90)

    if missing_score:
        print("\n" + "=" * 90)
        print("🔍 RAW POLL HISTORY FOR JOBS WITH NULL/'-' SCORE")
        print("=" * 90)
        for r in missing_score:
            print(
                f"\n--- idx={r['index'] + 1} id={r['id']} "
                f"state={r['state']} status={r['status']!r} ---"
            )
            for i, entry in enumerate(r["poll_history"], 1):
                print(
                    f"  #{i:03d} elapsed={entry['elapsed_s']:.1f}s "
                    f"http={entry['http_status']} error={entry['error']}"
                )
                print(f"       raw={entry['raw']}")
        print("=" * 90)


if __name__ == "__main__":
    asyncio.run(main())
