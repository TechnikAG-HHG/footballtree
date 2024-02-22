phrase_count = {}

while True:
    user_input = input("Enter a phrase (type 'final' to finish): ")

    if user_input.lower() == 'final':
        break

    if user_input in phrase_count:
        phrase_count[user_input] += 1
    else:
        phrase_count[user_input] = 1

for phrase, count in phrase_count.items():
    print(f'You wrote "{phrase}" {count} times.')
