from googlesearch import search
import os
err = 'command errored out with exit code 2359302'

print('\n\n')

results = search(query=err, stop=3)
results = [f'\n\t[{index + 1}] <=> {r}' for index, r in enumerate(results)]

results = ''.join(results)

if '.google-cookie' in os.listdir('.'):
    os.remove('.google-cookie')

print(f'These auto-generated links may help:{results}')