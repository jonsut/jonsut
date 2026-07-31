<img src="header.svg" alt="Jon Sutton, software engineer with roots in research, design and creative technology" width="900">

Most recently at Amazon, building applied-AI and real-time products from prototype through to production.

Recent work:

- Real-time AI translation serving 3M+ translations across 30+ languages, including 17 with no coverage from traditional translation providers
- A triple-validation framework for measuring AI quality rather than trusting it: human evaluation, BLEU scoring and multi-model adversarial testing, with a 96% error detection rate
- Live multi-device experiences spanning browser audio capture, streaming transcription and synchronised interfaces
- Named inventor on a granted US patent

Currently exploring practical AI evaluation, agent workflows, and expressive interfaces that remain reliable in production.

More at [jonsut.co.uk](https://jonsut.co.uk) · [LinkedIn](https://www.linkedin.com/in/jon-sutton-b11251147)

<br><br><br>

## Contribution graphs for things that aren't contributions

GitHub's contribution graph is a decent piece of information design doing exactly one
job. This is an experiment in pointing it at other things: any year of daily values,
banded into five levels, rebuilt every morning by a GitHub Action. Half curiosity
about what the form can carry, half an excuse to learn Actions properly by publishing
live data with them.

### London environment

The British talk about the weather constantly, and in fairness it has been unusually
worth talking about. Colour here shows how far each day sat from its long-term normal
rather than its absolute value, so a mild January reads as warm and a cool August
reads as cold.

<!-- TODAY:START -->
Yesterday in London: 27.7°C, 3.3mm of rain, PM2.5 at 5 µg/m³.
<!-- TODAY:END -->

<img src="london-temperature.svg" alt="Daily maximum temperature in London for the last 365 days, shown as a calendar heatmap of departures from the 1991-2020 normal" width="900">

<img src="london-rainfall.svg" alt="Rainfall in London for the last 365 days, shown as a calendar heatmap of 30-day totals against the 1991-2020 normal" width="900">

<img src="london-particulates.svg" alt="PM2.5 fine particulates in London for the last 365 days, shown as a calendar heatmap of departures from the 2015-2025 normal" width="900">

Rebuilt daily from [Open-Meteo](https://open-meteo.com/), using ERA5 and CAMS
reanalysis. Generated using Copernicus Climate Change Service information.
Method and code in [`tools/build_plates.py`](tools/build_plates.py).
