---
title: transcripts
description: Search, read, and inspect earnings-call transcripts.
---

# finance transcripts

The `transcripts.*` commands search, read, and inspect earnings-call transcripts. Use this namespace when the user asks about management commentary, prepared remarks, or Q&A from a specific quarter.

All examples use `--output json` so results are stable to parse in terminals, scripts, and automation workflows.

## finance transcripts.qa

Extract analyst Q&A pairs from a transcript.

### What it does

`finance transcripts.qa` extracts analyst Q&A pairs from a transcript. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `transcript`, `qa_pairs`, `count`, `source`.

### When to use it

Use this command when you need transcript Q&A pairs and speaker attribution rather than the full prepared remarks.

### Usage

```bash
finance transcripts.qa [SYMBOL] [url=URL] [quarter=latest limit=10] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | No | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `url` | No | None | URL | Document URL to fetch and read. |
| `limit` | No | `10` | Integer | Maximum number of records returned. |
| `quarter` | No | `latest` | String | Quarter selector such as `latest`, `Q4 2026`, or another provider-supported quarter label. |

### Basic usage

```bash
finance transcripts.qa IOT quarter=latest limit=5 --output json
```

### Example output

This output was generated with `finance transcripts.qa IOT quarter=latest limit=5 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "transcript": {
      "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
      "quarter": "Q4 2026",
      "published_at": "2026-03-05T23:27:39+00:00",
      "url": "https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/"
    },
    "qa_pairs": [
      {
        "questioner": "Matthew George Hedberg",
        "question": "Hey, guys. Can you hear me? Great. Thanks again, and great job this quarter. You know, a lot of positives to pick through here. The emerging product success was certainly a stand reaching two really significant milestones. I guess, as you look to the future and, by the way, I think you guys outlined a really, really compelling reason why data is at the core of Samsara Inc. and why that is extremely defensive and, in fact, offensive in an AI environment. Can you talk about, though, where you are seeing some of the best adoption rates for some of these emerging products? Is it across all your customers? Is it some of your larger particular verticals? Any sense for just how those emerging products are distributed?",
        "answers": [
          {
            "speaker": "Sanjit Biswas",
            "text": "Hey, Matt. This is Sanjit. I will take that one. I would say we are seeing very strong momentum, especially with large customers because they have the most complex physical operations—thousands, often tens of thousands, of frontline workers and a similar, probably larger number of assets. So when we introduce new technologies like commercial navigation, maintenance, training, they are very well received because they know immediately how to put that technology to work. So I would say if I had to choose a pattern, it would be among these larger customers where they are set up to absorb these new products."
          }
        ]
      },
      {
        "questioner": "Keith Weiss",
        "question": "Excellent. Thank you guys for taking the question, and congratulations on a really outstanding quarter and year. Two—well, really, two questions I want to ask. One more tactical, one more strategic. On the more tactical side of the equation, the acceleration that we have seen over the past couple of quarters in net new ARR—is it too simple to say that this is sort of asset tags and that new solution ramping up within the product portfolio, or is there a broader set of drivers that are behind that acceleration? And then on the more strategic side, coming out of the Morgan Stanley TMT conference, we have been talking a lot about proprietary data. One of the debates that emerged is how the value of data sustains over time, and I would love to hear your view on it in terms of the relative value of the data when it is brand new and it is just coming off of the devices versus how much value it retains as it becomes older and older and becomes part of that bigger dataset that you have over time. Thank you so much.",
        "answers": [
          {
            "speaker": "Dominic Phillips",
            "text": "Hey, Keith. This is Dominic. I will go for the first one, then Sanjit can take the second one. I think the acceleration—the net new ARR acceleration over the last three quarters—has been much broader than something simply as asset tags. Broadly, as a bucket, the emerging products have definitely been big contributors, going from 8% of the net new ACV mix in Q2 to 20% in Q3, and then 23% in Q4. Asset tags have been important within that, but once again, we did not see one product within the emerging products driving more than 50% of that contribution. I think it has been a lot of large customer momentum and success—again, a quarterly record 131 $1 million+ net new ACV transactions; our second-highest quarter ever of $100K+ adds. We are seeing good momentum internationally and then in specific verticals—construction and wholesale and retail and public sector this quarter were all strong. So emerging products are definitely playing a role, but the strength and the growth have been much more broad than that."
          },
          {
            "speaker": "Sanjit Biswas",
            "text": "And, Keith, on the proprietary data angle, we think there is a lot of value in the accumulation and really the data asset that builds up over time. I will give you one or two concrete examples. Maintenance is actually one that our customers have really started taking to. We have a tremendous amount of information about what happens with the specific make, model, year of a truck. So, for example, if you have a 2020 Freightliner Cascadia, how does it wear over time? What have others seen? Where does it start to break down? Where do maintenance costs go up? That is from the accumulation of a lot of data over time. The same philosophy applies to things like risk data. You want to understand how millions of drivers over different weather conditions over time, different tenures at their company, and different risk patterns behave. So it is not just the in-the-moment data—that is, of course, valuable—but it is really being able to look at it over time and across customers. That is where it accumulates to be something really interesting."
          }
        ]
      },
      {
        "questioner": "Aleksandr J. Zukin",
        "question": "Yeah, guys. Thank you for taking the question. I echo my congratulations on a really, really strong quarter. Maybe first one for you, Sanjit. Just the AI offering that you launched—the agentic offering—maybe help us understand a little bit of how you plan to monetize that within your customer base. I think you listed a few that are on the horizon. Maybe talk to us a little bit about your vision for introducing that type of functionality and how the pricing evolves around that. And then, Dom, it is your largest net new ARR beat as a public company despite the conservatism you always embed in the guidance. We are starting with a two percentage point expansion on a larger scale, implying the largest starting incremental margin guidance for a fiscal year guide. So maybe walk through the momentum that you are seeing in existing and new customers that gives you that confidence to embed that sales efficiency to start the guidance.",
        "answers": [
          {
            "speaker": "Sanjit Biswas",
            "text": "Sure. I will start with the agentic question. AI agents are a new concept to the world and very new in the world of our customers. We are getting these products out there to understand better how they are going to use the agents—how often they are used, the patterns, and so on. That will give us the data we need to figure out the right pricing model that both is a fair share of value, but also matches how the customers use the product. We will have more to come there. We will really get these out there starting in the summer with Beyond, and we are excited not just about the safety agent, but also the maintenance, compliance, and the other virtual team members we can add to our teams."
          },
          {
            "speaker": "Dominic Phillips",
            "text": "Yeah. I would say that we have—again, Q4 was fantastic—but we have really had three consecutive quarters now of accelerating net new ARR growth. A lot of momentum, obviously, to end FY 2026 and then taking us into FY 2027. I think not only have we demonstrated a lot of accelerating growth, but we have also done so by getting more efficient, again, across the board. We are finding ways to operate more efficiently. We are using a lot of AI tools internally to drive a lot more productivity. Even looking at something as simple as ARR per employee, that has increased every year over the last several years. I think it is up more than 30% over the last three years. We are able to drive a lot more top-line scale while doing so much more efficiently, and that gives us confidence that we can continue that into FY 2027. Great. Thank you."
          }
        ]
      },
      {
        "questioner": "Michael James Turrin",
        "question": "Hey. Thanks very much. I echo my congrats as well. The Q4 results are really impressive, even for Samsara Inc. in a Q4. So the first question is, you had a lot of rich detail in there, but help us with where the sources of upside came from and if anything at all surprised you relative to what you were expecting. As a second part to that, how that shades what you are framing to us for fiscal 2027 as well, Dom.",
        "answers": [
          {
            "speaker": "Dominic Phillips",
            "text": "Yeah. Again, as we just talked with Alex, third consecutive quarter of net new ARR acceleration; strongest net new ARR growth in eight quarters; and so much net new ARR acceleration that the overall $1.9 billion of ending ARR accelerated back up to 30%. Again, large customers, a lot of large deals—the record 131 $1 million+ transactions—and then the 204 $100K+ adds was very strong. Tied into the emerging products, we are just seeing much larger multiproduct transactions. Nine of the top 10 deals had two-plus products, eight of the top ten three-plus, and six of the top ten four-plus. So a lot of multiproduct strength driving the growth. We are getting contribution from these emerging frontiers, whether it is the emerging products at 23%, international, or some of these verticals. So three consecutive quarters of acceleration and a lot of growth strength, and that gives us a lot of good momentum going into 2027."
          }
        ]
      },
      {
        "questioner": "Matt Martino",
        "question": "Yeah. Thanks for taking the questions, guys. Sanjit, for you, asset tags clearly feel like something much bigger. As you introduce the XS form factor and bring in Hubble to extend the network, how should we think about the strategic end state there? Is this mainly about driving deeper within the base, or does this really start to open up an entirely broader asset visibility platform for you guys?",
        "answers": [
          {
            "speaker": "Sanjit Biswas",
            "text": "Yeah, Matt. I would say it is definitely both. The world of physical operations has a ton of assets. There are, of course, vehicles and trailers and construction equipment, but I mentioned a lot of the smaller handheld assets—tools, dollies, and so on. Really, our first priority here is, like I said with phase one, we are just simply trying to digitize and get this information into the cloud so we can start operating on it. As we do that, I think it does open up a lot of interesting use cases. Many of our customers are interested in things like asset dormancy—Which pieces of equipment have not moved? Maybe they do not need to own them and they could rent them instead. There are definitely sophisticated ways to load balance where those assets are placed. I do think there is this agentic opportunity. All of that will appeal to our existing customers, and I do think this will open up some new possibilities—maybe some customers that do not have a tremendous number of vehicles but have a lot of other kinds of field assets. We highlighted Total Safety, for example. They have about 250,000 assets. That would be a good example of one."
          }
        ]
      }
    ],
    "count": 5,
    "source": "motley_fool"
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.qa_pairs` | array | Question-and-answer pairs extracted from the transcript. |
| `data.qa_pairs[]` | object | Question-and-answer pairs extracted from the transcript. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.transcript` | object | Transcript metadata. |
| `data.qa_pairs[].answers` | array | Management answer turns. |
| `data.qa_pairs[].answers[]` | object | Management answer turns. |
| `data.qa_pairs[].question` | string | Analyst question text. |
| `data.qa_pairs[].questioner` | string | Questioner name when available. |
| `data.transcript.published_at` | string | Publication timestamp returned by the provider. |
| `data.transcript.quarter` | string | Fiscal quarter label. |
| `data.transcript.title` | string | Transcript title returned by the provider. |
| `data.transcript.url` | string | Source URL. |
| `data.qa_pairs[].answers[].speaker` | string | Speaker name. |
| `data.qa_pairs[].answers[].text` | string | Extracted text or raw text cell. |

