from tools.probe.getMicQueue import get_mic_queue
import time

if __name__ == '__main__':
    all_results = []
    for i in range(5):
        q = get_mic_queue("A Welcome Soap Box")
        print(f"Attempt {i+1}: {q}")
        all_results.extend(q)
        time.sleep(1)
    # dedupe
    uniq = []
    for n in all_results:
        if n not in uniq:
            uniq.append(n)
    print('\nAggregated:', uniq)
