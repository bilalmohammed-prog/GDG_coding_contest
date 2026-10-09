import asyncio
import json
import time
import httpx

API_URL = "https://gdg-coding-contest-6dnm.vercel.app/api/submit"
STATUS_URL = "https://gdg-coding-contest-6dnm.vercel.app/api/submission"
PROBLEM_ID = "top-k-frequent"
TOTAL_SUBMISSIONS = 500
POLL_INTERVAL = 1.0
# Worker concurrency is 5 (src/worker.ts). 100 jobs => 20 waves.
# Each job can take up to CONTAINER_TIMEOUT_SECONDS (30s) plus overhead.
# 60s is shorter than worst-case queue wait (~20 * 35s).
WORKER_CONCURRENCY = 10
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


# ============================================================
# 101-1000: Auto-generated additional submissions (900 total)
#
# Generated programmatically: several distinct correct
# algorithms and several distinct bug/error/slow patterns,
# each rendered under many variable-naming permutations.
# Every entry was verified before inclusion:
#   - correct/inefficient solutions: executed against a battery
#     of ~29 randomized test cases (including tie scenarios) and
#     checked with a tie-aware answer validator matching the
#     judge's own answersMatch() semantics
#   - buggy solutions: executed and confirmed to actually fail
#     that same battery (never accidentally correct)
#   - runtime-error solutions: executed and confirmed to raise
#   - slow/hanging solutions: syntax-checked only, never executed
#     locally (some are deliberately infinite loops)
#   - all 1000 entries (100 original + 900 generated) confirmed
#     pairwise-unique
# ============================================================

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [num for num, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for num in nums:
        tally[num] += 1
    heap = []
    for num, c in tally.items():
        heapq.heappush(heap, (c, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for c, num in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in frequency.items():
        buckets[c].append(num)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            result.append(num)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq
    counter_map = Counter(nums)
    return heapq.nlargest(k, counter_map.keys(), key=counter_map.get)
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for num in nums:
        occurrences[num] = occurrences.get(num, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    result = list(stats.keys())
    result.sort(key=stats.__getitem__, reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for num in nums:
        if num in freqs:
            freqs[num] += 1
        else:
            freqs[num] = 1
    result = []
    for num, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for num, c in cnt.most_common():
        result.append(num)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for num in nums:
        counter2[num] = counter2.setdefault(num, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [num for num, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for num in nums:
        seen[num] = seen.get(num, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for num in nums:
        freq_map[num] += 1
    heap = []
    for num, c in freq_map.items():
        heapq.heappush(heap, (c, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for c, num in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in bag.items():
        buckets[c].append(num)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            result.append(num)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq
    num_counts = Counter(nums)
    return heapq.nlargest(k, num_counts.keys(), key=num_counts.get)
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for num in nums:
        tally_map[num] = tally_map.get(num, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    result = list(freq_table.keys())
    result.sort(key=freq_table.__getitem__, reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for num in nums:
        if num in counter_dict:
            counter_dict[num] += 1
        else:
            counter_dict[num] = 1
    result = []
    for num, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for num, c in occ.most_common():
        result.append(num)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for num in nums:
        score_map[num] = score_map.setdefault(num, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [n for n, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for n in nums:
        tally[n] += 1
    heap = []
    for n, c in tally.items():
        heapq.heappush(heap, (c, n))
        if len(heap) > k:
            heapq.heappop(heap)
    return [n for c, n in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in frequency.items():
        buckets[c].append(n)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            result.append(n)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for n in nums:
        occurrences[n] = occurrences.get(n, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for n in nums:
        if n in freqs:
            freqs[n] += 1
        else:
            freqs[n] = 1
    result = []
    for n, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for n, c in cnt.most_common():
        result.append(n)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for n in nums:
        counter2[n] = counter2.setdefault(n, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [n for n, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for n in nums:
        seen[n] = seen.get(n, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for n in nums:
        freq_map[n] += 1
    heap = []
    for n, c in freq_map.items():
        heapq.heappush(heap, (c, n))
        if len(heap) > k:
            heapq.heappop(heap)
    return [n for c, n in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in bag.items():
        buckets[c].append(n)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            result.append(n)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for n in nums:
        tally_map[n] = tally_map.get(n, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for n in nums:
        if n in counter_dict:
            counter_dict[n] += 1
        else:
            counter_dict[n] = 1
    result = []
    for n, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for n, c in occ.most_common():
        result.append(n)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for n in nums:
        score_map[n] = score_map.setdefault(n, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [x for x, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for x in nums:
        tally[x] += 1
    heap = []
    for x, c in tally.items():
        heapq.heappush(heap, (c, x))
        if len(heap) > k:
            heapq.heappop(heap)
    return [x for c, x in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in frequency.items():
        buckets[c].append(x)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for x in buckets[c]:
            result.append(x)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for x in nums:
        occurrences[x] = occurrences.get(x, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for x in nums:
        if x in freqs:
            freqs[x] += 1
        else:
            freqs[x] = 1
    result = []
    for x, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for x, c in cnt.most_common():
        result.append(x)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for x in nums:
        counter2[x] = counter2.setdefault(x, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [x for x, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for x in nums:
        seen[x] = seen.get(x, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for x in nums:
        freq_map[x] += 1
    heap = []
    for x, c in freq_map.items():
        heapq.heappush(heap, (c, x))
        if len(heap) > k:
            heapq.heappop(heap)
    return [x for c, x in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in bag.items():
        buckets[c].append(x)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for x in buckets[c]:
            result.append(x)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for x in nums:
        tally_map[x] = tally_map.get(x, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for x in nums:
        if x in counter_dict:
            counter_dict[x] += 1
        else:
            counter_dict[x] = 1
    result = []
    for x, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for x, c in occ.most_common():
        result.append(x)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for x in nums:
        score_map[x] = score_map.setdefault(x, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [value for value, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for value in nums:
        tally[value] += 1
    heap = []
    for value, c in tally.items():
        heapq.heappush(heap, (c, value))
        if len(heap) > k:
            heapq.heappop(heap)
    return [value for c, value in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, c in frequency.items():
        buckets[c].append(value)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for value in buckets[c]:
            result.append(value)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for value in nums:
        occurrences[value] = occurrences.get(value, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for value in nums:
        if value in freqs:
            freqs[value] += 1
        else:
            freqs[value] = 1
    result = []
    for value, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for value, c in cnt.most_common():
        result.append(value)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for value in nums:
        counter2[value] = counter2.setdefault(value, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [value for value, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for value in nums:
        seen[value] = seen.get(value, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for value in nums:
        freq_map[value] += 1
    heap = []
    for value, c in freq_map.items():
        heapq.heappush(heap, (c, value))
        if len(heap) > k:
            heapq.heappop(heap)
    return [value for c, value in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, c in bag.items():
        buckets[c].append(value)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for value in buckets[c]:
            result.append(value)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for value in nums:
        tally_map[value] = tally_map.get(value, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for value in nums:
        if value in counter_dict:
            counter_dict[value] += 1
        else:
            counter_dict[value] = 1
    result = []
    for value, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for value, c in occ.most_common():
        result.append(value)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for value in nums:
        score_map[value] = score_map.setdefault(value, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [item for item, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for item in nums:
        counts[item] = counts.get(item, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for item in nums:
        tally[item] += 1
    heap = []
    for item, c in tally.items():
        heapq.heappush(heap, (c, item))
        if len(heap) > k:
            heapq.heappop(heap)
    return [item for c, item in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for item, c in frequency.items():
        buckets[c].append(item)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for item in buckets[c]:
            result.append(item)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for item in nums:
        occurrences[item] = occurrences.get(item, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for item in nums:
        if item in freqs:
            freqs[item] += 1
        else:
            freqs[item] = 1
    result = []
    for item, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for item, c in cnt.most_common():
        result.append(item)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for item in nums:
        counter2[item] = counter2.setdefault(item, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [item for item, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for item in nums:
        seen[item] = seen.get(item, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for item in nums:
        freq_map[item] += 1
    heap = []
    for item, c in freq_map.items():
        heapq.heappush(heap, (c, item))
        if len(heap) > k:
            heapq.heappop(heap)
    return [item for c, item in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for item, c in bag.items():
        buckets[c].append(item)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for item in buckets[c]:
            result.append(item)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for item in nums:
        tally_map[item] = tally_map.get(item, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for item in nums:
        if item in counter_dict:
            counter_dict[item] += 1
        else:
            counter_dict[item] = 1
    result = []
    for item, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for item, c in occ.most_common():
        result.append(item)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for item in nums:
        score_map[item] = score_map.setdefault(item, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [v for v, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for v in nums:
        counts[v] = counts.get(v, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for v in nums:
        tally[v] += 1
    heap = []
    for v, c in tally.items():
        heapq.heappush(heap, (c, v))
        if len(heap) > k:
            heapq.heappop(heap)
    return [v for c, v in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for v, c in frequency.items():
        buckets[c].append(v)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for v in buckets[c]:
            result.append(v)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for v in nums:
        occurrences[v] = occurrences.get(v, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for v in nums:
        if v in freqs:
            freqs[v] += 1
        else:
            freqs[v] = 1
    result = []
    for v, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for v, c in cnt.most_common():
        result.append(v)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for v in nums:
        counter2[v] = counter2.setdefault(v, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [v for v, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for v in nums:
        seen[v] = seen.get(v, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for v in nums:
        freq_map[v] += 1
    heap = []
    for v, c in freq_map.items():
        heapq.heappush(heap, (c, v))
        if len(heap) > k:
            heapq.heappop(heap)
    return [v for c, v in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for v, c in bag.items():
        buckets[c].append(v)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for v in buckets[c]:
            result.append(v)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for v in nums:
        tally_map[v] = tally_map.get(v, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for v in nums:
        if v in counter_dict:
            counter_dict[v] += 1
        else:
            counter_dict[v] = 1
    result = []
    for v, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for v, c in occ.most_common():
        result.append(v)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for v in nums:
        score_map[v] = score_map.setdefault(v, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [elem for elem, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for elem in nums:
        counts[elem] = counts.get(elem, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for elem in nums:
        tally[elem] += 1
    heap = []
    for elem, c in tally.items():
        heapq.heappush(heap, (c, elem))
        if len(heap) > k:
            heapq.heappop(heap)
    return [elem for c, elem in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for elem, c in frequency.items():
        buckets[c].append(elem)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for elem in buckets[c]:
            result.append(elem)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for elem in nums:
        occurrences[elem] = occurrences.get(elem, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for elem in nums:
        if elem in freqs:
            freqs[elem] += 1
        else:
            freqs[elem] = 1
    result = []
    for elem, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for elem, c in cnt.most_common():
        result.append(elem)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for elem in nums:
        counter2[elem] = counter2.setdefault(elem, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [elem for elem, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for elem in nums:
        seen[elem] = seen.get(elem, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for elem in nums:
        freq_map[elem] += 1
    heap = []
    for elem, c in freq_map.items():
        heapq.heappush(heap, (c, elem))
        if len(heap) > k:
            heapq.heappop(heap)
    return [elem for c, elem in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for elem, c in bag.items():
        buckets[c].append(elem)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for elem in buckets[c]:
            result.append(elem)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for elem in nums:
        tally_map[elem] = tally_map.get(elem, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for elem in nums:
        if elem in counter_dict:
            counter_dict[elem] += 1
        else:
            counter_dict[elem] = 1
    result = []
    for elem, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for elem, c in occ.most_common():
        result.append(elem)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for elem in nums:
        score_map[elem] = score_map.setdefault(elem, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [number for number, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for number in nums:
        counts[number] = counts.get(number, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for number in nums:
        tally[number] += 1
    heap = []
    for number, c in tally.items():
        heapq.heappush(heap, (c, number))
        if len(heap) > k:
            heapq.heappop(heap)
    return [number for c, number in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for number, c in frequency.items():
        buckets[c].append(number)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for number in buckets[c]:
            result.append(number)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for number in nums:
        occurrences[number] = occurrences.get(number, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for number in nums:
        if number in freqs:
            freqs[number] += 1
        else:
            freqs[number] = 1
    result = []
    for number, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for number, c in cnt.most_common():
        result.append(number)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for number in nums:
        counter2[number] = counter2.setdefault(number, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [number for number, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for number in nums:
        seen[number] = seen.get(number, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for number in nums:
        freq_map[number] += 1
    heap = []
    for number, c in freq_map.items():
        heapq.heappush(heap, (c, number))
        if len(heap) > k:
            heapq.heappop(heap)
    return [number for c, number in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for number, c in bag.items():
        buckets[c].append(number)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for number in buckets[c]:
            result.append(number)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for number in nums:
        tally_map[number] = tally_map.get(number, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for number in nums:
        if number in counter_dict:
            counter_dict[number] += 1
        else:
            counter_dict[number] = 1
    result = []
    for number, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for number, c in occ.most_common():
        result.append(number)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for number in nums:
        score_map[number] = score_map.setdefault(number, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [val for val, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for val in nums:
        counts[val] = counts.get(val, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for val in nums:
        tally[val] += 1
    heap = []
    for val, c in tally.items():
        heapq.heappush(heap, (c, val))
        if len(heap) > k:
            heapq.heappop(heap)
    return [val for c, val in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for val, c in frequency.items():
        buckets[c].append(val)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for val in buckets[c]:
            result.append(val)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for val in nums:
        occurrences[val] = occurrences.get(val, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for val in nums:
        if val in freqs:
            freqs[val] += 1
        else:
            freqs[val] = 1
    result = []
    for val, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for val, c in cnt.most_common():
        result.append(val)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for val in nums:
        counter2[val] = counter2.setdefault(val, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [val for val, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for val in nums:
        seen[val] = seen.get(val, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for val in nums:
        freq_map[val] += 1
    heap = []
    for val, c in freq_map.items():
        heapq.heappush(heap, (c, val))
        if len(heap) > k:
            heapq.heappop(heap)
    return [val for c, val in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for val, c in bag.items():
        buckets[c].append(val)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for val in buckets[c]:
            result.append(val)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for val in nums:
        tally_map[val] = tally_map.get(val, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for val in nums:
        if val in counter_dict:
            counter_dict[val] += 1
        else:
            counter_dict[val] = 1
    result = []
    for val, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for val, c in occ.most_common():
        result.append(val)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for val in nums:
        score_map[val] = score_map.setdefault(val, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return [e for e, _ in freq.most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for e in nums:
        counts[e] = counts.get(e, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    tally = defaultdict(int)
    for e in nums:
        tally[e] += 1
    heap = []
    for e, c in tally.items():
        heapq.heappush(heap, (c, e))
        if len(heap) > k:
            heapq.heappop(heap)
    return [e for c, e in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for e, c in frequency.items():
        buckets[c].append(e)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for e in buckets[c]:
            result.append(e)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for e in nums:
        occurrences[e] = occurrences.get(e, 0) + 1
    result = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for e in nums:
        if e in freqs:
            freqs[e] += 1
        else:
            freqs[e] = 1
    result = []
    for e, c in sorted(freqs.items(), key=lambda p: -p[1]):
        result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for e, c in cnt.most_common():
        result.append(e)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for e in nums:
        counter2[e] = counter2.setdefault(e, 0) + 1
    result = list(counter2)
    result.sort(key=lambda z: counter2[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [e for e, _ in hist.most_common(k)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for e in nums:
        seen[e] = seen.get(e, 0) + 1
    result = sorted(seen, key=lambda z: seen[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freq_map = defaultdict(int)
    for e in nums:
        freq_map[e] += 1
    heap = []
    for e, c in freq_map.items():
        heapq.heappush(heap, (c, e))
        if len(heap) > k:
            heapq.heappop(heap)
    return [e for c, e in heap]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for e, c in bag.items():
        buckets[c].append(e)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for e in buckets[c]:
            result.append(e)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for e in nums:
        tally_map[e] = tally_map.get(e, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for e in nums:
        if e in counter_dict:
            counter_dict[e] += 1
        else:
            counter_dict[e] = 1
    result = []
    for e, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    result = []
    for e, c in occ.most_common():
        result.append(e)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for e in nums:
        score_map[e] = score_map.setdefault(e, 0) + 1
    result = list(score_map)
    result.sort(key=lambda z: score_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    answer = sorted(counts, key=lambda z: counts[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in frequency.items():
        buckets[c].append(num)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            answer.append(num)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for num in nums:
        occurrences[num] = occurrences.get(num, 0) + 1
    answer = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    answer = list(stats.keys())
    answer.sort(key=stats.__getitem__, reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for num in nums:
        if num in freqs:
            freqs[num] += 1
        else:
            freqs[num] = 1
    answer = []
    for num, c in sorted(freqs.items(), key=lambda p: -p[1]):
        answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    answer = []
    for num, c in cnt.most_common():
        answer.append(num)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for num in nums:
        counter2[num] = counter2.setdefault(num, 0) + 1
    answer = list(counter2)
    answer.sort(key=lambda z: counter2[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for num in nums:
        seen[num] = seen.get(num, 0) + 1
    answer = sorted(seen, key=lambda z: seen[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in bag.items():
        buckets[c].append(num)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            answer.append(num)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for num in nums:
        tally_map[num] = tally_map.get(num, 0) + 1
    answer = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    answer = list(freq_table.keys())
    answer.sort(key=freq_table.__getitem__, reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for num in nums:
        if num in counter_dict:
            counter_dict[num] += 1
        else:
            counter_dict[num] = 1
    answer = []
    for num, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    answer = []
    for num, c in occ.most_common():
        answer.append(num)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for num in nums:
        score_map[num] = score_map.setdefault(num, 0) + 1
    answer = list(score_map)
    answer.sort(key=lambda z: score_map[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    answer = sorted(counts, key=lambda z: counts[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in frequency.items():
        buckets[c].append(n)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            answer.append(n)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for n in nums:
        occurrences[n] = occurrences.get(n, 0) + 1
    answer = sorted(occurrences.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for n in nums:
        if n in freqs:
            freqs[n] += 1
        else:
            freqs[n] = 1
    answer = []
    for n, c in sorted(freqs.items(), key=lambda p: -p[1]):
        answer.append(n)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    answer = []
    for n, c in cnt.most_common():
        answer.append(n)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    counter2 = dict()
    for n in nums:
        counter2[n] = counter2.setdefault(n, 0) + 1
    answer = list(counter2)
    answer.sort(key=lambda z: counter2[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for n in nums:
        seen[n] = seen.get(n, 0) + 1
    answer = sorted(seen, key=lambda z: seen[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in bag.items():
        buckets[c].append(n)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            answer.append(n)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for n in nums:
        tally_map[n] = tally_map.get(n, 0) + 1
    answer = sorted(tally_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for n in nums:
        if n in counter_dict:
            counter_dict[n] += 1
        else:
            counter_dict[n] = 1
    answer = []
    for n, c in sorted(counter_dict.items(), key=lambda p: -p[1]):
        answer.append(n)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    answer = []
    for n, c in occ.most_common():
        answer.append(n)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    score_map = dict()
    for n in nums:
        score_map[n] = score_map.setdefault(n, 0) + 1
    answer = list(score_map)
    answer.sort(key=lambda z: score_map[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for num in nums:
        freq[num] = freq.setdefault(num, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for num, c in counts.most_common():
        result.append(num)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for num in nums:
        if num in tally:
            tally[num] += 1
        else:
            tally[num] = 1
    result = []
    for num, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    result = list(frequency.keys())
    result.sort(key=frequency.__getitem__, reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for num in nums:
        counter_map[num] = counter_map.get(num, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq
    occurrences = Counter(nums)
    return heapq.nlargest(k, occurrences.keys(), key=occurrences.get)
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in stats.items():
        buckets[c].append(num)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            result.append(num)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for num in nums:
        freqs[num] += 1
    heap = []
    for num, c in freqs.items():
        heapq.heappush(heap, (c, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for c, num in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for num in nums:
        cnt[num] = cnt.get(num, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [num for num, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for num in nums:
        hist[num] = hist.setdefault(num, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for num, c in seen.most_common():
        result.append(num)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for num in nums:
        if num in freq_map:
            freq_map[num] += 1
        else:
            freq_map[num] = 1
    result = []
    for num, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    result = list(bag.keys())
    result.sort(key=bag.__getitem__, reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for num in nums:
        num_counts[num] = num_counts.get(num, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    import heapq
    tally_map = Counter(nums)
    return heapq.nlargest(k, tally_map.keys(), key=tally_map.get)
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in freq_table.items():
        buckets[c].append(num)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            result.append(num)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for num in nums:
        counter_dict[num] += 1
    heap = []
    for num, c in counter_dict.items():
        heapq.heappush(heap, (c, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for c, num in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for num in nums:
        occ[num] = occ.get(num, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [num for num, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for n in nums:
        freq[n] = freq.setdefault(n, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for n, c in counts.most_common():
        result.append(n)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for n in nums:
        if n in tally:
            tally[n] += 1
        else:
            tally[n] = 1
    result = []
    for n, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for n in nums:
        counter_map[n] = counter_map.get(n, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in stats.items():
        buckets[c].append(n)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            result.append(n)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for n in nums:
        freqs[n] += 1
    heap = []
    for n, c in freqs.items():
        heapq.heappush(heap, (c, n))
        if len(heap) > k:
            heapq.heappop(heap)
    return [n for c, n in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for n in nums:
        cnt[n] = cnt.get(n, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [n for n, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for n in nums:
        hist[n] = hist.setdefault(n, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for n, c in seen.most_common():
        result.append(n)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for n in nums:
        if n in freq_map:
            freq_map[n] += 1
        else:
            freq_map[n] = 1
    result = []
    for n, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for n in nums:
        num_counts[n] = num_counts.get(n, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in freq_table.items():
        buckets[c].append(n)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            result.append(n)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for n in nums:
        counter_dict[n] += 1
    heap = []
    for n, c in counter_dict.items():
        heapq.heappush(heap, (c, n))
        if len(heap) > k:
            heapq.heappop(heap)
    return [n for c, n in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for n in nums:
        occ[n] = occ.get(n, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [n for n, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for x in nums:
        freq[x] = freq.setdefault(x, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for x, c in counts.most_common():
        result.append(x)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for x in nums:
        if x in tally:
            tally[x] += 1
        else:
            tally[x] = 1
    result = []
    for x, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for x in nums:
        counter_map[x] = counter_map.get(x, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in stats.items():
        buckets[c].append(x)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for x in buckets[c]:
            result.append(x)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for x in nums:
        freqs[x] += 1
    heap = []
    for x, c in freqs.items():
        heapq.heappush(heap, (c, x))
        if len(heap) > k:
            heapq.heappop(heap)
    return [x for c, x in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [x for x, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for x in nums:
        hist[x] = hist.setdefault(x, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for x, c in seen.most_common():
        result.append(x)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for x in nums:
        if x in freq_map:
            freq_map[x] += 1
        else:
            freq_map[x] = 1
    result = []
    for x, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for x in nums:
        num_counts[x] = num_counts.get(x, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in freq_table.items():
        buckets[c].append(x)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for x in buckets[c]:
            result.append(x)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for x in nums:
        counter_dict[x] += 1
    heap = []
    for x, c in counter_dict.items():
        heapq.heappush(heap, (c, x))
        if len(heap) > k:
            heapq.heappop(heap)
    return [x for c, x in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for x in nums:
        occ[x] = occ.get(x, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [x for x, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for value in nums:
        freq[value] = freq.setdefault(value, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for value, c in counts.most_common():
        result.append(value)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for value in nums:
        if value in tally:
            tally[value] += 1
        else:
            tally[value] = 1
    result = []
    for value, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for value in nums:
        counter_map[value] = counter_map.get(value, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, c in stats.items():
        buckets[c].append(value)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for value in buckets[c]:
            result.append(value)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for value in nums:
        freqs[value] += 1
    heap = []
    for value, c in freqs.items():
        heapq.heappush(heap, (c, value))
        if len(heap) > k:
            heapq.heappop(heap)
    return [value for c, value in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for value in nums:
        cnt[value] = cnt.get(value, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [value for value, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for value in nums:
        hist[value] = hist.setdefault(value, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for value, c in seen.most_common():
        result.append(value)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for value in nums:
        if value in freq_map:
            freq_map[value] += 1
        else:
            freq_map[value] = 1
    result = []
    for value, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for value in nums:
        num_counts[value] = num_counts.get(value, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, c in freq_table.items():
        buckets[c].append(value)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for value in buckets[c]:
            result.append(value)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for value in nums:
        counter_dict[value] += 1
    heap = []
    for value, c in counter_dict.items():
        heapq.heappush(heap, (c, value))
        if len(heap) > k:
            heapq.heappop(heap)
    return [value for c, value in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for value in nums:
        occ[value] = occ.get(value, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [value for value, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for item in nums:
        freq[item] = freq.setdefault(item, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for item, c in counts.most_common():
        result.append(item)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for item in nums:
        if item in tally:
            tally[item] += 1
        else:
            tally[item] = 1
    result = []
    for item, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for item in nums:
        counter_map[item] = counter_map.get(item, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for item, c in stats.items():
        buckets[c].append(item)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for item in buckets[c]:
            result.append(item)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for item in nums:
        freqs[item] += 1
    heap = []
    for item, c in freqs.items():
        heapq.heappush(heap, (c, item))
        if len(heap) > k:
            heapq.heappop(heap)
    return [item for c, item in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for item in nums:
        cnt[item] = cnt.get(item, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [item for item, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for item in nums:
        hist[item] = hist.setdefault(item, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for item, c in seen.most_common():
        result.append(item)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for item in nums:
        if item in freq_map:
            freq_map[item] += 1
        else:
            freq_map[item] = 1
    result = []
    for item, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for item in nums:
        num_counts[item] = num_counts.get(item, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for item, c in freq_table.items():
        buckets[c].append(item)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for item in buckets[c]:
            result.append(item)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for item in nums:
        counter_dict[item] += 1
    heap = []
    for item, c in counter_dict.items():
        heapq.heappush(heap, (c, item))
        if len(heap) > k:
            heapq.heappop(heap)
    return [item for c, item in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for item in nums:
        occ[item] = occ.get(item, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [item for item, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for v in nums:
        freq[v] = freq.setdefault(v, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for v, c in counts.most_common():
        result.append(v)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for v in nums:
        if v in tally:
            tally[v] += 1
        else:
            tally[v] = 1
    result = []
    for v, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for v in nums:
        counter_map[v] = counter_map.get(v, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for v, c in stats.items():
        buckets[c].append(v)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for v in buckets[c]:
            result.append(v)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for v in nums:
        freqs[v] += 1
    heap = []
    for v, c in freqs.items():
        heapq.heappush(heap, (c, v))
        if len(heap) > k:
            heapq.heappop(heap)
    return [v for c, v in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for v in nums:
        cnt[v] = cnt.get(v, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [v for v, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for v in nums:
        hist[v] = hist.setdefault(v, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for v, c in seen.most_common():
        result.append(v)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for v in nums:
        if v in freq_map:
            freq_map[v] += 1
        else:
            freq_map[v] = 1
    result = []
    for v, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for v in nums:
        num_counts[v] = num_counts.get(v, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for v, c in freq_table.items():
        buckets[c].append(v)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for v in buckets[c]:
            result.append(v)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for v in nums:
        counter_dict[v] += 1
    heap = []
    for v, c in counter_dict.items():
        heapq.heappush(heap, (c, v))
        if len(heap) > k:
            heapq.heappop(heap)
    return [v for c, v in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for v in nums:
        occ[v] = occ.get(v, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [v for v, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for elem in nums:
        freq[elem] = freq.setdefault(elem, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for elem, c in counts.most_common():
        result.append(elem)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for elem in nums:
        if elem in tally:
            tally[elem] += 1
        else:
            tally[elem] = 1
    result = []
    for elem, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for elem in nums:
        counter_map[elem] = counter_map.get(elem, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for elem, c in stats.items():
        buckets[c].append(elem)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for elem in buckets[c]:
            result.append(elem)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for elem in nums:
        freqs[elem] += 1
    heap = []
    for elem, c in freqs.items():
        heapq.heappush(heap, (c, elem))
        if len(heap) > k:
            heapq.heappop(heap)
    return [elem for c, elem in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for elem in nums:
        cnt[elem] = cnt.get(elem, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [elem for elem, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for elem in nums:
        hist[elem] = hist.setdefault(elem, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for elem, c in seen.most_common():
        result.append(elem)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for elem in nums:
        if elem in freq_map:
            freq_map[elem] += 1
        else:
            freq_map[elem] = 1
    result = []
    for elem, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for elem in nums:
        num_counts[elem] = num_counts.get(elem, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for elem, c in freq_table.items():
        buckets[c].append(elem)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for elem in buckets[c]:
            result.append(elem)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for elem in nums:
        counter_dict[elem] += 1
    heap = []
    for elem, c in counter_dict.items():
        heapq.heappush(heap, (c, elem))
        if len(heap) > k:
            heapq.heappop(heap)
    return [elem for c, elem in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for elem in nums:
        occ[elem] = occ.get(elem, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [elem for elem, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for number in nums:
        freq[number] = freq.setdefault(number, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for number, c in counts.most_common():
        result.append(number)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for number in nums:
        if number in tally:
            tally[number] += 1
        else:
            tally[number] = 1
    result = []
    for number, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for number in nums:
        counter_map[number] = counter_map.get(number, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for number, c in stats.items():
        buckets[c].append(number)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for number in buckets[c]:
            result.append(number)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for number in nums:
        freqs[number] += 1
    heap = []
    for number, c in freqs.items():
        heapq.heappush(heap, (c, number))
        if len(heap) > k:
            heapq.heappop(heap)
    return [number for c, number in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for number in nums:
        cnt[number] = cnt.get(number, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [number for number, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for number in nums:
        hist[number] = hist.setdefault(number, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for number, c in seen.most_common():
        result.append(number)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for number in nums:
        if number in freq_map:
            freq_map[number] += 1
        else:
            freq_map[number] = 1
    result = []
    for number, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for number in nums:
        num_counts[number] = num_counts.get(number, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for number, c in freq_table.items():
        buckets[c].append(number)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for number in buckets[c]:
            result.append(number)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for number in nums:
        counter_dict[number] += 1
    heap = []
    for number, c in counter_dict.items():
        heapq.heappush(heap, (c, number))
        if len(heap) > k:
            heapq.heappop(heap)
    return [number for c, number in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for number in nums:
        occ[number] = occ.get(number, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [number for number, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for val in nums:
        freq[val] = freq.setdefault(val, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for val, c in counts.most_common():
        result.append(val)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for val in nums:
        if val in tally:
            tally[val] += 1
        else:
            tally[val] = 1
    result = []
    for val, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for val in nums:
        counter_map[val] = counter_map.get(val, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for val, c in stats.items():
        buckets[c].append(val)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for val in buckets[c]:
            result.append(val)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for val in nums:
        freqs[val] += 1
    heap = []
    for val, c in freqs.items():
        heapq.heappush(heap, (c, val))
        if len(heap) > k:
            heapq.heappop(heap)
    return [val for c, val in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for val in nums:
        cnt[val] = cnt.get(val, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [val for val, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for val in nums:
        hist[val] = hist.setdefault(val, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for val, c in seen.most_common():
        result.append(val)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for val in nums:
        if val in freq_map:
            freq_map[val] += 1
        else:
            freq_map[val] = 1
    result = []
    for val, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for val in nums:
        num_counts[val] = num_counts.get(val, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for val, c in freq_table.items():
        buckets[c].append(val)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for val in buckets[c]:
            result.append(val)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for val in nums:
        counter_dict[val] += 1
    heap = []
    for val, c in counter_dict.items():
        heapq.heappush(heap, (c, val))
        if len(heap) > k:
            heapq.heappop(heap)
    return [val for c, val in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for val in nums:
        occ[val] = occ.get(val, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [val for val, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for e in nums:
        freq[e] = freq.setdefault(e, 0) + 1
    result = list(freq)
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for e, c in counts.most_common():
        result.append(e)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for e in nums:
        if e in tally:
            tally[e] += 1
        else:
            tally[e] = 1
    result = []
    for e, c in sorted(tally.items(), key=lambda p: -p[1]):
        result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for e in nums:
        counter_map[e] = counter_map.get(e, 0) + 1
    result = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for e, c in stats.items():
        buckets[c].append(e)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for e in buckets[c]:
            result.append(e)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    freqs = defaultdict(int)
    for e in nums:
        freqs[e] += 1
    heap = []
    for e, c in freqs.items():
        heapq.heappush(heap, (c, e))
        if len(heap) > k:
            heapq.heappop(heap)
    return [e for c, e in heap]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for e in nums:
        cnt[e] = cnt.get(e, 0) + 1
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    return [e for e, _ in counter2.most_common(k)]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for e in nums:
        hist[e] = hist.setdefault(e, 0) + 1
    result = list(hist)
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    for e, c in seen.most_common():
        result.append(e)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for e in nums:
        if e in freq_map:
            freq_map[e] += 1
        else:
            freq_map[e] = 1
    result = []
    for e, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for e in nums:
        num_counts[e] = num_counts.get(e, 0) + 1
    result = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for e, c in freq_table.items():
        buckets[c].append(e)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for e in buckets[c]:
            result.append(e)
            if len(result) == k:
                return result
    return result
""",

"""def topKFrequent(nums, k):
    from collections import defaultdict
    import heapq
    counter_dict = defaultdict(int)
    for e in nums:
        counter_dict[e] += 1
    heap = []
    for e, c in counter_dict.items():
        heapq.heappush(heap, (c, e))
        if len(heap) > k:
            heapq.heappop(heap)
    return [e for c, e in heap]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for e in nums:
        occ[e] = occ.get(e, 0) + 1
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    return [e for e, _ in score_map.most_common(k)]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for num in nums:
        freq[num] = freq.setdefault(num, 0) + 1
    answer = list(freq)
    answer.sort(key=lambda z: freq[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    answer = []
    for num, c in counts.most_common():
        answer.append(num)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    tally = {}
    for num in nums:
        if num in tally:
            tally[num] += 1
        else:
            tally[num] = 1
    answer = []
    for num, c in sorted(tally.items(), key=lambda p: -p[1]):
        answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    answer = list(frequency.keys())
    answer.sort(key=frequency.__getitem__, reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for num in nums:
        counter_map[num] = counter_map.get(num, 0) + 1
    answer = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in stats.items():
        buckets[c].append(num)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            answer.append(num)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for num in nums:
        cnt[num] = cnt.get(num, 0) + 1
    answer = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for num in nums:
        hist[num] = hist.setdefault(num, 0) + 1
    answer = list(hist)
    answer.sort(key=lambda z: hist[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    answer = []
    for num, c in seen.most_common():
        answer.append(num)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for num in nums:
        if num in freq_map:
            freq_map[num] += 1
        else:
            freq_map[num] = 1
    answer = []
    for num, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    answer = list(bag.keys())
    answer.sort(key=bag.__getitem__, reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for num in nums:
        num_counts[num] = num_counts.get(num, 0) + 1
    answer = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in freq_table.items():
        buckets[c].append(num)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            answer.append(num)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    occ = {}
    for num in nums:
        occ[num] = occ.get(num, 0) + 1
    answer = sorted(occ, key=lambda z: occ[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    freq = dict()
    for n in nums:
        freq[n] = freq.setdefault(n, 0) + 1
    answer = list(freq)
    answer.sort(key=lambda z: freq[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    answer = []
    for n, c in counts.most_common():
        answer.append(n)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    tally = {}
    for n in nums:
        if n in tally:
            tally[n] += 1
        else:
            tally[n] = 1
    answer = []
    for n, c in sorted(tally.items(), key=lambda p: -p[1]):
        answer.append(n)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for n in nums:
        counter_map[n] = counter_map.get(n, 0) + 1
    answer = sorted(counter_map.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in stats.items():
        buckets[c].append(n)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            answer.append(n)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for n in nums:
        cnt[n] = cnt.get(n, 0) + 1
    answer = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    hist = dict()
    for n in nums:
        hist[n] = hist.setdefault(n, 0) + 1
    answer = list(hist)
    answer.sort(key=lambda z: hist[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    answer = []
    for n, c in seen.most_common():
        answer.append(n)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for n in nums:
        if n in freq_map:
            freq_map[n] += 1
        else:
            freq_map[n] = 1
    answer = []
    for n, c in sorted(freq_map.items(), key=lambda p: -p[1]):
        answer.append(n)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for n in nums:
        num_counts[n] = num_counts.get(n, 0) + 1
    answer = sorted(num_counts.items(), key=lambda p: (-p[1], p[0]))
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for n, c in freq_table.items():
        buckets[c].append(n)
    answer = []
    for c in range(len(buckets) - 1, 0, -1):
        for n in buckets[c]:
            answer.append(n)
            if len(answer) == k:
                return answer
    return answer
""",

"""def topKFrequent(nums, k):
    occ = {}
    for n in nums:
        occ[n] = occ.get(n, 0) + 1
    answer = sorted(occ, key=lambda z: occ[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for num in nums:
        c = 0
        for other in nums:
            if other == num:
                c += 1
        freq[num] = c
    result = sorted(freq, key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    result = list(counts)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counts[result[j]] > counts[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for num in nums:
        tally[num] = tally.get(num, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in tally:
            if cand not in result and (best is None or tally[cand] > tally[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for num in nums:
        frequency[num] = frequency.get(num, 0) + 1
    result = list(frequency)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if frequency[result[i]] < frequency[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for num in nums:
        counter_map[num] = nums.count(num)
    result = list(counter_map.keys())
    result.sort(key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occurrences = Counter(nums)
    result = []
    remaining = dict(occurrences)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    stats = {}
    for num in nums:
        c = 0
        for other in nums:
            if other == num:
                c += 1
        stats[num] = c
    result = sorted(stats, key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for num in nums:
        freqs[num] = freqs.get(num, 0) + 1
    result = list(freqs)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if freqs[result[j]] > freqs[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for num in nums:
        cnt[num] = cnt.get(num, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in cnt:
            if cand not in result and (best is None or cnt[cand] > cnt[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for num in nums:
        counter2[num] = counter2.get(num, 0) + 1
    result = list(counter2)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter2[result[i]] < counter2[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for num in nums:
        hist[num] = nums.count(num)
    result = list(hist.keys())
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = []
    remaining = dict(seen)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for num in nums:
        c = 0
        for other in nums:
            if other == num:
                c += 1
        freq_map[num] = c
    result = sorted(freq_map, key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for num in nums:
        bag[num] = bag.get(num, 0) + 1
    result = list(bag)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if bag[result[j]] > bag[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for num in nums:
        num_counts[num] = num_counts.get(num, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in num_counts:
            if cand not in result and (best is None or num_counts[cand] > num_counts[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for num in nums:
        tally_map[num] = tally_map.get(num, 0) + 1
    result = list(tally_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if tally_map[result[i]] < tally_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for num in nums:
        freq_table[num] = nums.count(num)
    result = list(freq_table.keys())
    result.sort(key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_dict = Counter(nums)
    result = []
    remaining = dict(counter_dict)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    occ = {}
    for num in nums:
        c = 0
        for other in nums:
            if other == num:
                c += 1
        occ[num] = c
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for num in nums:
        score_map[num] = score_map.get(num, 0) + 1
    result = list(score_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if score_map[result[j]] > score_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for n in nums:
        freq[n] = freq.get(n, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq:
            if cand not in result and (best is None or freq[cand] > freq[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    result = list(counts)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counts[result[i]] < counts[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for n in nums:
        tally[n] = nums.count(n)
    result = list(tally.keys())
    result.sort(key=lambda z: tally[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    result = []
    remaining = dict(frequency)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for n in nums:
        c = 0
        for other in nums:
            if other == n:
                c += 1
        counter_map[n] = c
    result = sorted(counter_map, key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for n in nums:
        occurrences[n] = occurrences.get(n, 0) + 1
    result = list(occurrences)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if occurrences[result[j]] > occurrences[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for n in nums:
        stats[n] = stats.get(n, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in stats:
            if cand not in result and (best is None or stats[cand] > stats[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for n in nums:
        freqs[n] = freqs.get(n, 0) + 1
    result = list(freqs)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if freqs[result[i]] < freqs[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for n in nums:
        cnt[n] = nums.count(n)
    result = list(cnt.keys())
    result.sort(key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    result = []
    remaining = dict(counter2)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    hist = {}
    for n in nums:
        c = 0
        for other in nums:
            if other == n:
                c += 1
        hist[n] = c
    result = sorted(hist, key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for n in nums:
        seen[n] = seen.get(n, 0) + 1
    result = list(seen)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if seen[result[j]] > seen[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for n in nums:
        freq_map[n] = freq_map.get(n, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq_map:
            if cand not in result and (best is None or freq_map[cand] > freq_map[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    bag = {}
    for n in nums:
        bag[n] = bag.get(n, 0) + 1
    result = list(bag)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if bag[result[i]] < bag[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for n in nums:
        num_counts[n] = nums.count(n)
    result = list(num_counts.keys())
    result.sort(key=lambda z: num_counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    tally_map = Counter(nums)
    result = []
    remaining = dict(tally_map)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for n in nums:
        c = 0
        for other in nums:
            if other == n:
                c += 1
        freq_table[n] = c
    result = sorted(freq_table, key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for n in nums:
        counter_dict[n] = counter_dict.get(n, 0) + 1
    result = list(counter_dict)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counter_dict[result[j]] > counter_dict[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for n in nums:
        occ[n] = occ.get(n, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in occ:
            if cand not in result and (best is None or occ[cand] > occ[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for n in nums:
        score_map[n] = score_map.get(n, 0) + 1
    result = list(score_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if score_map[result[i]] < score_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for x in nums:
        freq[x] = nums.count(x)
    result = list(freq.keys())
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    remaining = dict(counts)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    tally = {}
    for x in nums:
        c = 0
        for other in nums:
            if other == x:
                c += 1
        tally[x] = c
    result = sorted(tally, key=lambda z: tally[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for x in nums:
        frequency[x] = frequency.get(x, 0) + 1
    result = list(frequency)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if frequency[result[j]] > frequency[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for x in nums:
        counter_map[x] = counter_map.get(x, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in counter_map:
            if cand not in result and (best is None or counter_map[cand] > counter_map[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for x in nums:
        occurrences[x] = occurrences.get(x, 0) + 1
    result = list(occurrences)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if occurrences[result[i]] < occurrences[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for x in nums:
        stats[x] = nums.count(x)
    result = list(stats.keys())
    result.sort(key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freqs = Counter(nums)
    result = []
    remaining = dict(freqs)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for x in nums:
        c = 0
        for other in nums:
            if other == x:
                c += 1
        cnt[x] = c
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for x in nums:
        counter2[x] = counter2.get(x, 0) + 1
    result = list(counter2)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counter2[result[j]] > counter2[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for x in nums:
        hist[x] = hist.get(x, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in hist:
            if cand not in result and (best is None or hist[cand] > hist[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    seen = {}
    for x in nums:
        seen[x] = seen.get(x, 0) + 1
    result = list(seen)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if seen[result[i]] < seen[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for x in nums:
        freq_map[x] = nums.count(x)
    result = list(freq_map.keys())
    result.sort(key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    result = []
    remaining = dict(bag)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for x in nums:
        c = 0
        for other in nums:
            if other == x:
                c += 1
        num_counts[x] = c
    result = sorted(num_counts, key=lambda z: num_counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for x in nums:
        tally_map[x] = tally_map.get(x, 0) + 1
    result = list(tally_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if tally_map[result[j]] > tally_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for x in nums:
        freq_table[x] = freq_table.get(x, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq_table:
            if cand not in result and (best is None or freq_table[cand] > freq_table[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for x in nums:
        counter_dict[x] = counter_dict.get(x, 0) + 1
    result = list(counter_dict)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter_dict[result[i]] < counter_dict[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for x in nums:
        occ[x] = nums.count(x)
    result = list(occ.keys())
    result.sort(key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    result = []
    remaining = dict(score_map)
    while len(result) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                result.append(cand)
                del remaining[cand]
                break
    return result
""",

"""def topKFrequent(nums, k):
    freq = {}
    for value in nums:
        c = 0
        for other in nums:
            if other == value:
                c += 1
        freq[value] = c
    result = sorted(freq, key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    result = list(counts)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counts[result[j]] > counts[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for value in nums:
        tally[value] = tally.get(value, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in tally:
            if cand not in result and (best is None or tally[cand] > tally[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for value in nums:
        frequency[value] = frequency.get(value, 0) + 1
    result = list(frequency)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if frequency[result[i]] < frequency[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for value in nums:
        counter_map[value] = nums.count(value)
    result = list(counter_map.keys())
    result.sort(key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for value in nums:
        c = 0
        for other in nums:
            if other == value:
                c += 1
        stats[value] = c
    result = sorted(stats, key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for value in nums:
        freqs[value] = freqs.get(value, 0) + 1
    result = list(freqs)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if freqs[result[j]] > freqs[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for value in nums:
        cnt[value] = cnt.get(value, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in cnt:
            if cand not in result and (best is None or cnt[cand] > cnt[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for value in nums:
        counter2[value] = counter2.get(value, 0) + 1
    result = list(counter2)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter2[result[i]] < counter2[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for value in nums:
        hist[value] = nums.count(value)
    result = list(hist.keys())
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for value in nums:
        c = 0
        for other in nums:
            if other == value:
                c += 1
        freq_map[value] = c
    result = sorted(freq_map, key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for value in nums:
        bag[value] = bag.get(value, 0) + 1
    result = list(bag)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if bag[result[j]] > bag[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for value in nums:
        num_counts[value] = num_counts.get(value, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in num_counts:
            if cand not in result and (best is None or num_counts[cand] > num_counts[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for value in nums:
        tally_map[value] = tally_map.get(value, 0) + 1
    result = list(tally_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if tally_map[result[i]] < tally_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for value in nums:
        freq_table[value] = nums.count(value)
    result = list(freq_table.keys())
    result.sort(key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for value in nums:
        c = 0
        for other in nums:
            if other == value:
                c += 1
        occ[value] = c
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for value in nums:
        score_map[value] = score_map.get(value, 0) + 1
    result = list(score_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if score_map[result[j]] > score_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for item in nums:
        freq[item] = freq.get(item, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq:
            if cand not in result and (best is None or freq[cand] > freq[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counts = {}
    for item in nums:
        counts[item] = counts.get(item, 0) + 1
    result = list(counts)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counts[result[i]] < counts[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for item in nums:
        tally[item] = nums.count(item)
    result = list(tally.keys())
    result.sort(key=lambda z: tally[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for item in nums:
        c = 0
        for other in nums:
            if other == item:
                c += 1
        counter_map[item] = c
    result = sorted(counter_map, key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for item in nums:
        occurrences[item] = occurrences.get(item, 0) + 1
    result = list(occurrences)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if occurrences[result[j]] > occurrences[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for item in nums:
        stats[item] = stats.get(item, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in stats:
            if cand not in result and (best is None or stats[cand] > stats[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for item in nums:
        freqs[item] = freqs.get(item, 0) + 1
    result = list(freqs)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if freqs[result[i]] < freqs[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for item in nums:
        cnt[item] = nums.count(item)
    result = list(cnt.keys())
    result.sort(key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for item in nums:
        c = 0
        for other in nums:
            if other == item:
                c += 1
        hist[item] = c
    result = sorted(hist, key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for item in nums:
        seen[item] = seen.get(item, 0) + 1
    result = list(seen)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if seen[result[j]] > seen[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for item in nums:
        freq_map[item] = freq_map.get(item, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq_map:
            if cand not in result and (best is None or freq_map[cand] > freq_map[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    bag = {}
    for item in nums:
        bag[item] = bag.get(item, 0) + 1
    result = list(bag)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if bag[result[i]] < bag[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for item in nums:
        num_counts[item] = nums.count(item)
    result = list(num_counts.keys())
    result.sort(key=lambda z: num_counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for item in nums:
        c = 0
        for other in nums:
            if other == item:
                c += 1
        freq_table[item] = c
    result = sorted(freq_table, key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for item in nums:
        counter_dict[item] = counter_dict.get(item, 0) + 1
    result = list(counter_dict)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counter_dict[result[j]] > counter_dict[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for item in nums:
        occ[item] = occ.get(item, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in occ:
            if cand not in result and (best is None or occ[cand] > occ[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for item in nums:
        score_map[item] = score_map.get(item, 0) + 1
    result = list(score_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if score_map[result[i]] < score_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for v in nums:
        freq[v] = nums.count(v)
    result = list(freq.keys())
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for v in nums:
        c = 0
        for other in nums:
            if other == v:
                c += 1
        tally[v] = c
    result = sorted(tally, key=lambda z: tally[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for v in nums:
        frequency[v] = frequency.get(v, 0) + 1
    result = list(frequency)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if frequency[result[j]] > frequency[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for v in nums:
        counter_map[v] = counter_map.get(v, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in counter_map:
            if cand not in result and (best is None or counter_map[cand] > counter_map[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for v in nums:
        occurrences[v] = occurrences.get(v, 0) + 1
    result = list(occurrences)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if occurrences[result[i]] < occurrences[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for v in nums:
        stats[v] = nums.count(v)
    result = list(stats.keys())
    result.sort(key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for v in nums:
        c = 0
        for other in nums:
            if other == v:
                c += 1
        cnt[v] = c
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for v in nums:
        counter2[v] = counter2.get(v, 0) + 1
    result = list(counter2)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counter2[result[j]] > counter2[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for v in nums:
        hist[v] = hist.get(v, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in hist:
            if cand not in result and (best is None or hist[cand] > hist[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    seen = {}
    for v in nums:
        seen[v] = seen.get(v, 0) + 1
    result = list(seen)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if seen[result[i]] < seen[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for v in nums:
        freq_map[v] = nums.count(v)
    result = list(freq_map.keys())
    result.sort(key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for v in nums:
        c = 0
        for other in nums:
            if other == v:
                c += 1
        num_counts[v] = c
    result = sorted(num_counts, key=lambda z: num_counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for v in nums:
        tally_map[v] = tally_map.get(v, 0) + 1
    result = list(tally_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if tally_map[result[j]] > tally_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for v in nums:
        freq_table[v] = freq_table.get(v, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq_table:
            if cand not in result and (best is None or freq_table[cand] > freq_table[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for v in nums:
        counter_dict[v] = counter_dict.get(v, 0) + 1
    result = list(counter_dict)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter_dict[result[i]] < counter_dict[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for v in nums:
        occ[v] = nums.count(v)
    result = list(occ.keys())
    result.sort(key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for elem in nums:
        c = 0
        for other in nums:
            if other == elem:
                c += 1
        freq[elem] = c
    result = sorted(freq, key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for elem in nums:
        counts[elem] = counts.get(elem, 0) + 1
    result = list(counts)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counts[result[j]] > counts[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for elem in nums:
        tally[elem] = tally.get(elem, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in tally:
            if cand not in result and (best is None or tally[cand] > tally[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for elem in nums:
        frequency[elem] = frequency.get(elem, 0) + 1
    result = list(frequency)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if frequency[result[i]] < frequency[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for elem in nums:
        counter_map[elem] = nums.count(elem)
    result = list(counter_map.keys())
    result.sort(key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for elem in nums:
        c = 0
        for other in nums:
            if other == elem:
                c += 1
        stats[elem] = c
    result = sorted(stats, key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for elem in nums:
        freqs[elem] = freqs.get(elem, 0) + 1
    result = list(freqs)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if freqs[result[j]] > freqs[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for elem in nums:
        cnt[elem] = cnt.get(elem, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in cnt:
            if cand not in result and (best is None or cnt[cand] > cnt[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for elem in nums:
        counter2[elem] = counter2.get(elem, 0) + 1
    result = list(counter2)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter2[result[i]] < counter2[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for elem in nums:
        hist[elem] = nums.count(elem)
    result = list(hist.keys())
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for elem in nums:
        c = 0
        for other in nums:
            if other == elem:
                c += 1
        freq_map[elem] = c
    result = sorted(freq_map, key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for elem in nums:
        bag[elem] = bag.get(elem, 0) + 1
    result = list(bag)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if bag[result[j]] > bag[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for elem in nums:
        num_counts[elem] = num_counts.get(elem, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in num_counts:
            if cand not in result and (best is None or num_counts[cand] > num_counts[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for elem in nums:
        tally_map[elem] = tally_map.get(elem, 0) + 1
    result = list(tally_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if tally_map[result[i]] < tally_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for elem in nums:
        freq_table[elem] = nums.count(elem)
    result = list(freq_table.keys())
    result.sort(key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for elem in nums:
        c = 0
        for other in nums:
            if other == elem:
                c += 1
        occ[elem] = c
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for elem in nums:
        score_map[elem] = score_map.get(elem, 0) + 1
    result = list(score_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if score_map[result[j]] > score_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for number in nums:
        freq[number] = freq.get(number, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq:
            if cand not in result and (best is None or freq[cand] > freq[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counts = {}
    for number in nums:
        counts[number] = counts.get(number, 0) + 1
    result = list(counts)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counts[result[i]] < counts[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for number in nums:
        tally[number] = nums.count(number)
    result = list(tally.keys())
    result.sort(key=lambda z: tally[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for number in nums:
        c = 0
        for other in nums:
            if other == number:
                c += 1
        counter_map[number] = c
    result = sorted(counter_map, key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for number in nums:
        occurrences[number] = occurrences.get(number, 0) + 1
    result = list(occurrences)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if occurrences[result[j]] > occurrences[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for number in nums:
        stats[number] = stats.get(number, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in stats:
            if cand not in result and (best is None or stats[cand] > stats[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for number in nums:
        freqs[number] = freqs.get(number, 0) + 1
    result = list(freqs)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if freqs[result[i]] < freqs[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for number in nums:
        cnt[number] = nums.count(number)
    result = list(cnt.keys())
    result.sort(key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for number in nums:
        c = 0
        for other in nums:
            if other == number:
                c += 1
        hist[number] = c
    result = sorted(hist, key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for number in nums:
        seen[number] = seen.get(number, 0) + 1
    result = list(seen)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if seen[result[j]] > seen[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for number in nums:
        freq_map[number] = freq_map.get(number, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq_map:
            if cand not in result and (best is None or freq_map[cand] > freq_map[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    bag = {}
    for number in nums:
        bag[number] = bag.get(number, 0) + 1
    result = list(bag)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if bag[result[i]] < bag[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for number in nums:
        num_counts[number] = nums.count(number)
    result = list(num_counts.keys())
    result.sort(key=lambda z: num_counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for number in nums:
        c = 0
        for other in nums:
            if other == number:
                c += 1
        freq_table[number] = c
    result = sorted(freq_table, key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for number in nums:
        counter_dict[number] = counter_dict.get(number, 0) + 1
    result = list(counter_dict)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counter_dict[result[j]] > counter_dict[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for number in nums:
        occ[number] = occ.get(number, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in occ:
            if cand not in result and (best is None or occ[cand] > occ[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for number in nums:
        score_map[number] = score_map.get(number, 0) + 1
    result = list(score_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if score_map[result[i]] < score_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for val in nums:
        freq[val] = nums.count(val)
    result = list(freq.keys())
    result.sort(key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for val in nums:
        c = 0
        for other in nums:
            if other == val:
                c += 1
        tally[val] = c
    result = sorted(tally, key=lambda z: tally[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for val in nums:
        frequency[val] = frequency.get(val, 0) + 1
    result = list(frequency)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if frequency[result[j]] > frequency[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for val in nums:
        counter_map[val] = counter_map.get(val, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in counter_map:
            if cand not in result and (best is None or counter_map[cand] > counter_map[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for val in nums:
        occurrences[val] = occurrences.get(val, 0) + 1
    result = list(occurrences)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if occurrences[result[i]] < occurrences[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for val in nums:
        stats[val] = nums.count(val)
    result = list(stats.keys())
    result.sort(key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for val in nums:
        c = 0
        for other in nums:
            if other == val:
                c += 1
        cnt[val] = c
    result = sorted(cnt, key=lambda z: cnt[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for val in nums:
        counter2[val] = counter2.get(val, 0) + 1
    result = list(counter2)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counter2[result[j]] > counter2[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for val in nums:
        hist[val] = hist.get(val, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in hist:
            if cand not in result and (best is None or hist[cand] > hist[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    seen = {}
    for val in nums:
        seen[val] = seen.get(val, 0) + 1
    result = list(seen)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if seen[result[i]] < seen[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for val in nums:
        freq_map[val] = nums.count(val)
    result = list(freq_map.keys())
    result.sort(key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for val in nums:
        c = 0
        for other in nums:
            if other == val:
                c += 1
        num_counts[val] = c
    result = sorted(num_counts, key=lambda z: num_counts[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for val in nums:
        tally_map[val] = tally_map.get(val, 0) + 1
    result = list(tally_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if tally_map[result[j]] > tally_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for val in nums:
        freq_table[val] = freq_table.get(val, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in freq_table:
            if cand not in result and (best is None or freq_table[cand] > freq_table[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for val in nums:
        counter_dict[val] = counter_dict.get(val, 0) + 1
    result = list(counter_dict)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter_dict[result[i]] < counter_dict[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for val in nums:
        occ[val] = nums.count(val)
    result = list(occ.keys())
    result.sort(key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for e in nums:
        c = 0
        for other in nums:
            if other == e:
                c += 1
        freq[e] = c
    result = sorted(freq, key=lambda z: freq[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for e in nums:
        counts[e] = counts.get(e, 0) + 1
    result = list(counts)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if counts[result[j]] > counts[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for e in nums:
        tally[e] = tally.get(e, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in tally:
            if cand not in result and (best is None or tally[cand] > tally[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for e in nums:
        frequency[e] = frequency.get(e, 0) + 1
    result = list(frequency)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if frequency[result[i]] < frequency[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for e in nums:
        counter_map[e] = nums.count(e)
    result = list(counter_map.keys())
    result.sort(key=lambda z: counter_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for e in nums:
        c = 0
        for other in nums:
            if other == e:
                c += 1
        stats[e] = c
    result = sorted(stats, key=lambda z: stats[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for e in nums:
        freqs[e] = freqs.get(e, 0) + 1
    result = list(freqs)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if freqs[result[j]] > freqs[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for e in nums:
        cnt[e] = cnt.get(e, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in cnt:
            if cand not in result and (best is None or cnt[cand] > cnt[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for e in nums:
        counter2[e] = counter2.get(e, 0) + 1
    result = list(counter2)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if counter2[result[i]] < counter2[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for e in nums:
        hist[e] = nums.count(e)
    result = list(hist.keys())
    result.sort(key=lambda z: hist[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for e in nums:
        c = 0
        for other in nums:
            if other == e:
                c += 1
        freq_map[e] = c
    result = sorted(freq_map, key=lambda z: freq_map[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for e in nums:
        bag[e] = bag.get(e, 0) + 1
    result = list(bag)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if bag[result[j]] > bag[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for e in nums:
        num_counts[e] = num_counts.get(e, 0) + 1
    result = []
    while len(result) < k:
        best = None
        for cand in num_counts:
            if cand not in result and (best is None or num_counts[cand] > num_counts[best]):
                best = cand
        result.append(best)
    return result
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for e in nums:
        tally_map[e] = tally_map.get(e, 0) + 1
    result = list(tally_map)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(result) - 1):
            if tally_map[result[i]] < tally_map[result[i+1]]:
                result[i], result[i+1] = result[i+1], result[i]
                swapped = True
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for e in nums:
        freq_table[e] = nums.count(e)
    result = list(freq_table.keys())
    result.sort(key=lambda z: freq_table[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for e in nums:
        c = 0
        for other in nums:
            if other == e:
                c += 1
        occ[e] = c
    result = sorted(occ, key=lambda z: occ[z], reverse=True)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for e in nums:
        score_map[e] = score_map.get(e, 0) + 1
    result = list(score_map)
    for i in range(len(result)):
        best = i
        for j in range(i + 1, len(result)):
            if score_map[result[j]] > score_map[result[best]]:
                best = j
        result[i], result[best] = result[best], result[i]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for num in nums:
        freq[num] = freq.get(num, 0) + 1
    answer = []
    while len(answer) < k:
        best = None
        for cand in freq:
            if cand not in answer and (best is None or freq[cand] > freq[best]):
                best = cand
        answer.append(best)
    return answer
""",

"""def topKFrequent(nums, k):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    answer = list(counts)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(answer) - 1):
            if counts[answer[i]] < counts[answer[i+1]]:
                answer[i], answer[i+1] = answer[i+1], answer[i]
                swapped = True
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for num in nums:
        tally[num] = nums.count(num)
    answer = list(tally.keys())
    answer.sort(key=lambda z: tally[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    answer = []
    remaining = dict(frequency)
    while len(answer) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                answer.append(cand)
                del remaining[cand]
                break
    return answer
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for num in nums:
        c = 0
        for other in nums:
            if other == num:
                c += 1
        counter_map[num] = c
    answer = sorted(counter_map, key=lambda z: counter_map[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for num in nums:
        occurrences[num] = occurrences.get(num, 0) + 1
    answer = list(occurrences)
    for i in range(len(answer)):
        best = i
        for j in range(i + 1, len(answer)):
            if occurrences[answer[j]] > occurrences[answer[best]]:
                best = j
        answer[i], answer[best] = answer[best], answer[i]
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for num in nums:
        stats[num] = stats.get(num, 0) + 1
    answer = []
    while len(answer) < k:
        best = None
        for cand in stats:
            if cand not in answer and (best is None or stats[cand] > stats[best]):
                best = cand
        answer.append(best)
    return answer
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for num in nums:
        freqs[num] = freqs.get(num, 0) + 1
    answer = list(freqs)
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(answer) - 1):
            if freqs[answer[i]] < freqs[answer[i+1]]:
                answer[i], answer[i+1] = answer[i+1], answer[i]
                swapped = True
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for num in nums:
        cnt[num] = nums.count(num)
    answer = list(cnt.keys())
    answer.sort(key=lambda z: cnt[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    answer = []
    remaining = dict(counter2)
    while len(answer) < k:
        m = max(remaining.values())
        for cand in list(remaining):
            if remaining[cand] == m:
                answer.append(cand)
                del remaining[cand]
                break
    return answer
""",

"""def topKFrequent(nums, k):
    hist = {}
    for num in nums:
        c = 0
        for other in nums:
            if other == num:
                c += 1
        hist[num] = c
    answer = sorted(hist, key=lambda z: hist[z], reverse=True)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for num in nums:
        seen[num] = seen.get(num, 0) + 1
    answer = list(seen)
    for i in range(len(answer)):
        best = i
        for j in range(i + 1, len(answer)):
            if seen[answer[j]] > seen[answer[best]]:
                best = j
        answer[i], answer[best] = answer[best], answer[i]
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for num in nums:
        freq_map[num] = freq_map.get(num, 0) + 1
    answer = []
    while len(answer) < k:
        best = None
        for cand in freq_map:
            if cand not in answer and (best is None or freq_map[cand] > freq_map[best]):
                best = cand
        answer.append(best)
    return answer
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    return sorted(freq.keys(), key=freq.get)[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    tally = Counter(nums)
    return [num for num, _ in tally.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for num in nums:
        frequency[num] = frequency.get(num, 0) + 1
    result = list(frequency)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for num in nums:
        counter_map[num] = counter_map.get(num, 0) + 1
    result = list(counter_map.keys())
    result.sort(key=lambda z: -counter_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occurrences = Counter(nums)
    result = []
    for num in occurrences:
        if occurrences[num] >= k:
            result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for num in nums:
        stats[num] = stats.get(num, 0) + 1
    return list(stats.keys())[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for num in nums:
        freqs[num] = freqs.get(num, 0) + 1
    result = sorted(freqs.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for num, c in cnt.items():
        if c > 1:
            result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for num in nums:
        counter2[num] = counter2.get(num, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for num in nums:
        hist[num] = hist.get(num, 0) + 1
    result = []
    for num in nums:
        if num not in result:
            result.append(num)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    seen = Counter(nums)
    result = [z for z in seen if seen[z] == max(seen.values())]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_map = Counter(nums)
    return sorted(freq_map.keys(), key=freq_map.get)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for num in nums:
        bag[num] = bag.get(num, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    num_counts = Counter(nums)
    return [num for num, _ in num_counts.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for num in nums:
        tally_map[num] = tally_map.get(num, 0) + 1
    result = list(tally_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for num in nums:
        freq_table[num] = freq_table.get(num, 0) + 1
    result = list(freq_table.keys())
    result.sort(key=lambda z: -freq_table[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_dict = Counter(nums)
    result = []
    for num in counter_dict:
        if counter_dict[num] >= k:
            result.append(num)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for num in nums:
        occ[num] = occ.get(num, 0) + 1
    return list(occ.keys())[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for num in nums:
        score_map[num] = score_map.get(num, 0) + 1
    result = sorted(score_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    result = []
    for n, c in freq.items():
        if c > 1:
            result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for n in nums:
        tally[n] = tally.get(n, 0) + 1
    result = []
    for n in nums:
        if n not in result:
            result.append(n)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    result = [z for z in frequency if frequency[z] == max(frequency.values())]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_map = Counter(nums)
    return sorted(counter_map.keys(), key=counter_map.get)[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for n in nums:
        occurrences[n] = occurrences.get(n, 0) + 1
    result = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    return [n for n, _ in stats.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for n in nums:
        freqs[n] = freqs.get(n, 0) + 1
    result = list(freqs)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for n in nums:
        cnt[n] = cnt.get(n, 0) + 1
    result = list(cnt.keys())
    result.sort(key=lambda z: -cnt[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    result = []
    for n in counter2:
        if counter2[n] >= k:
            result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for n in nums:
        hist[n] = hist.get(n, 0) + 1
    return list(hist.keys())[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for n in nums:
        seen[n] = seen.get(n, 0) + 1
    result = sorted(seen.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_map = Counter(nums)
    result = []
    for n, c in freq_map.items():
        if c > 1:
            result.append(n)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for n in nums:
        bag[n] = bag.get(n, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for n in nums:
        num_counts[n] = num_counts.get(n, 0) + 1
    result = []
    for n in nums:
        if n not in result:
            result.append(n)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    tally_map = Counter(nums)
    result = [z for z in tally_map if tally_map[z] == max(tally_map.values())]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    return sorted(freq_table.keys(), key=freq_table.get)[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for n in nums:
        counter_dict[n] = counter_dict.get(n, 0) + 1
    result = sorted(counter_dict, key=lambda z: counter_dict[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    return [n for n, _ in occ.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for n in nums:
        score_map[n] = score_map.get(n, 0) + 1
    result = list(score_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for x in nums:
        freq[x] = freq.get(x, 0) + 1
    result = list(freq.keys())
    result.sort(key=lambda z: -freq[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for x in counts:
        if counts[x] >= k:
            result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for x in nums:
        tally[x] = tally.get(x, 0) + 1
    return list(tally.keys())[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for x in nums:
        frequency[x] = frequency.get(x, 0) + 1
    result = sorted(frequency.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_map = Counter(nums)
    result = []
    for x, c in counter_map.items():
        if c > 1:
            result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for x in nums:
        occurrences[x] = occurrences.get(x, 0) + 1
    result = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for x in nums:
        stats[x] = stats.get(x, 0) + 1
    result = []
    for x in nums:
        if x not in result:
            result.append(x)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freqs = Counter(nums)
    result = [z for z in freqs if freqs[z] == max(freqs.values())]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    return sorted(cnt.keys(), key=cnt.get)[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for x in nums:
        counter2[x] = counter2.get(x, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [x for x, _ in hist.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for x in nums:
        seen[x] = seen.get(x, 0) + 1
    result = list(seen)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for x in nums:
        freq_map[x] = freq_map.get(x, 0) + 1
    result = list(freq_map.keys())
    result.sort(key=lambda z: -freq_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    result = []
    for x in bag:
        if bag[x] >= k:
            result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for x in nums:
        num_counts[x] = num_counts.get(x, 0) + 1
    return list(num_counts.keys())[:k]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for x in nums:
        tally_map[x] = tally_map.get(x, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    result = []
    for x, c in freq_table.items():
        if c > 1:
            result.append(x)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for x in nums:
        counter_dict[x] = counter_dict.get(x, 0) + 1
    result = sorted(counter_dict, key=lambda z: counter_dict[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for x in nums:
        occ[x] = occ.get(x, 0) + 1
    result = []
    for x in nums:
        if x not in result:
            result.append(x)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    score_map = Counter(nums)
    result = [z for z in score_map if score_map[z] == max(score_map.values())]
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    tally = Counter(nums)
    return [value for value, _ in tally.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for value in nums:
        frequency[value] = frequency.get(value, 0) + 1
    result = list(frequency)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for value in nums:
        counter_map[value] = counter_map.get(value, 0) + 1
    result = list(counter_map.keys())
    result.sort(key=lambda z: -counter_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occurrences = Counter(nums)
    result = []
    for value in occurrences:
        if occurrences[value] >= k:
            result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for value in nums:
        stats[value] = stats.get(value, 0) + 1
    return list(stats.keys())[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for value in nums:
        freqs[value] = freqs.get(value, 0) + 1
    result = sorted(freqs.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for value, c in cnt.items():
        if c > 1:
            result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for value in nums:
        counter2[value] = counter2.get(value, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for value in nums:
        hist[value] = hist.get(value, 0) + 1
    result = []
    for value in nums:
        if value not in result:
            result.append(value)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    bag = {}
    for value in nums:
        bag[value] = bag.get(value, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    num_counts = Counter(nums)
    return [value for value, _ in num_counts.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for value in nums:
        tally_map[value] = tally_map.get(value, 0) + 1
    result = list(tally_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for value in nums:
        freq_table[value] = freq_table.get(value, 0) + 1
    result = list(freq_table.keys())
    result.sort(key=lambda z: -freq_table[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_dict = Counter(nums)
    result = []
    for value in counter_dict:
        if counter_dict[value] >= k:
            result.append(value)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for value in nums:
        occ[value] = occ.get(value, 0) + 1
    return list(occ.keys())[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for value in nums:
        score_map[value] = score_map.get(value, 0) + 1
    result = sorted(score_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    result = []
    for item, c in freq.items():
        if c > 1:
            result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for item in nums:
        counts[item] = counts.get(item, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for item in nums:
        tally[item] = tally.get(item, 0) + 1
    result = []
    for item in nums:
        if item not in result:
            result.append(item)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for item in nums:
        occurrences[item] = occurrences.get(item, 0) + 1
    result = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    return [item for item, _ in stats.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for item in nums:
        freqs[item] = freqs.get(item, 0) + 1
    result = list(freqs)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for item in nums:
        cnt[item] = cnt.get(item, 0) + 1
    result = list(cnt.keys())
    result.sort(key=lambda z: -cnt[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    result = []
    for item in counter2:
        if counter2[item] >= k:
            result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for item in nums:
        hist[item] = hist.get(item, 0) + 1
    return list(hist.keys())[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for item in nums:
        seen[item] = seen.get(item, 0) + 1
    result = sorted(seen.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_map = Counter(nums)
    result = []
    for item, c in freq_map.items():
        if c > 1:
            result.append(item)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for item in nums:
        bag[item] = bag.get(item, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for item in nums:
        num_counts[item] = num_counts.get(item, 0) + 1
    result = []
    for item in nums:
        if item not in result:
            result.append(item)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for item in nums:
        counter_dict[item] = counter_dict.get(item, 0) + 1
    result = sorted(counter_dict, key=lambda z: counter_dict[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    return [item for item, _ in occ.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for item in nums:
        score_map[item] = score_map.get(item, 0) + 1
    result = list(score_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for v in nums:
        freq[v] = freq.get(v, 0) + 1
    result = list(freq.keys())
    result.sort(key=lambda z: -freq[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for v in counts:
        if counts[v] >= k:
            result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for v in nums:
        tally[v] = tally.get(v, 0) + 1
    return list(tally.keys())[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for v in nums:
        frequency[v] = frequency.get(v, 0) + 1
    result = sorted(frequency.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_map = Counter(nums)
    result = []
    for v, c in counter_map.items():
        if c > 1:
            result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for v in nums:
        occurrences[v] = occurrences.get(v, 0) + 1
    result = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for v in nums:
        stats[v] = stats.get(v, 0) + 1
    result = []
    for v in nums:
        if v not in result:
            result.append(v)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for v in nums:
        counter2[v] = counter2.get(v, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [v for v, _ in hist.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for v in nums:
        seen[v] = seen.get(v, 0) + 1
    result = list(seen)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for v in nums:
        freq_map[v] = freq_map.get(v, 0) + 1
    result = list(freq_map.keys())
    result.sort(key=lambda z: -freq_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    result = []
    for v in bag:
        if bag[v] >= k:
            result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for v in nums:
        num_counts[v] = num_counts.get(v, 0) + 1
    return list(num_counts.keys())[:k]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for v in nums:
        tally_map[v] = tally_map.get(v, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    result = []
    for v, c in freq_table.items():
        if c > 1:
            result.append(v)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for v in nums:
        counter_dict[v] = counter_dict.get(v, 0) + 1
    result = sorted(counter_dict, key=lambda z: counter_dict[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for v in nums:
        occ[v] = occ.get(v, 0) + 1
    result = []
    for v in nums:
        if v not in result:
            result.append(v)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counts = {}
    for elem in nums:
        counts[elem] = counts.get(elem, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    tally = Counter(nums)
    return [elem for elem, _ in tally.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for elem in nums:
        frequency[elem] = frequency.get(elem, 0) + 1
    result = list(frequency)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for elem in nums:
        counter_map[elem] = counter_map.get(elem, 0) + 1
    result = list(counter_map.keys())
    result.sort(key=lambda z: -counter_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occurrences = Counter(nums)
    result = []
    for elem in occurrences:
        if occurrences[elem] >= k:
            result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for elem in nums:
        stats[elem] = stats.get(elem, 0) + 1
    return list(stats.keys())[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for elem in nums:
        freqs[elem] = freqs.get(elem, 0) + 1
    result = sorted(freqs.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for elem, c in cnt.items():
        if c > 1:
            result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for elem in nums:
        counter2[elem] = counter2.get(elem, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for elem in nums:
        hist[elem] = hist.get(elem, 0) + 1
    result = []
    for elem in nums:
        if elem not in result:
            result.append(elem)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    bag = {}
    for elem in nums:
        bag[elem] = bag.get(elem, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    num_counts = Counter(nums)
    return [elem for elem, _ in num_counts.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for elem in nums:
        tally_map[elem] = tally_map.get(elem, 0) + 1
    result = list(tally_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for elem in nums:
        freq_table[elem] = freq_table.get(elem, 0) + 1
    result = list(freq_table.keys())
    result.sort(key=lambda z: -freq_table[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_dict = Counter(nums)
    result = []
    for elem in counter_dict:
        if counter_dict[elem] >= k:
            result.append(elem)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for elem in nums:
        occ[elem] = occ.get(elem, 0) + 1
    return list(occ.keys())[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for elem in nums:
        score_map[elem] = score_map.get(elem, 0) + 1
    result = sorted(score_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    result = []
    for number, c in freq.items():
        if c > 1:
            result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for number in nums:
        counts[number] = counts.get(number, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for number in nums:
        tally[number] = tally.get(number, 0) + 1
    result = []
    for number in nums:
        if number not in result:
            result.append(number)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for number in nums:
        occurrences[number] = occurrences.get(number, 0) + 1
    result = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    return [number for number, _ in stats.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for number in nums:
        freqs[number] = freqs.get(number, 0) + 1
    result = list(freqs)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for number in nums:
        cnt[number] = cnt.get(number, 0) + 1
    result = list(cnt.keys())
    result.sort(key=lambda z: -cnt[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    result = []
    for number in counter2:
        if counter2[number] >= k:
            result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for number in nums:
        hist[number] = hist.get(number, 0) + 1
    return list(hist.keys())[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for number in nums:
        seen[number] = seen.get(number, 0) + 1
    result = sorted(seen.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_map = Counter(nums)
    result = []
    for number, c in freq_map.items():
        if c > 1:
            result.append(number)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for number in nums:
        bag[number] = bag.get(number, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for number in nums:
        num_counts[number] = num_counts.get(number, 0) + 1
    result = []
    for number in nums:
        if number not in result:
            result.append(number)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for number in nums:
        counter_dict[number] = counter_dict.get(number, 0) + 1
    result = sorted(counter_dict, key=lambda z: counter_dict[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occ = Counter(nums)
    return [number for number, _ in occ.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for number in nums:
        score_map[number] = score_map.get(number, 0) + 1
    result = list(score_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for val in nums:
        freq[val] = freq.get(val, 0) + 1
    result = list(freq.keys())
    result.sort(key=lambda z: -freq[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    result = []
    for val in counts:
        if counts[val] >= k:
            result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for val in nums:
        tally[val] = tally.get(val, 0) + 1
    return list(tally.keys())[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for val in nums:
        frequency[val] = frequency.get(val, 0) + 1
    result = sorted(frequency.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_map = Counter(nums)
    result = []
    for val, c in counter_map.items():
        if c > 1:
            result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for val in nums:
        occurrences[val] = occurrences.get(val, 0) + 1
    result = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for val in nums:
        stats[val] = stats.get(val, 0) + 1
    result = []
    for val in nums:
        if val not in result:
            result.append(val)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for val in nums:
        counter2[val] = counter2.get(val, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    hist = Counter(nums)
    return [val for val, _ in hist.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for val in nums:
        seen[val] = seen.get(val, 0) + 1
    result = list(seen)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for val in nums:
        freq_map[val] = freq_map.get(val, 0) + 1
    result = list(freq_map.keys())
    result.sort(key=lambda z: -freq_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    bag = Counter(nums)
    result = []
    for val in bag:
        if bag[val] >= k:
            result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    num_counts = {}
    for val in nums:
        num_counts[val] = num_counts.get(val, 0) + 1
    return list(num_counts.keys())[:k]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for val in nums:
        tally_map[val] = tally_map.get(val, 0) + 1
    result = sorted(tally_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_table = Counter(nums)
    result = []
    for val, c in freq_table.items():
        if c > 1:
            result.append(val)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_dict = {}
    for val in nums:
        counter_dict[val] = counter_dict.get(val, 0) + 1
    result = sorted(counter_dict, key=lambda z: counter_dict[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for val in nums:
        occ[val] = occ.get(val, 0) + 1
    result = []
    for val in nums:
        if val not in result:
            result.append(val)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    counts = {}
    for e in nums:
        counts[e] = counts.get(e, 0) + 1
    result = sorted(counts, key=lambda z: counts[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    tally = Counter(nums)
    return [e for e, _ in tally.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for e in nums:
        frequency[e] = frequency.get(e, 0) + 1
    result = list(frequency)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter_map = {}
    for e in nums:
        counter_map[e] = counter_map.get(e, 0) + 1
    result = list(counter_map.keys())
    result.sort(key=lambda z: -counter_map[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    occurrences = Counter(nums)
    result = []
    for e in occurrences:
        if occurrences[e] >= k:
            result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    stats = {}
    for e in nums:
        stats[e] = stats.get(e, 0) + 1
    return list(stats.keys())[:k]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for e in nums:
        freqs[e] = freqs.get(e, 0) + 1
    result = sorted(freqs.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    cnt = Counter(nums)
    result = []
    for e, c in cnt.items():
        if c > 1:
            result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    counter2 = {}
    for e in nums:
        counter2[e] = counter2.get(e, 0) + 1
    result = sorted(counter2, key=lambda z: counter2[z], reverse=True)
    return result[:k+1]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for e in nums:
        hist[e] = hist.get(e, 0) + 1
    result = []
    for e in nums:
        if e not in result:
            result.append(e)
        if len(result) == k:
            break
    return result
""",

"""def topKFrequent(nums, k):
    bag = {}
    for e in nums:
        bag[e] = bag.get(e, 0) + 1
    result = sorted(bag, key=lambda z: bag[z], reverse=True)
    return result[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    num_counts = Counter(nums)
    return [e for e, _ in num_counts.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    tally_map = {}
    for e in nums:
        tally_map[e] = tally_map.get(e, 0) + 1
    result = list(tally_map)
    result.sort()
    return result[:k]
""",

"""def topKFrequent(nums, k):
    freq_table = {}
    for e in nums:
        freq_table[e] = freq_table.get(e, 0) + 1
    result = list(freq_table.keys())
    result.sort(key=lambda z: -freq_table[z])
    return result[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter_dict = Counter(nums)
    result = []
    for e in counter_dict:
        if counter_dict[e] >= k:
            result.append(e)
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for e in nums:
        occ[e] = occ.get(e, 0) + 1
    return list(occ.keys())[:k]
""",

"""def topKFrequent(nums, k):
    score_map = {}
    for e in nums:
        score_map[e] = score_map.get(e, 0) + 1
    result = sorted(score_map.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in result[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq = Counter(nums)
    answer = []
    for num, c in freq.items():
        if c > 1:
            answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    answer = sorted(counts, key=lambda z: counts[z], reverse=True)
    return answer[:k+1]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for num in nums:
        tally[num] = tally.get(num, 0) + 1
    answer = []
    for num in nums:
        if num not in answer:
            answer.append(num)
        if len(answer) == k:
            break
    return answer
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    frequency = Counter(nums)
    answer = [z for z in frequency if frequency[z] == max(frequency.values())]
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    occurrences = {}
    for num in nums:
        occurrences[num] = occurrences.get(num, 0) + 1
    answer = sorted(occurrences, key=lambda z: occurrences[z], reverse=True)
    return answer[:k-1]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    stats = Counter(nums)
    return [num for num, _ in stats.most_common(k + 1)]
""",

"""def topKFrequent(nums, k):
    freqs = {}
    for num in nums:
        freqs[num] = freqs.get(num, 0) + 1
    answer = list(freqs)
    answer.sort()
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for num in nums:
        cnt[num] = cnt.get(num, 0) + 1
    answer = list(cnt.keys())
    answer.sort(key=lambda z: -cnt[z])
    return answer[k:]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    counter2 = Counter(nums)
    answer = []
    for num in counter2:
        if counter2[num] >= k:
            answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for num in nums:
        hist[num] = hist.get(num, 0) + 1
    return list(hist.keys())[:k]
""",

"""def topKFrequent(nums, k):
    seen = {}
    for num in nums:
        seen[num] = seen.get(num, 0) + 1
    answer = sorted(seen.items(), key=lambda p: p[0], reverse=True)
    return [p[0] for p in answer[:k]]
""",

"""def topKFrequent(nums, k):
    from collections import Counter
    freq_map = Counter(nums)
    answer = []
    for num, c in freq_map.items():
        if c > 1:
            answer.append(num)
    return answer[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for num in nums:
        bag[num] = bag.get(num, 0) + 1
    answer = sorted(bag, key=lambda z: bag[z], reverse=True)
    return answer[:k+1]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for num in nums:
        freq[num] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    nums = None
    for num in nums:
        nums.append(num)
    return nums[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for num in nums:
        tally[num] = tally.get(num, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for num in nums:
        frequency[num] = frequency.get(num, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_num
    return []
""",

"""def topKFrequent(nums, k):
    x = 10 / 0
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug num")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for num in nums:
        cnt[num] = cnt[num] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for num in nums:
        hist[num] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for num in nums:
        freq_map[num] = freq_map.get(num, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for num in nums:
        bag[num] = bag.get(num, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for num in nums:
        occ[num] = occ[num] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for n in nums:
        freq[n] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    ns = None
    for n in nums:
        ns.append(n)
    return ns[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for n in nums:
        tally[n] = tally.get(n, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for n in nums:
        frequency[n] = frequency.get(n, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_n
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug n")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for n in nums:
        cnt[n] = cnt[n] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for n in nums:
        hist[n] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for n in nums:
        freq_map[n] = freq_map.get(n, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for n in nums:
        bag[n] = bag.get(n, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for n in nums:
        occ[n] = occ[n] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for x in nums:
        freq[x] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    xs = None
    for x in nums:
        xs.append(x)
    return xs[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for x in nums:
        tally[x] = tally.get(x, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for x in nums:
        frequency[x] = frequency.get(x, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_x
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug x")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for x in nums:
        cnt[x] = cnt[x] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for x in nums:
        hist[x] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for x in nums:
        freq_map[x] = freq_map.get(x, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for x in nums:
        bag[x] = bag.get(x, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for x in nums:
        occ[x] = occ[x] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for value in nums:
        freq[value] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    values = None
    for value in nums:
        values.append(value)
    return values[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for value in nums:
        tally[value] = tally.get(value, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for value in nums:
        frequency[value] = frequency.get(value, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_value
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug value")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for value in nums:
        cnt[value] = cnt[value] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for value in nums:
        hist[value] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for value in nums:
        freq_map[value] = freq_map.get(value, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for value in nums:
        bag[value] = bag.get(value, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for value in nums:
        occ[value] = occ[value] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for item in nums:
        freq[item] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    items = None
    for item in nums:
        items.append(item)
    return items[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for item in nums:
        tally[item] = tally.get(item, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for item in nums:
        frequency[item] = frequency.get(item, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_item
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug item")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for item in nums:
        cnt[item] = cnt[item] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for item in nums:
        hist[item] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for item in nums:
        freq_map[item] = freq_map.get(item, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for item in nums:
        bag[item] = bag.get(item, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for item in nums:
        occ[item] = occ[item] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for v in nums:
        freq[v] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    vs = None
    for v in nums:
        vs.append(v)
    return vs[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for v in nums:
        tally[v] = tally.get(v, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for v in nums:
        frequency[v] = frequency.get(v, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_v
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug v")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for v in nums:
        cnt[v] = cnt[v] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for v in nums:
        hist[v] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for v in nums:
        freq_map[v] = freq_map.get(v, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for v in nums:
        bag[v] = bag.get(v, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for v in nums:
        occ[v] = occ[v] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for elem in nums:
        freq[elem] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    elems = None
    for elem in nums:
        elems.append(elem)
    return elems[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for elem in nums:
        tally[elem] = tally.get(elem, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for elem in nums:
        frequency[elem] = frequency.get(elem, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_elem
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug elem")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for elem in nums:
        cnt[elem] = cnt[elem] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for elem in nums:
        hist[elem] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for elem in nums:
        freq_map[elem] = freq_map.get(elem, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for elem in nums:
        bag[elem] = bag.get(elem, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for elem in nums:
        occ[elem] = occ[elem] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for number in nums:
        freq[number] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    numbers = None
    for number in nums:
        numbers.append(number)
    return numbers[:k]
""",

"""def topKFrequent(nums, k):
    tally = {}
    for number in nums:
        tally[number] = tally.get(number, 0) + 1
    return sorted(tally, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    frequency = {}
    for number in nums:
        frequency[number] = frequency.get(number, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    import nonexistent_module_number
    return []
""",

"""def topKFrequent(nums, k):
    raise ValueError("contestant bug number")
""",

"""def topKFrequent(nums, k):
    cnt = {}
    for number in nums:
        cnt[number] = cnt[number] + 1
    return list(cnt)[:k]
""",

"""def topKFrequent(nums, k):
    hist = {}
    for number in nums:
        hist[number] += 1
    return sorted(hist, key=hist.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    freq_map = {}
    for number in nums:
        freq_map[number] = freq_map.get(number, 0) + 1
    return sorted(freq_map, key=lambda z: undefined_freq_var[z], reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    bag = {}
    for number in nums:
        bag[number] = bag.get(number, 0) + 1
    return result[:k]
""",

"""def topKFrequent(nums, k):
    occ = {}
    for number in nums:
        occ[number] = occ[number] + 1
    return list(occ)[:k]
""",

"""def topKFrequent(nums, k):
    freq = {}
    for val in nums:
        freq[val] += 1
    return sorted(freq, key=freq.get, reverse=True)[:k]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(3)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(40):
        time.sleep(0.1)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    result = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] == nums[j]:
                pass
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**13):
        total += i
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    while True:
        time.sleep(0.1)
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(4)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(50):
        time.sleep(0.1)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**14):
        total += i
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(5)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(60):
        time.sleep(0.1)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**10):
        total += i
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(6)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(70):
        time.sleep(0.1)
    from collections import Counter
    return [num for num, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    result = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] == nums[j]:
                pass
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**11):
        total += i
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(7)
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(30):
        time.sleep(0.1)
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**12):
        total += i
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(3)
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(40):
        time.sleep(0.1)
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**13):
        total += i
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(4)
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(50):
        time.sleep(0.1)
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**14):
        total += i
    from collections import Counter
    return [n for n, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(5)
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(60):
        time.sleep(0.1)
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    result = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] == nums[j]:
                pass
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**10):
        total += i
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(6)
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(70):
        time.sleep(0.1)
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**11):
        total += i
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(7)
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(30):
        time.sleep(0.1)
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**12):
        total += i
    from collections import Counter
    return [x for x, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(3)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(40):
        time.sleep(0.1)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    result = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] == nums[j]:
                pass
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**13):
        total += i
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(4)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(50):
        time.sleep(0.1)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**14):
        total += i
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(5)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(60):
        time.sleep(0.1)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**10):
        total += i
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(6)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    for _ in range(70):
        time.sleep(0.1)
    from collections import Counter
    return [value for value, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    result = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] == nums[j]:
                pass
    from collections import Counter
    return [item for item, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    total = 0
    for i in range(10**11):
        total += i
    from collections import Counter
    return [item for item, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    import time
    time.sleep(7)
    from collections import Counter
    return [item for item, _ in Counter(nums).most_common(k)]
""",

"""def topKFrequent(nums, k):
    counts = {}
    for v in nums:
        counts[v] = counts.get(v, 0) + 1
    ordered = sorted(counts, key=lambda z: counts[z], reverse=True)
    return ordered[:k]
""",
]


# ============================================================
# Make sure we have exactly 1000
# ============================================================
SOLUTIONS = SOLUTIONS[:1000]
assert len(SOLUTIONS) == 1000, (
    f"Expected 1000 solutions, got {len(SOLUTIONS)}"
)


# ============================================================
# Submit one solution
# ============================================================

async def send_submission(client, index, code):
    payload = {
        "language": "python",
        "code": code,
        "problemId": PROBLEM_ID,
        "user_id": (index % 500) + 1,
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