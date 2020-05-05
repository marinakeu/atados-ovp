def result_contains(results, key, value):
    found = False
    for result in results:
        if result[key] == value:
            found = True
            break
    return found