## finance transcripts.read

Read a transcript and split prepared remarks / Q&A.

### What it does

`finance transcripts.read` reads a transcript and split prepared remarks / Q&A. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `transcript`, `date`, `summary`, `text`, `char_count`, `returned_chars`, `truncated`, `prepared_speakers`.

### When to use it

Use this command when you need the prepared remarks, transcript summary, speaker list, and Q&A count for one quarter or URL.

### Usage

```bash
finance transcripts.read [SYMBOL] [url=URL] [quarter=latest max_chars=12000 include_turns=false] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | No | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `url` | No | None | URL | Document URL to fetch and read. |
| `include_turns` | No | `false` | `true`, `false` | Include transcript speaker turns. |
| `max_chars` | No | `12000` | Integer | Maximum text characters returned. |
| `quarter` | No | `latest` | String | Quarter selector such as `latest`, `Q4 2026`, or another provider-supported quarter label. |

### Basic usage

```bash
finance transcripts.read IOT quarter=latest max_chars=1000 --output json
```

### Example output

This output was generated with `finance transcripts.read IOT quarter=latest max_chars=1000 --output json`.

```json
{
  "ok": true,
  "data": {
    "transcript": {
      "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
      "quarter": "Q4 2026",
      "published_at": "2026-03-05T23:27:39+00:00",
      "url": "https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/"
    },
    "date": "Thursday, March 5, 2026 at 5 p.m. ET",
    "summary": "Samsara ( IOT +1.71% ) accelerated top-line and large customer growth while further expanding margins and achieving GAAP profitability. Management emphasized the accelerating contribution of emerging products, with asset tags and multi-product deals fueling record large-customer transactions and broader platform adoption. International expansion, especially in Europe, displayed sustained momentum through landmark deals and targeted investments.",
    "text": "Sanjit Biswas: Thanks, Mike, and thank you everyone for joining us today. FY 2026 was an outstanding year of durable and efficient growth. We ended the year with $1.9 billion in ARR, growing 30% year over year. Our $432 million of net new ARR drove this performance, growing 21% year over year and demonstrating our ability to accelerate growth even as we operate at much larger scale. Our momentum is strongest with our largest customers. We ended the year with $1.2 billion of ARR from our $100K+ ARR customers, an increase of 37% year over year, our second consecutive quarter of sequential acceleration.\n\nAs we look back on FY 2026, it is clear we are uniquely positioned to help digitize the world of physical operations. We help these industries transform through a combination of hardware devices, cloud connectivity, deep AI, and data integrations. At the heart of our competitive advantage is our proprietary data asset, information that is not simply found on the Internet. This includes ev",
    "char_count": 52879,
    "returned_chars": 1000,
    "truncated": true,
    "prepared_speakers": [
      "Dominic Phillips",
      "Sanjit Biswas"
    ],
    "prepared_turn_count": 2,
    "qa_pair_count": 19,
    "source": "motley_fool",
    "symbol": "IOT"
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.char_count` | integer | Total extracted character count before truncation. |
| `data.date` | string | Transcript event date string as published by the provider. |
| `data.prepared_speakers` | array | Speakers found in prepared remarks. |
| `data.prepared_speakers[]` | string | Speakers found in prepared remarks. |
| `data.prepared_turn_count` | integer | Number of prepared-remarks turns. |
| `data.qa_pair_count` | integer | Number of Q&A pairs. |
| `data.returned_chars` | integer | Characters included in this response. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.summary` | string | Short human-readable summary. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.text` | string | Extracted document text after truncation. |
| `data.transcript` | object | Transcript metadata. |
| `data.truncated` | boolean | Whether the command truncated the result. |
| `data.transcript.published_at` | string | Publication timestamp returned by the provider. |
| `data.transcript.quarter` | string | Fiscal quarter label. |
| `data.transcript.title` | string | Transcript title returned by the provider. |
| `data.transcript.url` | string | Source URL. |

## finance transcripts.search

Search public earnings-call transcripts.

### What it does

`finance transcripts.search` searches public earnings-call transcripts. It returns `ok`, `data`, `error`, and `warnings` in JSON output. The result payload includes `symbol`, `transcripts`, `count`, `source`.

### When to use it

Use this command when you need to discover available public transcript URLs before reading or extracting Q&A.

Results come from public Motley Fool transcript pages when available.

### Usage

```bash
finance transcripts.search SYMBOL [limit=4 debug=false] [--output json]
```

### Arguments

| Argument | Required | Default | Accepted values | Description |
| --- | --- | --- | --- | --- |
| `symbol` | Yes | None | String | Ticker symbol to query, such as `AAPL` or `NVDA`. |
| `debug` | No | `false` | `true`, `false` | Include debug details. |
| `limit` | No | `4` | Integer | Maximum number of records returned. |

### Basic usage

```bash
finance transcripts.search IOT limit=4 --output json
```

### Example output

This output was generated with `finance transcripts.search IOT limit=4 --output json`.

```json
{
  "ok": true,
  "data": {
    "symbol": "IOT",
    "transcripts": [
      {
        "symbol": "IOT",
        "title": "Samsara (IOT) Q4 2026 Earnings Call Transcript",
        "quarter": "Q4 2026",
        "published_at": "2026-03-05T23:27:39+00:00",
        "url": "https://www.fool.com/earnings/call-transcripts/2026/03/05/samsara-iot-q4-2026-earnings-call-transcript/",
        "source": "motley_fool"
      },
      {
        "symbol": "IOT",
        "title": "Samsara (IOT) Q3 2026 Earnings Call Transcript",
        "quarter": "Q3 2026",
        "published_at": "2025-12-05T15:06:48+00:00",
        "url": "https://www.fool.com/earnings/call-transcripts/2025/12/05/samsara-iot-q3-2026-earnings-call-transcript/",
        "source": "motley_fool"
      }
    ],
    "count": 2,
    "source": "motley_fool"
  },
  "error": null,
  "warnings": []
}
```

### Output fields

| Field | Type | Description |
| --- | --- | --- |
| `ok` | boolean | Whether the command completed successfully. |
| `data` | object or null | Command-specific result payload. It is `null` when `ok` is `false`. |
| `error` | string or null | Human-readable error message when `ok` is `false`; otherwise `null`. |
| `warnings` | array | Non-fatal warnings returned by the command. |
| `data.count` | integer | Number of records included in the adjacent result array. |
| `data.source` | string | Provider or source identifier for the returned data. |
| `data.symbol` | string | Ticker symbol used by the command. |
| `data.transcripts` | array | Transcript search results. |
| `data.transcripts[]` | object | Transcript search results. |
| `data.transcripts[].published_at` | string | Publication timestamp returned by the provider. |
| `data.transcripts[].quarter` | string | Fiscal quarter label. |
| `data.transcripts[].source` | string | Provider or source identifier for the returned data. |
| `data.transcripts[].symbol` | string | Ticker symbol associated with the transcript result. |
| `data.transcripts[].title` | string | Transcript title returned by the provider. |
| `data.transcripts[].url` | string | Source URL. |
