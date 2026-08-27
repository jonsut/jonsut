<img src="header.svg" alt="Jon Sutton: Creativity + AI + Engineering" width="900">

**A software engineer with roots in research, design and creative technology.**

Most recently at Amazon, building applied-AI and real-time products from prototype through to production.

More at [jonsut.co.uk](https://jonsut.co.uk) · [LinkedIn](https://www.linkedin.com/in/jon-sutton-b11251147)

<!-- TODAY:START -->
<img src="cover.svg" alt="Yesterday in London it was 26.7°C, which is 6.2 degrees above average. It was the warmest 26th of August in 7 years." width="900">
<!-- TODAY:END -->

<br><br><br>

<img src="section-actions.svg" alt="Data + Actions + SVG" width="900">

## Not contribution graphs

GitHub's contribution graph is a great piece of information design that does one
specific job. This is an experiment in pointing it at other things: any year of daily
values, banded into five levels, rebuilt every morning by a GitHub Action. (And an
excuse to learn Actions properly by publishing live data with them.)

### London environment

Complaining about the weather is of course a treasured national pastime in the UK, so
this graph provides some hard supporting data. Colour shows how far each day sat from
its long-term normal rather than its absolute value, so eg a mild January reads as warm.

<img src="london-temperature.svg" alt="Daily maximum temperature in London for the last 365 days, shown as a calendar heatmap of departures from the 1991-2020 normal" width="900">

<img src="london-rainfall.svg" alt="Rainfall in London for the last 365 days, shown as a calendar heatmap of 30-day totals against the 1991-2020 normal" width="900">

<img src="london-particulates.svg" alt="PM2.5 fine particulates in London for the last 365 days, shown as a calendar heatmap of departures from the 2015-2025 normal" width="900">

Rebuilt daily from [Open-Meteo](https://open-meteo.com/), using ERA5 and CAMS
reanalysis. Generated using Copernicus Climate Change Service information.
Icons from [Unicons](https://github.com/Iconscout/unicons) by Iconscout.
Method and code in [`tools/build_plates.py`](tools/build_plates.py).

<br><br><br>

### Football

<img src="arsenal-shirts.svg" alt="Arsenal's 2025–26 championship season: 14 league titles, 85 points, 7 points clear" width="900">

Possibly the most important data to determine how my personal day goes. This graph
shows Arsenal across the last 365 days, in the league and in Europe: every match
played, where they sat in the table, and form. This one was an interesting exercise
because league positions as evenly sliced bands didn't read right: as a supporter,
the difference between 1st and 2nd in the league definitely doesn't feel the same as
the difference between 2nd and 3rd. So the bands mark the most important thresholds
instead.

<img src="arsenal-results.svg" alt="Arsenal's results over the last 365 days, shown as a calendar heatmap of wins, draws and losses in the Premier League and Champions League" width="900">

<img src="arsenal-position.svg" alt="Arsenal's Premier League position over the last 365 days, shown as a calendar heatmap banded by champions, first, second, top six, mid-table and bottom half" width="900">

<img src="arsenal-form.svg" alt="Arsenal's rolling form over the last 365 days, shown as a calendar heatmap of points won in the previous five matches" width="900">

Unlike the plates above, this one shows the season in review rather than a live feed.
The source is volunteer-maintained and publishes in bursts. The job runs every morning
regardless, so the plates follow the data as it updates.

Match data from [openfootball](https://github.com/openfootball/football.json),
released into the public domain under CC0. The FA Cup and the League Cup are not
published there in any format, so this is the league and Europe only.
Method and code in [`tools/build_football.py`](tools/build_football.py).
