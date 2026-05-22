"""Accumulate GitHub repo view counts into views.json across the rolling 14-day window.

Mirrors MShawon's clones script (https://github.com/MShawon/github-clone-count-badge)
but operates on the /traffic/views API shape, which uses the 'views' key instead of 'clones'.
"""
import json

with open('views.json', 'r') as fh:
    now = json.load(fh)

with open('views_before.json', 'r') as fh:
    before = json.load(fh)
timestamps = {before['views'][i]['timestamp']: i for i in range(len(before['views']))}

latest = dict(before)
for i in range(len(now['views'])):
    timestamp = now['views'][i]['timestamp']
    if timestamp in timestamps:
        latest['views'][timestamps[timestamp]] = now['views'][i]
    else:
        latest['views'].append(now['views'][i])


latest['count'] = sum(map(lambda x: int(x['count']), latest['views']))
latest['uniques'] = sum(map(lambda x: int(x['uniques']), latest['views']))

if len(timestamps) > 100:
    remove_this = []
    views = latest['views']
    for i in range(len(timestamps) - 35):
        views[i]['timestamp'] = views[i]['timestamp'][:7]
        if views[i]['timestamp'] == views[i + 1]['timestamp'][:7]:
            views[i + 1]['count'] += views[i]['count']
            views[i + 1]['uniques'] += views[i]['uniques']
            remove_this.append(views[i])

    for item in remove_this:
        views.remove(item)

with open('views.json', 'w', encoding='utf-8') as fh:
    json.dump(latest, fh, ensure_ascii=False, indent=4)
