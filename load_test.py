import asyncio
import time
import httpx # install with: pip install httpx

API_URL = "http://localhost:3000/api/submit"
TOTAL_SUBMISSIONS = 50

# Payload to submit
payload = {
    "language": "python",
    "code": "import time\nprint('Testing worker load!')\ntime.sleep(0.5)"
}

async def send_submission(client, index):
    try:
        response = await client.post(API_URL, json=payload, timeout=10.0)
        data = response.json()
        print(f"[Job {index+1:02d}] Queued successfully -> Submission ID: {data.get('submissionId')}")
        return True
    except Exception as e:
        print(f"[Job {index+1:02d}] Failed to queue: {e}")
        return False

async def main():
    print(f"🚀 Starting load test: Sending {TOTAL_SUBMISSIONS} requests to {API_URL}...\n")
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [send_submission(client, i) for i in range(TOTAL_SUBMISSIONS)]
        results = await asyncio.gather(*tasks)

    total_time = round(time.time() - start_time, 2)
    successful = results.count(True)
    failed = results.count(False)

    print("\n" + "="*40)
    print("📊 API QUEUING METRICS")
    print("="*40)
    print(f"Total Sent      : {TOTAL_SUBMISSIONS}")
    print(f"Successfully Queued: {successful}")
    print(f"Failed          : {failed}")
    print(f"Time Taken to Queue: {total_time}s")
    print(f"API Throughput  : {round(TOTAL_SUBMISSIONS / total_time, 2)} req/sec")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())